"""Integration tests for API key authentication."""
from __future__ import annotations

import pytest
from unittest.mock import patch


@pytest.mark.asyncio
class TestAPIKeyAuth:
    async def test_no_key_configured_allows_all_requests(self, test_client):
        # Default: settings.api_key == "" → auth disabled
        resp = await test_client.post(
            "/api/v1/analyze",
            json={"ticker": "AAPL", "period": "1y"},
        )
        # 202 accepted (gateway mock returns immediately)
        assert resp.status_code == 202

    async def test_with_key_configured_correct_key_passes(self, test_client):
        with patch("app.api.deps.settings") as mock_cfg:
            mock_cfg.api_key = "test-secret-key"
            resp = await test_client.get(
                "/api/v1/analyze",
                headers={"X-API-Key": "test-secret-key"},
            )
        assert resp.status_code == 200

    async def test_with_key_configured_wrong_key_returns_403(self, test_client):
        with patch("app.api.deps.settings") as mock_cfg:
            mock_cfg.api_key = "correct-key"
            resp = await test_client.get(
                "/api/v1/analyze",
                headers={"X-API-Key": "wrong-key"},
            )
        assert resp.status_code == 403
        assert "Invalid API key" in resp.json()["detail"]

    async def test_with_key_configured_missing_header_returns_401(self, test_client):
        with patch("app.api.deps.settings") as mock_cfg:
            mock_cfg.api_key = "some-key"
            resp = await test_client.get("/api/v1/analyze")
        assert resp.status_code == 401
        assert "Missing" in resp.json()["detail"]

    async def test_health_endpoint_requires_no_key(self, test_client):
        # Health endpoints are always public regardless of API_KEY setting
        with patch("app.api.deps.settings") as mock_cfg:
            mock_cfg.api_key = "strict-key"
            resp = await test_client.get("/api/v1/health")
        assert resp.status_code == 200

    async def test_ready_endpoint_requires_no_key(self, test_client):
        with patch("app.api.deps.settings") as mock_cfg:
            mock_cfg.api_key = "strict-key"
            resp = await test_client.get("/api/v1/ready")
        assert resp.status_code == 200
