"""Unit tests for the SourceRegistry — thread-safe in-process data source tracker."""
from __future__ import annotations

import threading
import time

import pytest

from app.services.source_registry import DataSourceInfo, SourceRegistry, SourceStatus, get_source_registry


class TestSourceRegistryDefaults:
    def test_initializes_with_known_sources(self):
        reg = SourceRegistry()
        all_sources = reg.get_all()
        keys = {s.key for s in all_sources}
        assert "yahoo_finance" in keys
        assert "newsapi" in keys
        assert "alpha_vantage" in keys

    def test_yahoo_finance_starts_ok(self):
        reg = SourceRegistry()
        src = reg.get("yahoo_finance")
        assert src is not None
        assert src.status == SourceStatus.OK

    def test_newsapi_starts_warn(self):
        reg = SourceRegistry()
        src = reg.get("newsapi")
        assert src is not None
        assert src.status == SourceStatus.WARN

    def test_alpha_vantage_starts_offline(self):
        reg = SourceRegistry()
        src = reg.get("alpha_vantage")
        assert src is not None
        assert src.status == SourceStatus.OFFLINE

    def test_future_sources_present(self):
        reg = SourceRegistry()
        future_keys = {s.key for s in reg.get_all() if s.status == SourceStatus.FUTURE}
        assert len(future_keys) >= 1

    def test_get_unknown_source_returns_none(self):
        reg = SourceRegistry()
        assert reg.get("nonexistent_source") is None


class TestRecordFetch:
    def test_record_fetch_updates_last_fetch(self):
        reg = SourceRegistry()
        assert reg.get("yahoo_finance").last_fetch is None
        reg.record_fetch("yahoo_finance", latency_ms=120.5, records=252)
        src = reg.get("yahoo_finance")
        assert src.last_fetch is not None
        assert src.latency_ms == 120.5
        assert src.records_returned == 252

    def test_record_fetch_with_error_sets_error_status(self):
        reg = SourceRegistry()
        reg.record_fetch("yahoo_finance", error="Connection timeout")
        src = reg.get("yahoo_finance")
        assert src.status == SourceStatus.ERROR
        assert "timeout" in src.error_message.lower()

    def test_record_fetch_clears_error_on_success(self):
        reg = SourceRegistry()
        reg.record_fetch("yahoo_finance", error="Previous error")
        assert reg.get("yahoo_finance").status == SourceStatus.ERROR
        reg.record_fetch("yahoo_finance", records=100)
        src = reg.get("yahoo_finance")
        assert src.status == SourceStatus.OK
        assert src.error_message == ""

    def test_record_fetch_ignores_unknown_source(self):
        reg = SourceRegistry()
        reg.record_fetch("nonexistent", latency_ms=50.0)  # must not raise

    def test_record_fetch_does_not_change_offline_status(self):
        reg = SourceRegistry()
        reg.record_fetch("alpha_vantage", records=10)
        assert reg.get("alpha_vantage").status == SourceStatus.OFFLINE

    def test_record_fetch_does_not_change_future_status(self):
        reg = SourceRegistry()
        future_src = next(s for s in reg.get_all() if s.status == SourceStatus.FUTURE)
        reg.record_fetch(future_src.key, records=1)
        assert reg.get(future_src.key).status == SourceStatus.FUTURE

    def test_assets_covered_updated(self):
        reg = SourceRegistry()
        reg.record_fetch("yahoo_finance", assets=5)
        assert reg.get("yahoo_finance").assets_covered == 5


class TestUpdateStatus:
    def test_update_status_changes_status(self):
        reg = SourceRegistry()
        reg.update_status("newsapi", SourceStatus.OK, notes="API key now configured")
        src = reg.get("newsapi")
        assert src.status == SourceStatus.OK
        assert src.notes == "API key now configured"

    def test_update_status_unknown_source_is_noop(self):
        reg = SourceRegistry()
        reg.update_status("ghost_source", SourceStatus.ERROR)  # must not raise


class TestSummary:
    def test_summary_returns_total(self):
        reg = SourceRegistry()
        summary = reg.summary()
        assert summary["total"] == len(reg.get_all())

    def test_summary_by_status_sums_to_total(self):
        reg = SourceRegistry()
        summary = reg.summary()
        total = sum(summary["by_status"].values())
        assert total == summary["total"]

    def test_summary_includes_ok_status(self):
        reg = SourceRegistry()
        summary = reg.summary()
        assert "OK" in summary["by_status"]


class TestToDictList:
    def test_to_dict_list_returns_list_of_dicts(self):
        reg = SourceRegistry()
        result = reg.to_dict_list()
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)

    def test_to_dict_list_contains_required_keys(self):
        reg = SourceRegistry()
        for item in reg.to_dict_list():
            for key in ("key", "name", "status", "description", "last_fetch", "latency_ms"):
                assert key in item

    def test_to_dict_list_status_is_string(self):
        reg = SourceRegistry()
        for item in reg.to_dict_list():
            assert isinstance(item["status"], str)


class TestThreadSafety:
    def test_concurrent_record_fetch_does_not_crash(self):
        reg = SourceRegistry()
        errors: list[Exception] = []

        def worker():
            try:
                for _ in range(20):
                    reg.record_fetch("yahoo_finance", latency_ms=10.0, records=5)
                    time.sleep(0)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread safety violations: {errors}"


class TestSingleton:
    def test_get_source_registry_returns_same_instance(self):
        reg1 = get_source_registry()
        reg2 = get_source_registry()
        assert reg1 is reg2
