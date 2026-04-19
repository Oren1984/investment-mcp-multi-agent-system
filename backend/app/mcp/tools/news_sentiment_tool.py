from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.mcp.base_tool import MCPBaseTool
from app.services.news_service import NewsService
from app.services.market_data_service import MarketDataService


class NewsSentimentInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    days: int = Field(7, description="Number of days to look back for news", ge=1, le=30)


class NewsSentimentTool(MCPBaseTool):
    name = "get_news_sentiment"
    description = "Fetch recent news headlines and calculate sentiment score for a ticker."
    input_schema = NewsSentimentInput

    def __init__(self, news: NewsService, market_data: MarketDataService):
        self._news = news
        self._market_data = market_data

    def run(self, inputs: NewsSentimentInput) -> dict[str, Any]:
        info = self._market_data.get_company_info(inputs.ticker)
        company_name = info.get("company_name", inputs.ticker)
        return self._news.get_news_sentiment(inputs.ticker, company_name, inputs.days)
