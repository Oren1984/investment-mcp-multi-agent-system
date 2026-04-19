from __future__ import annotations

import numpy as np
import pandas as pd
import yfinance as yf

from app.core.errors import ExternalAPIError
from app.core.logging import get_logger

logger = get_logger(__name__)

BENCHMARK = "SPY"
TRADING_DAYS = 252


class RiskService:
    def get_risk_metrics(self, ticker: str, period: str = "1y") -> dict:
        try:
            stock_hist = yf.Ticker(ticker).history(period=period)
            bench_hist = yf.Ticker(BENCHMARK).history(period=period)

            if stock_hist.empty:
                raise ExternalAPIError(f"No price data for {ticker}")

            stock_returns = stock_hist["Close"].pct_change().dropna()
            bench_returns = bench_hist["Close"].pct_change().dropna()

            # Align dates
            aligned = pd.DataFrame({"stock": stock_returns, "bench": bench_returns}).dropna()

            # Beta
            cov_matrix = aligned.cov()
            beta = float(cov_matrix.loc["stock", "bench"] / cov_matrix.loc["bench", "bench"])

            # Annualized volatility
            ann_vol = float(stock_returns.std() * np.sqrt(TRADING_DAYS) * 100)

            # Max drawdown
            cum = (1 + stock_returns).cumprod()
            rolling_max = cum.cummax()
            drawdown = (cum - rolling_max) / rolling_max
            max_drawdown = float(drawdown.min() * 100)

            # Sharpe ratio (risk-free rate ≈ 5% annualized)
            risk_free = 0.05 / TRADING_DAYS
            excess_returns = stock_returns - risk_free
            sharpe = float(excess_returns.mean() / excess_returns.std() * np.sqrt(TRADING_DAYS)) if excess_returns.std() > 0 else 0.0

            # Value at Risk (95% confidence, 1-day)
            var_95 = float(np.percentile(stock_returns, 5) * 100)

            # Annualized return
            ann_return = float(((1 + stock_returns.mean()) ** TRADING_DAYS - 1) * 100)

            return {
                "ticker": ticker,
                "period": period,
                "beta": round(beta, 3),
                "annualized_volatility_pct": round(ann_vol, 2),
                "annualized_return_pct": round(ann_return, 2),
                "max_drawdown_pct": round(max_drawdown, 2),
                "sharpe_ratio": round(sharpe, 3),
                "var_95_1day_pct": round(var_95, 3),
                "benchmark": BENCHMARK,
            }
        except ExternalAPIError:
            raise
        except Exception as e:
            logger.exception("risk_metrics error", extra={"ticker": ticker})
            raise ExternalAPIError(f"Failed to calculate risk metrics for {ticker}: {e}") from e

    def get_technical_indicators(self, ticker: str, period: str = "6mo") -> dict:
        try:
            hist = yf.Ticker(ticker).history(period=period)
            if hist.empty:
                raise ExternalAPIError(f"No price data for {ticker}")

            close = hist["Close"]
            volume = hist["Volume"]

            # Simple Moving Averages
            sma20 = float(close.rolling(20).mean().iloc[-1])
            sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
            sma200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None
            ema12 = float(close.ewm(span=12).mean().iloc[-1])
            ema26 = float(close.ewm(span=26).mean().iloc[-1])

            # MACD
            macd_line = ema12 - ema26
            signal_line = float(pd.Series([macd_line]).ewm(span=9).mean().iloc[-1])
            macd_hist = macd_line - signal_line

            # RSI (14-period) — guard against division by zero when loss = 0
            delta = close.diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()
            loss_val = float(loss.iloc[-1])
            gain_val = float(gain.iloc[-1])
            if loss_val == 0:
                rsi = 100.0 if gain_val > 0 else 50.0
            else:
                rs_val = gain_val / loss_val
                rsi = 100 - (100 / (1 + rs_val))

            # Bollinger Bands (20-period, 2 std)
            bb_mid = close.rolling(20).mean()
            bb_std = close.rolling(20).std()
            bb_upper = float((bb_mid + 2 * bb_std).iloc[-1])
            bb_lower = float((bb_mid - 2 * bb_std).iloc[-1])
            current_price = float(close.iloc[-1])

            # Volume trend
            avg_volume_20 = float(volume.rolling(20).mean().iloc[-1])
            last_volume = float(volume.iloc[-1])

            return {
                "ticker": ticker,
                "current_price": round(current_price, 2),
                "sma_20": round(sma20, 2),
                "sma_50": round(sma50, 2) if sma50 else None,
                "sma_200": round(sma200, 2) if sma200 else None,
                "ema_12": round(ema12, 2),
                "ema_26": round(ema26, 2),
                "macd": round(macd_line, 4),
                "macd_signal": round(signal_line, 4),
                "macd_histogram": round(macd_hist, 4),
                "rsi_14": round(rsi, 2),
                "bollinger_upper": round(bb_upper, 2),
                "bollinger_lower": round(bb_lower, 2),
                "volume_vs_avg_pct": round((last_volume / avg_volume_20 - 1) * 100, 1) if avg_volume_20 > 0 else 0,
                "trend": "BULLISH" if current_price > sma50 else "BEARISH" if sma50 else "NEUTRAL",
                "rsi_signal": "OVERSOLD" if rsi < 30 else "OVERBOUGHT" if rsi > 70 else "NEUTRAL",
            }
        except ExternalAPIError:
            raise
        except Exception as e:
            raise ExternalAPIError(f"Failed to calculate technical indicators for {ticker}: {e}") from e
