"""Unit tests for MCPGateway.execute_rag_pass — aggregated RAG data collection."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.core.errors import ExternalAPIError, ToolExecutionError


class TestExecuteRagPass:
    def test_rag_pass_returns_correct_structure(self, mock_gateway):
        result = mock_gateway.execute_rag_pass("AAPL", "1y")

        assert result["ticker"] == "AAPL"
        assert result["period"] == "1y"
        assert result["mode"] == "rag_only"
        assert "data" in result
        assert "errors" in result
        assert "sources_used" in result
        assert "sources_failed" in result

    def test_rag_pass_sources_used_lists_successful_tools(self, mock_gateway):
        result = mock_gateway.execute_rag_pass("AAPL", "1y")
        sources_used = result["sources_used"]
        assert isinstance(sources_used, list)
        assert len(sources_used) > 0

    def test_rag_pass_data_contains_stock_price(self, mock_gateway):
        result = mock_gateway.execute_rag_pass("AAPL", "1y")
        assert "stock_price" in result["data"]

    def test_rag_pass_data_stock_price_has_ticker_field(self, mock_gateway):
        result = mock_gateway.execute_rag_pass("AAPL", "1y")
        stock_data = result["data"]["stock_price"]
        assert stock_data.get("ticker") == "AAPL"

    def test_rag_pass_total_tools_attempted(self, mock_gateway):
        result = mock_gateway.execute_rag_pass("AAPL", "1y")
        total = len(result["sources_used"]) + len(result["sources_failed"])
        # 6 tools are attempted: stock_price, financial_statements, technical_indicators,
        # sector_analysis, risk_metrics, news_sentiment
        assert total == 6

    def test_rag_pass_partial_failure_isolates_errors(self, mock_gateway, mock_risk):
        mock_risk.get_risk_metrics.side_effect = ExternalAPIError("Risk API down")
        result = mock_gateway.execute_rag_pass("AAPL", "1y")

        assert "risk_metrics" in result["sources_failed"]
        assert "risk_metrics" not in result["sources_used"]
        # Other tools should still succeed
        assert "stock_price" in result["sources_used"]

    def test_rag_pass_all_failures_returns_empty_data(self, mock_gateway, mock_market_data, mock_financials, mock_risk, mock_news):
        mock_market_data.get_price_history.side_effect = ExternalAPIError("Down")
        mock_market_data.get_company_info.side_effect = ExternalAPIError("Down")
        mock_market_data.get_sector_comparison.side_effect = ExternalAPIError("Down")
        mock_financials.get_key_metrics.side_effect = ExternalAPIError("Down")
        mock_financials.get_income_statement.side_effect = ExternalAPIError("Down")
        mock_financials.get_balance_sheet.side_effect = ExternalAPIError("Down")
        mock_financials.get_cash_flow.side_effect = ExternalAPIError("Down")
        mock_risk.get_technical_indicators.side_effect = ExternalAPIError("Down")
        mock_risk.get_risk_metrics.side_effect = ExternalAPIError("Down")
        mock_news.get_news_sentiment.side_effect = ExternalAPIError("Down")

        result = mock_gateway.execute_rag_pass("AAPL", "1y")

        assert len(result["sources_used"]) == 0
        assert len(result["sources_failed"]) == 6
        assert result["data"] == {}

    def test_rag_pass_data_includes_latency_field(self, mock_gateway):
        result = mock_gateway.execute_rag_pass("AAPL", "1y")
        for key, data in result["data"].items():
            assert "_latency_ms" in data, f"Tool '{key}' missing _latency_ms"

    def test_rag_pass_data_includes_tool_field(self, mock_gateway):
        result = mock_gateway.execute_rag_pass("AAPL", "1y")
        for key, data in result["data"].items():
            assert "_tool" in data, f"Tool '{key}' missing _tool"
            assert data["_tool"] == key


class TestBuildRagSnapshotReport:
    def _make_full_rag_result(self) -> dict:
        return {
            "ticker": "AAPL",
            "period": "1y",
            "mode": "rag_only",
            "sources_used": ["stock_price", "financial_statements", "technical_indicators",
                             "sector_analysis", "risk_metrics", "news_sentiment"],
            "sources_failed": [],
            "data": {
                "stock_price": {
                    "ticker": "AAPL",
                    "current_price": 175.0,
                    "price_change_pct": 12.5,
                    "data": {"2024-01-01": {"Close": 175.0}},
                },
                "financial_statements": {
                    "key_metrics": {"pe_ratio": 28.5, "gross_margins": 0.44},
                    "income_statement": {},
                },
                "technical_indicators": {
                    "rsi_14": 58.0,
                    "macd": 4.0,
                    "macd_signal": 3.5,
                    "sma_20": 172.0,
                    "sma_50": 168.0,
                    "trend": "BULLISH",
                    "rsi_signal": "NEUTRAL",
                },
                "sector_analysis": {
                    "sector": "Technology",
                    "sector_etf": "XLK",
                    "stock_1y_return_pct": 15.0,
                    "sector_1y_return_pct": 10.0,
                    "relative_performance_pct": 5.0,
                },
                "risk_metrics": {
                    "beta": 1.25,
                    "annualized_volatility_pct": 24.5,
                    "max_drawdown_pct": -18.3,
                    "sharpe_ratio": 0.85,
                    "var_95_1day_pct": -2.1,
                    "annualized_return_pct": 15.0,
                },
                "news_sentiment": {
                    "sentiment_score": 0.4,
                    "sentiment_label": "POSITIVE",
                    "article_count": 5,
                    "headlines": ["Apple beats earnings"],
                    "_source": "newsapi",
                },
            },
            "errors": {},
        }

    def test_report_contains_ticker_in_title(self):
        from app.crews.investment_crew import _build_rag_snapshot_report
        result = _build_rag_snapshot_report("AAPL", "1y", self._make_full_rag_result(), 2.5)
        assert "AAPL" in result

    def test_report_contains_price_section(self):
        from app.crews.investment_crew import _build_rag_snapshot_report
        result = _build_rag_snapshot_report("AAPL", "1y", self._make_full_rag_result(), 2.5)
        assert "Price Overview" in result
        assert "175.00" in result

    def test_report_contains_technical_section(self):
        from app.crews.investment_crew import _build_rag_snapshot_report
        result = _build_rag_snapshot_report("AAPL", "1y", self._make_full_rag_result(), 2.5)
        assert "Technical Indicators" in result
        assert "RSI" in result

    def test_report_contains_risk_section(self):
        from app.crews.investment_crew import _build_rag_snapshot_report
        result = _build_rag_snapshot_report("AAPL", "1y", self._make_full_rag_result(), 2.5)
        assert "Risk Metrics" in result
        assert "1.25" in result  # beta value

    def test_report_contains_sector_section(self):
        from app.crews.investment_crew import _build_rag_snapshot_report
        result = _build_rag_snapshot_report("AAPL", "1y", self._make_full_rag_result(), 2.5)
        assert "Sector Context" in result
        assert "Technology" in result

    def test_report_contains_news_sentiment(self):
        from app.crews.investment_crew import _build_rag_snapshot_report
        result = _build_rag_snapshot_report("AAPL", "1y", self._make_full_rag_result(), 2.5)
        assert "News Sentiment" in result
        assert "POSITIVE" in result

    def test_report_contains_data_provenance(self):
        from app.crews.investment_crew import _build_rag_snapshot_report
        result = _build_rag_snapshot_report("AAPL", "1y", self._make_full_rag_result(), 2.5)
        assert "Data Provenance" in result
        assert "Yahoo Finance" in result

    def test_report_shows_failed_sources_as_failed(self):
        from app.crews.investment_crew import _build_rag_snapshot_report
        rag_result = self._make_full_rag_result()
        rag_result["sources_used"].remove("risk_metrics")
        rag_result["sources_failed"].append("risk_metrics")
        rag_result["errors"]["risk_metrics"] = "API timeout"
        del rag_result["data"]["risk_metrics"]

        result = _build_rag_snapshot_report("AAPL", "1y", rag_result, 3.0)
        assert "FAILED" in result

    def test_report_contains_disclaimer(self):
        from app.crews.investment_crew import _build_rag_snapshot_report
        result = _build_rag_snapshot_report("AAPL", "1y", self._make_full_rag_result(), 2.5)
        assert "not financial advice" in result.lower()


class TestFormatRagContextSummary:
    def test_includes_ticker_header(self):
        from app.crews.investment_crew import _format_rag_context_summary
        rag_result = {
            "ticker": "AAPL",
            "period": "1y",
            "data": {
                "stock_price": {"current_price": 175.0, "price_change_pct": 12.5},
            },
            "sources_failed": [],
        }
        result = _format_rag_context_summary(rag_result)
        assert "AAPL" in result

    def test_includes_failed_tools_note(self):
        from app.crews.investment_crew import _format_rag_context_summary
        rag_result = {
            "ticker": "AAPL",
            "period": "1y",
            "data": {},
            "sources_failed": ["news_sentiment", "sector_analysis"],
        }
        result = _format_rag_context_summary(rag_result)
        assert "Failed tools" in result
        assert "news_sentiment" in result

    def test_empty_data_returns_minimal_string(self):
        from app.crews.investment_crew import _format_rag_context_summary
        rag_result = {"ticker": "XYZ", "period": "1y", "data": {}, "sources_failed": []}
        result = _format_rag_context_summary(rag_result)
        assert "XYZ" in result
        assert isinstance(result, str)
