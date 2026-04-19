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
