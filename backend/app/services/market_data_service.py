from __future__ import annotations

from datetime import datetime

import pandas as pd
import yfinance as yf

from app.core.errors import ExternalAPIError
from app.core.logging import get_logger

logger = get_logger(__name__)


class MarketDataService:
    def get_price_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> dict:
        try:
            t = yf.Ticker(ticker)
            df: pd.DataFrame = t.history(period=period, interval=interval)
            if df.empty:
                raise ExternalAPIError(f"No price data for {ticker}")
            df.index = df.index.strftime("%Y-%m-%d")
            return {
                "ticker": ticker,
                "period": period,
                "interval": interval,
                "data": df[["Open", "High", "Low", "Close", "Volume"]].round(4).to_dict(orient="index"),
                "current_price": float(df["Close"].iloc[-1]),
                "price_change_pct": float(
                    (df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0] * 100
                ),
            }
        except ExternalAPIError:
            raise
        except Exception as e:
            logger.exception("market_data error", extra={"ticker": ticker})
            raise ExternalAPIError(f"Failed to fetch price data for {ticker}: {e}") from e

    def get_company_info(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            return {
                "ticker": ticker,
                "company_name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "exchange": info.get("exchange", ""),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield"),
                "52w_high": info.get("fiftyTwoWeekHigh"),
                "52w_low": info.get("fiftyTwoWeekLow"),
                "avg_volume": info.get("averageVolume"),
                "description": info.get("longBusinessSummary", "")[:500],
            }
        except Exception as e:
            logger.exception("company_info error", extra={"ticker": ticker})
            raise ExternalAPIError(f"Failed to fetch company info for {ticker}: {e}") from e

    def get_sector_comparison(self, ticker: str, sector_etf: str | None = None) -> dict:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            sector = info.get("sector", "")

            etf_map = {
                "Technology": "XLK",
                "Healthcare": "XLV",
                "Financials": "XLF",
                "Consumer Cyclical": "XLY",
                "Consumer Defensive": "XLP",
                "Energy": "XLE",
                "Industrials": "XLI",
                "Materials": "XLB",
                "Real Estate": "XLRE",
                "Utilities": "XLU",
                "Communication Services": "XLC",
            }
            etf = sector_etf or etf_map.get(sector, "SPY")

            stock_hist = yf.Ticker(ticker).history(period="1y")
            etf_hist = yf.Ticker(etf).history(period="1y")

            if stock_hist.empty or etf_hist.empty:
                raise ExternalAPIError(f"Could not retrieve comparison data for {ticker}")

            stock_return = float(
                (stock_hist["Close"].iloc[-1] - stock_hist["Close"].iloc[0]) / stock_hist["Close"].iloc[0] * 100
            )
            etf_return = float(
                (etf_hist["Close"].iloc[-1] - etf_hist["Close"].iloc[0]) / etf_hist["Close"].iloc[0] * 100
            )

            return {
                "ticker": ticker,
                "sector": sector,
                "sector_etf": etf,
                "stock_1y_return_pct": round(stock_return, 2),
                "sector_1y_return_pct": round(etf_return, 2),
                "relative_performance_pct": round(stock_return - etf_return, 2),
            }
        except ExternalAPIError:
            raise
        except Exception as e:
            raise ExternalAPIError(f"Failed sector comparison for {ticker}: {e}") from e
