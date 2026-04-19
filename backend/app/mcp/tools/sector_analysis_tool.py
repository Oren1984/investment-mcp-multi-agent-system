from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.mcp.base_tool import MCPBaseTool
from app.services.market_data_service import MarketDataService


class SectorAnalysisInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    sector_etf: str | None = Field(None, description="Optional specific sector ETF override (e.g. XLK)")


class SectorAnalysisTool(MCPBaseTool):
    name = "get_sector_analysis"
    description = "Compare stock performance vs its sector ETF and provide sector context."
    input_schema = SectorAnalysisInput

    def __init__(self, market_data: MarketDataService):
        self._market_data = market_data

    def run(self, inputs: SectorAnalysisInput) -> dict[str, Any]:
        comparison = self._market_data.get_sector_comparison(inputs.ticker, inputs.sector_etf)
        info = self._market_data.get_company_info(inputs.ticker)
        return {
            **comparison,
            "pe_ratio": info.get("pe_ratio"),
            "market_cap": info.get("market_cap"),
            "sector": info.get("sector", comparison.get("sector", "")),
        }
