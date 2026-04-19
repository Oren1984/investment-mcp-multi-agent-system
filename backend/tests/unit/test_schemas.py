"""Unit tests for Pydantic schemas — validation and serialization correctness."""
import pytest
from pydantic import ValidationError

from app.schemas.analysis import AnalysisRequest, HistoryItem, ReportResponse
from app.schemas.common import HealthResponse, ReadyResponse


class TestAnalysisRequest:
    def test_ticker_uppercased(self):
        req = AnalysisRequest(ticker="aapl")
        assert req.ticker == "AAPL"

    def test_ticker_stripped(self):
        req = AnalysisRequest(ticker="  msft  ")
        assert req.ticker == "MSFT"

    def test_default_period(self):
        req = AnalysisRequest(ticker="AAPL")
        assert req.period == "1y"

    def test_valid_periods(self):
        for period in ("1mo", "3mo", "6mo", "1y", "2y", "5y"):
            req = AnalysisRequest(ticker="AAPL", period=period)
            assert req.period == period

    def test_invalid_period_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            AnalysisRequest(ticker="AAPL", period="10y")
        assert "period" in str(exc_info.value).lower() or "value" in str(exc_info.value).lower()

    def test_empty_ticker_rejected(self):
        with pytest.raises(ValidationError):
            AnalysisRequest(ticker="")

    def test_ticker_too_long_rejected(self):
        with pytest.raises(ValidationError):
            AnalysisRequest(ticker="TOOLONGTICKER")

    def test_period_invalid_type(self):
        with pytest.raises(ValidationError):
            AnalysisRequest(ticker="AAPL", period="daily")


class TestHealthResponse:
    def test_default_version(self):
        resp = HealthResponse(status="ok")
        assert resp.version == "1.0.0"

    def test_status_preserved(self):
        resp = HealthResponse(status="degraded")
        assert resp.status == "degraded"


class TestReadyResponse:
    def test_tool_list(self):
        resp = ReadyResponse(status="ok", db="ok", mcp_tools=["get_stock_price", "save_report"])
        assert "get_stock_price" in resp.mcp_tools
        assert len(resp.mcp_tools) == 2
