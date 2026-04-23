"""Integration tests for the /sources endpoint."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
class TestSourcesEndpoint:
    async def test_list_sources_returns_200(self, test_client):
        resp = await test_client.get("/api/v1/sources")
        assert resp.status_code == 200

    async def test_list_sources_response_structure(self, test_client):
        resp = await test_client.get("/api/v1/sources")
        data = resp.json()
        assert "sources" in data
        assert "summary" in data
        assert isinstance(data["sources"], list)

    async def test_sources_contain_required_fields(self, test_client):
        resp = await test_client.get("/api/v1/sources")
        sources = resp.json()["sources"]
        assert len(sources) > 0
        for src in sources:
            for field in ("key", "name", "status", "description"):
                assert field in src, f"Missing field '{field}' in source {src.get('key')}"

    async def test_sources_include_yahoo_finance(self, test_client):
        resp = await test_client.get("/api/v1/sources")
        keys = {s["key"] for s in resp.json()["sources"]}
        assert "yahoo_finance" in keys

    async def test_sources_status_is_valid_string(self, test_client):
        resp = await test_client.get("/api/v1/sources")
        valid_statuses = {"OK", "WARN", "ERROR", "OFFLINE", "FUTURE"}
        for src in resp.json()["sources"]:
            assert src["status"] in valid_statuses, f"Invalid status: {src['status']}"

    async def test_summary_endpoint_returns_200(self, test_client):
        resp = await test_client.get("/api/v1/sources/status")
        assert resp.status_code == 200

    async def test_summary_includes_total_and_by_status(self, test_client):
        resp = await test_client.get("/api/v1/sources/status")
        data = resp.json()
        assert "total" in data
        assert "by_status" in data
        assert isinstance(data["total"], int)
        assert data["total"] > 0

    async def test_summary_by_status_values_are_counts(self, test_client):
        resp = await test_client.get("/api/v1/sources/status")
        data = resp.json()
        for status, count in data["by_status"].items():
            assert isinstance(count, int)
            assert count >= 0

    async def test_sources_no_auth_required(self, test_client):
        """Sources endpoint is public — no API key should be required."""
        resp = await test_client.get("/api/v1/sources")
        assert resp.status_code != 403
