from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AnalysisRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    period: str = Field("1y", description="Historical period for analysis: 1mo, 3mo, 6mo, 1y, 2y, 5y")

    @field_validator("ticker")
    @classmethod
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper().strip()

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        valid = {"1mo", "3mo", "6mo", "1y", "2y", "5y"}
        if v not in valid:
            raise ValueError(f"period must be one of {valid}")
        return v


class AnalysisResponse(BaseModel):
    run_id: str
    ticker: str
    status: str
    created_at: datetime


class AnalysisStatusResponse(BaseModel):
    run_id: str
    ticker: str
    status: str
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None


class ReportResponse(BaseModel):
    report_id: str
    run_id: str
    ticker: str
    content: str
    structured: dict[str, Any] | None = None
    created_at: datetime


class HistoryItem(BaseModel):
    run_id: str
    ticker: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    has_report: bool = False


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
