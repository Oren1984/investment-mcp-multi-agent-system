from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class SourceStatus(str, Enum):
    OK = "OK"
    WARN = "WARN"
    ERROR = "ERROR"
    OFFLINE = "OFFLINE"
    FUTURE = "FUTURE"


@dataclass
class DataSourceInfo:
    key: str
    name: str
    status: SourceStatus
    description: str
    asset_types: str = ""
    last_fetch: Optional[datetime] = None
    latency_ms: float = 0.0
    records_returned: int = 0
    assets_covered: int = 0
    notes: str = ""
    error_message: str = ""


class SourceRegistry:
    """Thread-safe in-process registry tracking status of all data providers."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sources: dict[str, DataSourceInfo] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        self._sources = {
            "yahoo_finance": DataSourceInfo(
                key="yahoo_finance",
                name="Yahoo Finance",
                status=SourceStatus.OK,
                description="Price history, financials, company info via yfinance",
                asset_types="equities",
                notes="Provides price history, financial statements, technical data, sector ETFs",
            ),
            "newsapi": DataSourceInfo(
                key="newsapi",
                name="News API",
                status=SourceStatus.WARN,
                description="Financial news headlines via newsapi.org",
                asset_types="news",
                notes="Key not configured — using keyword sentiment fallback",
            ),
            "alpha_vantage": DataSourceInfo(
                key="alpha_vantage",
                name="Alpha Vantage",
                status=SourceStatus.OFFLINE,
                description="Market data and technical indicators",
                asset_types="equities",
                notes="API key reserved in config but provider not yet active",
            ),
            "finnhub": DataSourceInfo(
                key="finnhub",
                name="Finnhub",
                status=SourceStatus.FUTURE,
                description="Real-time market data, earnings, and company fundamentals",
                asset_types="equities",
                notes="Future integration — not yet implemented",
            ),
            "polygon": DataSourceInfo(
                key="polygon",
                name="Polygon.io",
                status=SourceStatus.FUTURE,
                description="Institutional-grade market data and aggregates",
                asset_types="equities, options, forex",
                notes="Future integration — not yet implemented",
            ),
        }

    def record_fetch(
        self,
        source_key: str,
        latency_ms: float = 0.0,
        records: int = 0,
        assets: int = 0,
        error: str = "",
    ) -> None:
        with self._lock:
            src = self._sources.get(source_key)
            if src is None:
                return
            src.last_fetch = datetime.now(timezone.utc)
            src.latency_ms = round(latency_ms, 1)
            src.records_returned = records
            if assets:
                src.assets_covered = assets
            if error:
                src.status = SourceStatus.ERROR
                src.error_message = error
            else:
                src.error_message = ""
                if src.status not in (SourceStatus.OFFLINE, SourceStatus.FUTURE):
                    if src.status == SourceStatus.ERROR:
                        src.status = SourceStatus.OK

    def update_status(self, source_key: str, status: SourceStatus, notes: str = "") -> None:
        with self._lock:
            src = self._sources.get(source_key)
            if src is None:
                return
            src.status = status
            if notes:
                src.notes = notes

    def get_all(self) -> list[DataSourceInfo]:
        with self._lock:
            return list(self._sources.values())

    def get(self, key: str) -> Optional[DataSourceInfo]:
        with self._lock:
            return self._sources.get(key)

    def to_dict_list(self) -> list[dict]:
        with self._lock:
            out = []
            for src in self._sources.values():
                out.append({
                    "key": src.key,
                    "name": src.name,
                    "status": src.status.value,
                    "description": src.description,
                    "asset_types": src.asset_types,
                    "last_fetch": src.last_fetch.isoformat() if src.last_fetch else None,
                    "latency_ms": src.latency_ms,
                    "records_returned": src.records_returned,
                    "assets_covered": src.assets_covered,
                    "notes": src.notes,
                    "error_message": src.error_message,
                })
            return out

    def summary(self) -> dict:
        with self._lock:
            by_status: dict[str, int] = {}
            for src in self._sources.values():
                key = src.status.value
                by_status[key] = by_status.get(key, 0) + 1
            return {
                "total": len(self._sources),
                "by_status": by_status,
            }


_registry: Optional[SourceRegistry] = None
_lock = threading.Lock()


def get_source_registry() -> SourceRegistry:
    global _registry
    if _registry is None:
        with _lock:
            if _registry is None:
                _registry = SourceRegistry()
    return _registry
