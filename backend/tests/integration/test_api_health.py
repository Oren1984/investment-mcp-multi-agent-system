"""Integration tests for health and readiness endpoints."""
import pytest
import pytest_asyncio


@pytest.mark.asyncio
class TestHealthEndpoints:
    async def test_health_returns_200(self, test_client):
        resp = await test_client.get("/api/v1/health")
        assert resp.status_code == 200

    async def test_health_response_body(self, test_client):
        resp = await test_client.get("/api/v1/health")
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data

    async def test_ready_returns_200(self, test_client):
        resp = await test_client.get("/api/v1/ready")
        assert resp.status_code == 200

    async def test_ready_includes_tool_list(self, test_client):
        resp = await test_client.get("/api/v1/ready")
        data = resp.json()
        assert "mcp_tools" in data
        assert isinstance(data["mcp_tools"], list)
        assert len(data["mcp_tools"]) > 0

    async def test_metrics_endpoint_available(self, test_client):
        resp = await test_client.get("/metrics")
        assert resp.status_code == 200
        # Prometheus metrics are plain text
        assert "http_requests" in resp.text or "python" in resp.text

    async def test_docs_available(self, test_client):
        resp = await test_client.get("/docs")
        assert resp.status_code == 200
