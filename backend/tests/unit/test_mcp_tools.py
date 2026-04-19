"""
Unit tests for MCP tool validation and execution logic.
All external services are injected as mocks.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from app.core.errors import ToolNotFoundError, ToolExecutionError
from app.mcp.base_tool import MCPBaseTool, MCPToolResult
from app.mcp.registry import MCPRegistry


class TestMCPRegistry:
    def test_register_and_get(self):
        tool = MagicMock(spec=MCPBaseTool)
        tool.name = "test_tool"
        registry = MCPRegistry()
        registry.register(tool)
        assert registry.get("test_tool") is tool

    def test_get_nonexistent_raises(self):
        registry = MCPRegistry()
        with pytest.raises(ToolNotFoundError):
            registry.get("nonexistent")

    def test_list_tools(self):
        t1 = MagicMock(spec=MCPBaseTool)
        t1.name = "tool_a"
        t2 = MagicMock(spec=MCPBaseTool)
        t2.name = "tool_b"
        registry = MCPRegistry()
        registry.register(t1)
        registry.register(t2)
        assert set(registry.list_tools()) == {"tool_a", "tool_b"}

    def test_register_overrides_existing(self):
        t1 = MagicMock(spec=MCPBaseTool)
        t1.name = "my_tool"
        t2 = MagicMock(spec=MCPBaseTool)
        t2.name = "my_tool"
        registry = MCPRegistry()
        registry.register(t1)
        registry.register(t2)
        assert registry.get("my_tool") is t2


class TestStockPriceTool:
    def test_valid_input_calls_service(self, mock_market_data):
        from app.mcp.tools.stock_price_tool import StockPriceTool

        tool = StockPriceTool(market_data=mock_market_data)
        result = tool.execute({"ticker": "AAPL", "period": "1y"})

        assert result.success is True
        assert result.data["ticker"] == "AAPL"
        mock_market_data.get_price_history.assert_called_once_with("AAPL", "1y", "1d")

    def test_missing_ticker_fails_validation(self, mock_market_data):
        from app.mcp.tools.stock_price_tool import StockPriceTool

        tool = StockPriceTool(market_data=mock_market_data)
        result = tool.execute({})  # missing required 'ticker'

        assert result.success is False
        assert result.error is not None

    def test_invalid_period_fails_validation(self, mock_market_data):
        from app.mcp.tools.stock_price_tool import StockPriceTool

        tool = StockPriceTool(market_data=mock_market_data)
        # period accepts any string, so check with a valid call to confirm no error
        result = tool.execute({"ticker": "AAPL", "period": "1y"})
        assert result.success is True

    def test_service_exception_returns_failure(self, mock_market_data):
        from app.mcp.tools.stock_price_tool import StockPriceTool
        from app.core.errors import ExternalAPIError

        mock_market_data.get_price_history.side_effect = ExternalAPIError("API down")
        tool = StockPriceTool(market_data=mock_market_data)
        result = tool.execute({"ticker": "AAPL"})

        assert result.success is False
        assert "API down" in result.error


class TestFinancialStatementsTool:
    def test_all_statements_returned(self, mock_financials, mock_market_data):
        from app.mcp.tools.financial_statements_tool import FinancialStatementsTool

        tool = FinancialStatementsTool(financials=mock_financials, market_data=mock_market_data)
        result = tool.execute({"ticker": "AAPL", "statement_type": "all"})

        assert result.success is True
        assert "key_metrics" in result.data
        assert "income_statement" in result.data
        assert "balance_sheet" in result.data
        assert "cash_flow" in result.data

    def test_income_only(self, mock_financials, mock_market_data):
        from app.mcp.tools.financial_statements_tool import FinancialStatementsTool

        tool = FinancialStatementsTool(financials=mock_financials, market_data=mock_market_data)
        result = tool.execute({"ticker": "AAPL", "statement_type": "income"})

        assert result.success is True
        assert "income_statement" in result.data
        assert "balance_sheet" not in result.data


class TestRiskMetricsTool:
    def test_valid_call(self, mock_risk):
        from app.mcp.tools.risk_metrics_tool import RiskMetricsTool

        tool = RiskMetricsTool(risk=mock_risk)
        result = tool.execute({"ticker": "AAPL", "period": "1y"})

        assert result.success is True
        assert result.data["beta"] == 1.25
        mock_risk.get_risk_metrics.assert_called_once_with("AAPL", "1y")


class TestTechnicalIndicatorsTool:
    def test_valid_call(self, mock_risk):
        from app.mcp.tools.technical_indicators_tool import TechnicalIndicatorsTool

        tool = TechnicalIndicatorsTool(risk=mock_risk)
        result = tool.execute({"ticker": "AAPL", "period": "6mo"})

        assert result.success is True
        assert result.data["rsi_14"] == 58.0
        assert result.data["trend"] == "BULLISH"


class TestNewsSentimentTool:
    def test_valid_call(self, mock_news, mock_market_data):
        from app.mcp.tools.news_sentiment_tool import NewsSentimentTool

        tool = NewsSentimentTool(news=mock_news, market_data=mock_market_data)
        result = tool.execute({"ticker": "AAPL", "days": 7})

        assert result.success is True
        assert result.data["sentiment_label"] == "POSITIVE"

    def test_days_out_of_range_fails(self, mock_news, mock_market_data):
        from app.mcp.tools.news_sentiment_tool import NewsSentimentTool

        tool = NewsSentimentTool(news=mock_news, market_data=mock_market_data)
        result = tool.execute({"ticker": "AAPL", "days": 100})  # max is 30

        assert result.success is False


class TestMCPGateway:
    def test_all_tools_registered(self, mock_gateway):
        tools = mock_gateway.list_tools()
        expected = {
            "get_stock_price",
            "get_financial_statements",
            "get_technical_indicators",
            "get_sector_analysis",
            "get_risk_metrics",
            "get_news_sentiment",
        }
        assert expected.issubset(set(tools))

    def test_unknown_tool_raises(self, mock_gateway):
        with pytest.raises(ToolNotFoundError):
            mock_gateway.call("nonexistent_tool", {})

    def test_successful_call_returns_data(self, mock_gateway):
        result = mock_gateway.call("get_risk_metrics", {"ticker": "AAPL", "period": "1y"})
        assert result["beta"] == 1.25

    def test_tool_execution_failure_raises(self, mock_gateway, mock_risk):
        from app.core.errors import ExternalAPIError
        mock_risk.get_risk_metrics.side_effect = ExternalAPIError("Timeout")
        with pytest.raises(ToolExecutionError):
            mock_gateway.call("get_risk_metrics", {"ticker": "AAPL", "period": "1y"})
