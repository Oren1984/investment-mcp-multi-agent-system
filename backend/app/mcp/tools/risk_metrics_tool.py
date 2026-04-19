from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.mcp.base_tool import MCPBaseTool
from app.services.risk_service import RiskService


class RiskMetricsInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    period: str = Field("1y", description="Historical period for risk calculations")


class RiskMetricsTool(MCPBaseTool):
    name = "get_risk_metrics"
    description = "Calculate investment risk metrics: beta, volatility, VaR, Sharpe ratio, max drawdown."
    input_schema = RiskMetricsInput

    def __init__(self, risk: RiskService):
        self._risk = risk

    def run(self, inputs: RiskMetricsInput) -> dict[str, Any]:
        return self._risk.get_risk_metrics(inputs.ticker, inputs.period)
