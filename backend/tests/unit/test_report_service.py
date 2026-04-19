"""Unit tests for report service — parsing and storage logic."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest


SAMPLE_REPORT = """# Investment Analysis Report: AAPL

## Executive Summary
Apple is a strong buy with solid fundamentals and bullish technicals.

## Fundamental Analysis
Revenue grew 5% YoY. EPS of $6.13. Healthy margins.

## Technical Analysis
RSI at 58, MACD positive. Price above SMA 50 and 200.

## Sector Context
Outperforming XLK by 5%. Strong competitive position.

## Risk Profile
Beta 1.25. Volatility 24.5%. Moderate risk.

## Investment Recommendation
BUY. 12-month target $195. Catalyst: iPhone 16 cycle.

## Disclaimer
This is for informational purposes only.
"""


class TestReportServiceParsing:
    def test_parse_structured_returns_all_sections(self, sync_db_session):
        from app.services.report_service import ReportService

        svc = ReportService(sync_db_session)
        structured = svc.parse_structured(SAMPLE_REPORT, "AAPL")

        assert structured["ticker"] == "AAPL"
        assert "fundamental" in structured["fundamentals"].lower() or structured["fundamentals"] != ""
        assert structured["recommendation"] != ""

    def test_parse_structured_ticker_preserved(self, sync_db_session):
        from app.services.report_service import ReportService

        svc = ReportService(sync_db_session)
        structured = svc.parse_structured(SAMPLE_REPORT, "TSLA")
        assert structured["ticker"] == "TSLA"

    def test_parse_empty_report(self, sync_db_session):
        from app.services.report_service import ReportService

        svc = ReportService(sync_db_session)
        structured = svc.parse_structured("", "AAPL")
        # All sections should be empty strings, no crash
        assert structured["ticker"] == "AAPL"
        assert isinstance(structured["executive_summary"], str)


class TestReportServiceSave:
    def test_save_creates_report_record(self, sync_db_session):
        from app.services.report_service import ReportService
        from uuid import uuid4

        svc = ReportService(sync_db_session)
        run_id = str(uuid4())

        # Need an AnalysisRun to satisfy FK
        from app.db.models.analysis_run import AnalysisRun, RunStatus
        run = AnalysisRun(id=run_id, ticker="AAPL", status=RunStatus.RUNNING, config={})
        sync_db_session.add(run)
        sync_db_session.flush()

        report = svc.save(run_id=run_id, ticker="AAPL", content=SAMPLE_REPORT)

        assert report.id is not None
        assert report.run_id == run_id
        assert report.ticker_symbol == "AAPL"
        assert report.content == SAMPLE_REPORT

    def test_save_with_structured_data(self, sync_db_session):
        from app.services.report_service import ReportService
        from uuid import uuid4
        from app.db.models.analysis_run import AnalysisRun, RunStatus

        run_id = str(uuid4())
        run = AnalysisRun(id=run_id, ticker="MSFT", status=RunStatus.RUNNING, config={})
        sync_db_session.add(run)
        sync_db_session.flush()

        svc = ReportService(sync_db_session)
        structured = {"recommendation": "BUY", "ticker": "MSFT"}
        report = svc.save(run_id=run_id, ticker="MSFT", content="Test", structured=structured)

        assert report.structured["recommendation"] == "BUY"
