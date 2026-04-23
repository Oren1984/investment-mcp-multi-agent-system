from __future__ import annotations

import threading
from typing import Any

from app.core.errors import ToolExecutionError, ToolNotFoundError
from app.core.logging import get_logger
from app.mcp.base_tool import MCPToolResult
from app.mcp.registry import MCPRegistry
from app.services import (
    FinancialsService,
    LLMService,
    MarketDataService,
    NewsService,
    ReportService,
    RiskService,
)

logger = get_logger(__name__)
_gateway_lock = threading.Lock()


class MCPGateway:
    def __init__(
        self,
        market_data: MarketDataService,
        financials: FinancialsService,
        risk: RiskService,
        news: NewsService,
        llm: LLMService,
    ):
        self._registry = MCPRegistry()
        self._setup_tools(market_data, financials, risk, news, llm)

    def _setup_tools(
        self,
        market_data: MarketDataService,
        financials: FinancialsService,
        risk: RiskService,
        news: NewsService,
        llm: LLMService,
    ) -> None:
        from app.mcp.tools.stock_price_tool import StockPriceTool
        from app.mcp.tools.financial_statements_tool import FinancialStatementsTool
        from app.mcp.tools.technical_indicators_tool import TechnicalIndicatorsTool
        from app.mcp.tools.sector_analysis_tool import SectorAnalysisTool
        from app.mcp.tools.risk_metrics_tool import RiskMetricsTool
        from app.mcp.tools.news_sentiment_tool import NewsSentimentTool

        self._registry.register(StockPriceTool(market_data=market_data))
        self._registry.register(FinancialStatementsTool(financials=financials, market_data=market_data))
        self._registry.register(TechnicalIndicatorsTool(risk=risk))
        self._registry.register(SectorAnalysisTool(market_data=market_data))
        self._registry.register(RiskMetricsTool(risk=risk))
        self._registry.register(NewsSentimentTool(news=news, market_data=market_data))

    def execute_rag_pass(self, ticker: str, period: str = "1y") -> dict[str, Any]:
        """Call all data tools and return aggregated raw data — no LLM involved."""
        import time

        # Tuple: (result_key, tool_name, payload)
        # result_key is the short name used by report builders (no "get_" prefix)
        tools_to_run = [
            ("stock_price", "get_stock_price", {"ticker": ticker, "period": period, "interval": "1d"}),
            ("financial_statements", "get_financial_statements", {"ticker": ticker, "statement_type": "all"}),
            ("technical_indicators", "get_technical_indicators", {"ticker": ticker, "period": "6mo"}),
            ("sector_analysis", "get_sector_analysis", {"ticker": ticker}),
            ("risk_metrics", "get_risk_metrics", {"ticker": ticker, "period": period}),
            ("news_sentiment", "get_news_sentiment", {"ticker": ticker, "days": 14}),
        ]

        results: dict[str, Any] = {}
        errors: dict[str, str] = {}

        for result_key, tool_name, payload in tools_to_run:
            t0 = time.perf_counter()
            try:
                data = self.call(tool_name, payload)
                data["_tool"] = result_key
                data["_latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
                results[result_key] = data
            except Exception as exc:
                errors[result_key] = str(exc)
                logger.warning("RAG pass tool failed", extra={"tool_name": tool_name, "error": str(exc)})

        return {
            "ticker": ticker,
            "period": period,
            "mode": "rag_only",
            "sources_used": list(results.keys()),
            "sources_failed": list(errors.keys()),
            "data": results,
            "errors": errors,
        }

    def call(self, tool_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        logger.info("MCP tool call", extra={"tool_name": tool_name})
        try:
            tool = self._registry.get(tool_name)
        except ToolNotFoundError:
            raise

        result: MCPToolResult = tool.execute(payload)
        if not result.success:
            raise ToolExecutionError(tool_name, result.error or "unknown error")
        return result.data or {}

    def list_tools(self) -> list[str]:
        return self._registry.list_tools()


_gateway_instance: MCPGateway | None = None


def create_gateway() -> MCPGateway:
    return MCPGateway(
        market_data=MarketDataService(),
        financials=FinancialsService(),
        risk=RiskService(),
        news=NewsService(),
        llm=LLMService(),
    )


def get_gateway() -> MCPGateway:
    global _gateway_instance
    if _gateway_instance is None:
        with _gateway_lock:
            if _gateway_instance is None:
                _gateway_instance = create_gateway()
    return _gateway_instance
