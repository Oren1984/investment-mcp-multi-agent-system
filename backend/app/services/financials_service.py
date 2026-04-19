from __future__ import annotations

import yfinance as yf

from app.core.errors import ExternalAPIError
from app.core.logging import get_logger

logger = get_logger(__name__)


class FinancialsService:
    def get_income_statement(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            df = t.financials
            if df is None or df.empty:
                raise ExternalAPIError(f"No income statement data for {ticker}")
            df.columns = [str(c.date()) for c in df.columns]
            return {"ticker": ticker, "statement": "income", "data": df.to_dict()}
        except ExternalAPIError:
            raise
        except Exception as e:
            raise ExternalAPIError(f"Failed to fetch income statement for {ticker}: {e}") from e

    def get_balance_sheet(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            df = t.balance_sheet
            if df is None or df.empty:
                raise ExternalAPIError(f"No balance sheet data for {ticker}")
            df.columns = [str(c.date()) for c in df.columns]
            return {"ticker": ticker, "statement": "balance_sheet", "data": df.to_dict()}
        except ExternalAPIError:
            raise
        except Exception as e:
            raise ExternalAPIError(f"Failed to fetch balance sheet for {ticker}: {e}") from e

    def get_cash_flow(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            df = t.cashflow
            if df is None or df.empty:
                raise ExternalAPIError(f"No cash flow data for {ticker}")
            df.columns = [str(c.date()) for c in df.columns]
            return {"ticker": ticker, "statement": "cash_flow", "data": df.to_dict()}
        except ExternalAPIError:
            raise
        except Exception as e:
            raise ExternalAPIError(f"Failed to fetch cash flow for {ticker}: {e}") from e

    def get_key_metrics(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            return {
                "ticker": ticker,
                "eps": info.get("trailingEps"),
                "eps_growth_yoy": info.get("earningsGrowth"),
                "revenue_growth_yoy": info.get("revenueGrowth"),
                "gross_margins": info.get("grossMargins"),
                "operating_margins": info.get("operatingMargins"),
                "profit_margins": info.get("profitMargins"),
                "return_on_equity": info.get("returnOnEquity"),
                "return_on_assets": info.get("returnOnAssets"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "quick_ratio": info.get("quickRatio"),
                "free_cashflow": info.get("freeCashflow"),
                "total_revenue": info.get("totalRevenue"),
                "total_debt": info.get("totalDebt"),
                "book_value": info.get("bookValue"),
            }
        except Exception as e:
            raise ExternalAPIError(f"Failed to fetch key metrics for {ticker}: {e}") from e
