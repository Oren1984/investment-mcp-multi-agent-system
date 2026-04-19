from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.errors import ExternalAPIError
from app.core.logging import get_logger

logger = get_logger(__name__)


class NewsService:
    BASE_URL = "https://newsapi.org/v2/everything"

    def get_news_sentiment(self, ticker: str, company_name: str, days: int = 7) -> dict:
        if not settings.news_api_key:
            return self._fallback_response(ticker)

        try:
            from datetime import datetime, timedelta, timezone

            from_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

            params = {
                "q": f"{company_name} OR {ticker}",
                "from": from_date,
                "sortBy": "relevancy",
                "language": "en",
                "pageSize": 10,
                "apiKey": settings.news_api_key,
            }

            with httpx.Client(timeout=10) as client:
                response = client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

            articles = data.get("articles", [])
            headlines = [a.get("title", "") for a in articles if a.get("title")]

            sentiment_score = self._simple_sentiment(headlines)

            return {
                "ticker": ticker,
                "company_name": company_name,
                "days_covered": days,
                "article_count": len(headlines),
                "headlines": headlines[:5],
                "sentiment_score": sentiment_score,
                "sentiment_label": "POSITIVE" if sentiment_score > 0.1 else "NEGATIVE" if sentiment_score < -0.1 else "NEUTRAL",
            }
        except ExternalAPIError:
            raise
        except Exception as e:
            logger.warning(f"news_service error for {ticker}: {e}")
            return self._fallback_response(ticker)

    def _simple_sentiment(self, headlines: list[str]) -> float:
        positive_words = {"gain", "rise", "beat", "surged", "record", "growth", "profit", "strong", "positive", "up", "high"}
        negative_words = {"loss", "fall", "miss", "drop", "decline", "weak", "negative", "down", "low", "cut", "risk", "concern"}

        if not headlines:
            return 0.0

        total = 0.0
        for h in headlines:
            words = set(h.lower().split())
            pos = len(words & positive_words)
            neg = len(words & negative_words)
            total += (pos - neg)

        return round(total / len(headlines), 2)

    def _fallback_response(self, ticker: str) -> dict:
        return {
            "ticker": ticker,
            "company_name": "",
            "days_covered": 0,
            "article_count": 0,
            "headlines": [],
            "sentiment_score": 0.0,
            "sentiment_label": "UNAVAILABLE",
            "note": "News API key not configured",
        }
