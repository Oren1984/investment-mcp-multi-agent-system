from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.mcp.base_tool import MCPBaseTool
from app.services.market_data_service import MarketDataService


class StockPriceInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g. AAPL)")
    period: str = Field("1y", description="Period: 1mo, 3mo, 6mo, 1y, 2y, 5y")
    interval: str = Field("1d", description="Data interval: 1d, 1wk, 1mo")


class StockPriceTool(MCPBaseTool):
    name = "get_stock_price"
    description = "Fetch historical OHLCV price data and current price for a stock ticker."
    input_schema = StockPriceInput

    def __init__(self, market_data: MarketDataService):
        self._market_data = market_data

    def run(self, inputs: StockPriceInput) -> dict[str, Any]:
        price_data = self._market_data.get_price_history(inputs.ticker, inputs.period, inputs.interval)
        info = self._market_data.get_company_info(inputs.ticker)
        return {**price_data, "company_info": info}
