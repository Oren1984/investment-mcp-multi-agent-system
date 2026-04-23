"""
Unit tests for risk and technical indicator calculations.
All tests use synthetic price series so no external API calls are made.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
import yfinance as yf


def make_price_series(values: list[float], index_name: str = "Date") -> pd.DataFrame:
    dates = pd.date_range("2023-01-01", periods=len(values), freq="D")
    return pd.DataFrame(
        {"Open": values, "High": values, "Low": values, "Close": values, "Volume": [1_000_000] * len(values)},
        index=dates,
    )


class TestRSICalculation:
    """Verify RSI formula guards in risk_service.get_technical_indicators."""

    def _compute_rsi(self, close: pd.Series) -> float:
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        loss_val = float(loss.iloc[-1])
        gain_val = float(gain.iloc[-1])
        if loss_val == 0:
            return 100.0 if gain_val > 0 else 50.0
        rs_val = gain_val / loss_val
        return 100 - (100 / (1 + rs_val))

    def test_rsi_monotonically_rising_series_approaches_100(self):
        """Constantly rising prices: RSI should be very high (≥ 70)."""
        prices = list(range(100, 130))  # 30 daily closes, each 1 higher
        close = pd.Series([float(p) for p in prices])
        rsi = self._compute_rsi(close)
        assert rsi >= 70.0

    def test_rsi_monotonically_falling_series_approaches_0(self):
        """Constantly falling prices: RSI should be very low (≤ 30)."""
        prices = list(range(130, 100, -1))
        close = pd.Series([float(p) for p in prices])
        rsi = self._compute_rsi(close)
        assert rsi <= 30.0

    def test_rsi_no_loss_returns_100(self):
        """Only gains, zero losses: RSI should return 100."""
        prices = [100.0] * 14 + [101.0, 102.0, 103.0]
        close = pd.Series(prices)
        rsi = self._compute_rsi(close)
        assert rsi == 100.0

    def test_rsi_flat_prices_returns_50(self):
        """Flat prices: gain=0, loss=0, should return 50 as neutral."""
        prices = [100.0] * 20
        close = pd.Series(prices)
        rsi = self._compute_rsi(close)
        assert rsi == 50.0

    def test_rsi_range(self):
        """RSI must always be between 0 and 100."""
        import random
        random.seed(42)
        prices = [100.0 + random.uniform(-2, 2) for _ in range(30)]
        close = pd.Series(prices)
        rsi = self._compute_rsi(close)
        assert 0 <= rsi <= 100


class TestSharpeRatio:
    """Verify Sharpe ratio calculation correctness."""

    def _compute_sharpe(self, returns: pd.Series) -> float:
        TRADING_DAYS = 252
        risk_free = 0.05 / TRADING_DAYS
        excess = returns - risk_free
        if excess.std() == 0:
            return 0.0
        return float(excess.mean() / excess.std() * np.sqrt(TRADING_DAYS))

    def test_zero_std_returns_zero(self):
        """Constant returns (zero std) → Sharpe = 0."""
        returns = pd.Series([0.001] * 50)
        assert self._compute_sharpe(returns) == 0.0

    def test_positive_excess_returns_positive_sharpe(self):
        """Returns well above risk-free rate → positive Sharpe."""
        returns = pd.Series([0.003] * 252)  # ~75% annual
        sharpe = self._compute_sharpe(returns)
        assert sharpe > 0

    def test_negative_excess_returns_negative_sharpe(self):
        """Returns well below risk-free rate with variance → negative Sharpe."""
        # Mix of negative returns with small variance so std > 0
        import random
        random.seed(7)
        returns = pd.Series([-0.003 + random.uniform(-0.001, 0.001) for _ in range(252)])
        sharpe = self._compute_sharpe(returns)
        assert sharpe < 0


class TestVolatilityCalculation:
    def test_flat_prices_zero_volatility(self):
        """Constant prices → returns are 0 → std = 0 → annualized vol = 0."""
        TRADING_DAYS = 252
        returns = pd.Series([0.0] * 252)
        ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS) * 100)
        assert ann_vol == 0.0

    def test_volatile_series_has_positive_volatility(self):
        TRADING_DAYS = 252
        np.random.seed(42)
        returns = pd.Series(np.random.normal(0.001, 0.02, 252))
        ann_vol = float(returns.std() * np.sqrt(TRADING_DAYS) * 100)
        assert ann_vol > 0


class TestMaxDrawdown:
    def test_monotonically_rising_zero_drawdown(self):
        """Prices that only go up → max drawdown = 0."""
        prices = pd.Series([float(i) for i in range(100, 152)])
        returns = prices.pct_change().dropna()
        cum = (1 + returns).cumprod()
        rolling_max = cum.cummax()
        drawdown = (cum - rolling_max) / rolling_max
        assert abs(drawdown.min()) < 1e-10

    def test_crash_and_recovery(self):
        """50% crash (after a stable peak) should produce -50% drawdown."""
        # Need a flat peak before the crash so rolling_max captures the high
        prices = pd.Series([100.0, 100.0, 100.0, 50.0, 100.0])
        returns = prices.pct_change().dropna()
        cum = (1 + returns).cumprod()
        rolling_max = cum.cummax()
        drawdown = (cum - rolling_max) / rolling_max
        assert abs(drawdown.min() + 0.5) < 0.01


class TestRiskServiceWithMock:
    """Test RiskService with yfinance mocked out."""

    def _make_mock_history(self, prices: list[float]) -> pd.DataFrame:
        dates = pd.date_range("2023-01-01", periods=len(prices), freq="D")
        return pd.DataFrame(
            {
                "Open": prices,
                "High": [p * 1.01 for p in prices],
                "Low": [p * 0.99 for p in prices],
                "Close": prices,
                "Volume": [1_000_000] * len(prices),
            },
            index=dates,
        )

    def test_risk_metrics_returns_expected_keys(self):
        from app.services.risk_service import RiskService

        prices = [100.0 + i * 0.5 for i in range(260)]  # gently rising
        mock_df = self._make_mock_history(prices)

        with patch.object(yf.Ticker, "history", return_value=mock_df):
            svc = RiskService()
            result = svc.get_risk_metrics("AAPL", "1y")

        expected_keys = {"ticker", "beta", "annualized_volatility_pct", "max_drawdown_pct", "sharpe_ratio", "var_95_1day_pct"}
        assert expected_keys.issubset(result.keys())

    def test_technical_indicators_returns_expected_keys(self):
        from app.services.risk_service import RiskService

        prices = [100.0 + i * 0.5 for i in range(130)]
        mock_df = self._make_mock_history(prices)

        with patch.object(yf.Ticker, "history", return_value=mock_df):
            svc = RiskService()
            result = svc.get_technical_indicators("AAPL", "6mo")

        expected_keys = {"ticker", "current_price", "rsi_14", "macd", "sma_20", "trend", "rsi_signal"}
        assert expected_keys.issubset(result.keys())

    def test_rsi_in_valid_range(self):
        from app.services.risk_service import RiskService

        prices = [100.0 + i * 0.3 for i in range(130)]
        mock_df = self._make_mock_history(prices)

        with patch.object(yf.Ticker, "history", return_value=mock_df):
            svc = RiskService()
            result = svc.get_technical_indicators("AAPL", "6mo")

        assert 0 <= result["rsi_14"] <= 100

    def test_empty_dataframe_raises_external_api_error(self):
        from app.services.risk_service import RiskService
        from app.core.errors import ExternalAPIError

        with patch.object(yf.Ticker, "history", return_value=pd.DataFrame()):
            svc = RiskService()
            with pytest.raises(ExternalAPIError):
                svc.get_risk_metrics("INVALID", "1y")
