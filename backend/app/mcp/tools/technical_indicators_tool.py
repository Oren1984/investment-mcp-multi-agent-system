from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.mcp.base_tool import MCPBaseTool
from app.services.risk_service import RiskService


class TechnicalIndicatorsInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    period: str = Field("6mo", description="Price history period for indicator calculation")


class TechnicalIndicatorsTool(MCPBaseTool):
    name = "get_technical_indicators"
    description = "Calculate technical indicators: RSI, MACD, Bollinger Bands, SMA/EMA, trend signals."
    input_schema = TechnicalIndicatorsInput

    def __init__(self, risk: RiskService):
        self._risk = risk

    def run(self, inputs: TechnicalIndicatorsInput) -> dict[str, Any]:
        return self._risk.get_technical_indicators(inputs.ticker, inputs.period)
