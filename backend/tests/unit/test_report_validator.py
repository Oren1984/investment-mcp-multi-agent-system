"""Unit tests for report section validator."""
from __future__ import annotations

import pytest

from app.utils.report_validator import validate_report_sections, REQUIRED_SECTIONS

COMPLETE_REPORT = """
## Executive Summary
Strong buy.

## Fundamental Analysis
Solid revenue growth.

## Technical Analysis
RSI 58, bullish MACD.

## Sector Analysis
Outperforming peers.

## Risk Assessment
Beta 1.2, low drawdown.

## Recommendation
BUY
"""

PARTIAL_REPORT = """
## Executive Summary
Overview.

## Fundamental Analysis
Details.
"""


class TestValidateReportSections:
    def test_complete_report_is_valid(self):
        is_valid, missing = validate_report_sections(COMPLETE_REPORT)
        assert is_valid is True
        assert missing == []

    def test_partial_report_returns_missing_sections(self):
        is_valid, missing = validate_report_sections(PARTIAL_REPORT)
        assert is_valid is False
        assert "Technical Analysis" in missing
        assert "Sector Analysis" in missing
        assert "Risk Assessment" in missing
        assert "Recommendation" in missing

    def test_empty_report_returns_all_missing(self):
        is_valid, missing = validate_report_sections("")
        assert is_valid is False
        assert set(missing) == set(REQUIRED_SECTIONS)

    def test_case_insensitive_matching(self):
        # LLMs may vary case; validation should still pass
        lowercased = COMPLETE_REPORT.lower()
        is_valid, missing = validate_report_sections(lowercased)
        assert is_valid is True

    def test_returns_exactly_missing_sections(self):
        report = "## Executive Summary\nOK\n## Recommendation\nBUY"
        is_valid, missing = validate_report_sections(report)
        assert is_valid is False
        assert "Fundamental Analysis" in missing
        assert "Executive Summary" not in missing
        assert "Recommendation" not in missing
