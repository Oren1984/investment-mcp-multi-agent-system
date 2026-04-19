"""CrewAI-compatible tool wrappers that delegate to the MCP Gateway."""
from __future__ import annotations

import json
from typing import Any, Type

from crewai.tools.base_tool import BaseTool as CrewAIBaseTool
from pydantic import BaseModel, ConfigDict, Field

from app.mcp.gateway import MCPGateway


def _to_str(data: Any) -> str:
    if isinstance(data, str):
        return data
    return json.dumps(data, indent=2, default=str)


class StockPriceCrewTool(CrewAIBaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "get_stock_price"
    description: str = (
        "Fetch historical OHLCV price data, current price, and company information for a stock ticker. "
        "Input: ticker (str), period (str, e.g. '1y'), interval (str, e.g. '1d')"
    )
    gateway: MCPGateway

    def _run(self, ticker: str, period: str = "1y", interval: str = "1d") -> str:
        result = self.gateway.call("get_stock_price", {"ticker": ticker, "period": period, "interval": interval})
        return _to_str(result)


class FinancialStatementsCrewTool(CrewAIBaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "get_financial_statements"
    description: str = (
        "Retrieve financial statements and key metrics (P/E, margins, growth, debt ratios). "
        "Input: ticker (str), statement_type (str: 'all'|'income'|'balance'|'cashflow')"
    )
    gateway: MCPGateway

    def _run(self, ticker: str, statement_type: str = "all") -> str:
        result = self.gateway.call("get_financial_statements", {"ticker": ticker, "statement_type": statement_type})
        return _to_str(result)


class TechnicalIndicatorsCrewTool(CrewAIBaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "get_technical_indicators"
    description: str = (
        "Calculate RSI, MACD, Bollinger Bands, SMA/EMA, and trend signals for a ticker. "
        "Input: ticker (str), period (str, e.g. '6mo')"
    )
    gateway: MCPGateway

    def _run(self, ticker: str, period: str = "6mo") -> str:
        result = self.gateway.call("get_technical_indicators", {"ticker": ticker, "period": period})
        return _to_str(result)


class SectorAnalysisCrewTool(CrewAIBaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "get_sector_analysis"
    description: str = (
        "Compare stock performance vs its sector ETF, get sector context and relative positioning. "
        "Input: ticker (str), sector_etf (str, optional)"
    )
    gateway: MCPGateway

    def _run(self, ticker: str, sector_etf: str | None = None) -> str:
        payload: dict = {"ticker": ticker}
        if sector_etf:
            payload["sector_etf"] = sector_etf
        result = self.gateway.call("get_sector_analysis", payload)
        return _to_str(result)


class RiskMetricsCrewTool(CrewAIBaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "get_risk_metrics"
    description: str = (
        "Calculate investment risk metrics: beta, annualized volatility, VaR (95%), "
        "Sharpe ratio, and max drawdown. Input: ticker (str), period (str, e.g. '1y')"
    )
    gateway: MCPGateway

    def _run(self, ticker: str, period: str = "1y") -> str:
        result = self.gateway.call("get_risk_metrics", {"ticker": ticker, "period": period})
        return _to_str(result)


class NewsSentimentCrewTool(CrewAIBaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "get_news_sentiment"
    description: str = (
        "Fetch recent news headlines and sentiment score for a stock. "
        "Input: ticker (str), days (int, 1-30)"
    )
    gateway: MCPGateway

    def _run(self, ticker: str, days: int = 7) -> str:
        result = self.gateway.call("get_news_sentiment", {"ticker": ticker, "days": days})
        return _to_str(result)


class SaveReportCrewTool(CrewAIBaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "save_report"
    description: str = (
        "Persist the final investment report to the database. "
        "Input: run_id (str), ticker (str), content (str full report), structured (dict, optional)"
    )
    gateway: MCPGateway

    def _run(self, run_id: str, ticker: str, content: str, structured: dict | None = None) -> str:
        # SaveReportTool manages its own DB session independently
        from app.mcp.tools.save_report_tool import SaveReportTool as MCSaveReport
        from app.mcp.tools.save_report_tool import SaveReportInput

        tool = MCSaveReport()
        result = tool.execute({"run_id": run_id, "ticker": ticker, "content": content, "structured": structured or {}})
        return _to_str({"success": result.success, "data": result.data, "error": result.error})


def build_crewai_tools(gateway: MCPGateway) -> dict[str, CrewAIBaseTool]:
    return {
        "stock_price": StockPriceCrewTool(gateway=gateway),
        "financial_statements": FinancialStatementsCrewTool(gateway=gateway),
        "technical_indicators": TechnicalIndicatorsCrewTool(gateway=gateway),
        "sector_analysis": SectorAnalysisCrewTool(gateway=gateway),
        "risk_metrics": RiskMetricsCrewTool(gateway=gateway),
        "news_sentiment": NewsSentimentCrewTool(gateway=gateway),
        "save_report": SaveReportCrewTool(gateway=gateway),
    }
