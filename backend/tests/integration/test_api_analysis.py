"""
Integration tests for analysis API routes.
DB is in-memory SQLite; crew execution is mocked so no LLM calls are made.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest


@pytest.mark.asyncio
class TestCreateAnalysis:
    async def test_submit_returns_202(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background") as mock_bg:
            mock_bg.return_value = None
            resp = await test_client.post("/api/v1/analyze", json={"ticker": "AAPL"})
        assert resp.status_code == 202

    async def test_submit_returns_run_id(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background"):
            resp = await test_client.post("/api/v1/analyze", json={"ticker": "AAPL"})
        data = resp.json()
        assert "run_id" in data
        assert len(data["run_id"]) > 0

    async def test_submit_ticker_uppercased(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background"):
            resp = await test_client.post("/api/v1/analyze", json={"ticker": "aapl"})
        data = resp.json()
        assert data["ticker"] == "AAPL"

    async def test_submit_invalid_ticker_rejected(self, test_client):
        resp = await test_client.post("/api/v1/analyze", json={"ticker": ""})
        assert resp.status_code == 422

    async def test_submit_invalid_period_rejected(self, test_client):
        resp = await test_client.post("/api/v1/analyze", json={"ticker": "AAPL", "period": "10y"})
        assert resp.status_code == 422

    async def test_submit_status_is_pending(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background"):
            resp = await test_client.post("/api/v1/analyze", json={"ticker": "AAPL"})
        data = resp.json()
        assert data["status"] == "PENDING"


@pytest.mark.asyncio
class TestGetStatus:
    async def test_status_of_created_run(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background"):
            create_resp = await test_client.post("/api/v1/analyze", json={"ticker": "MSFT"})
        run_id = create_resp.json()["run_id"]

        status_resp = await test_client.get(f"/api/v1/analyze/{run_id}/status")
        assert status_resp.status_code == 200

        data = status_resp.json()
        assert data["run_id"] == run_id
        assert data["ticker"] == "MSFT"
        assert data["status"] in ("PENDING", "RUNNING", "COMPLETED", "FAILED")

    async def test_status_nonexistent_run_returns_404(self, test_client):
        fake_id = str(uuid4())
        resp = await test_client.get(f"/api/v1/analyze/{fake_id}/status")
        assert resp.status_code == 404

    async def test_status_response_schema(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background"):
            create_resp = await test_client.post("/api/v1/analyze", json={"ticker": "TSLA"})
        run_id = create_resp.json()["run_id"]

        resp = await test_client.get(f"/api/v1/analyze/{run_id}/status")
        data = resp.json()

        required_fields = {"run_id", "ticker", "status", "created_at"}
        assert required_fields.issubset(data.keys())


@pytest.mark.asyncio
class TestGetReport:
    async def test_report_not_ready_returns_202(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background"):
            create_resp = await test_client.post("/api/v1/analyze", json={"ticker": "GOOGL"})
        run_id = create_resp.json()["run_id"]

        # Run is PENDING, not COMPLETED → should return 202
        resp = await test_client.get(f"/api/v1/analyze/{run_id}/report")
        assert resp.status_code == 202

    async def test_report_nonexistent_run_returns_404(self, test_client):
        fake_id = str(uuid4())
        resp = await test_client.get(f"/api/v1/analyze/{fake_id}/report")
        assert resp.status_code == 404

    async def test_completed_run_returns_report(self, test_client, async_db_session):
        from app.db.models.analysis_run import AnalysisRun, RunStatus
        from app.db.models.report import Report
        from datetime import datetime, timezone

        # Manually insert a COMPLETED run and report
        run_id = str(uuid4())
        report_id = str(uuid4())

        run = AnalysisRun(
            id=run_id,
            ticker="NVDA",
            status=RunStatus.COMPLETED,
            config={"period": "1y"},
            created_at=datetime.now(timezone.utc),
        )
        async_db_session.add(run)
        await async_db_session.flush()

        report = Report(
            id=report_id,
            run_id=run_id,
            ticker_symbol="NVDA",
            content="# Report for NVDA\n## Executive Summary\nBullish.",
            structured={"executive_summary": "Bullish"},
            created_at=datetime.now(timezone.utc),
        )
        async_db_session.add(report)
        await async_db_session.commit()

        resp = await test_client.get(f"/api/v1/analyze/{run_id}/report")
        assert resp.status_code == 200

        data = resp.json()
        assert data["ticker"] == "NVDA"
        assert data["run_id"] == run_id
        assert "content" in data
        assert "# Report for NVDA" in data["content"]


@pytest.mark.asyncio
class TestListHistory:
    async def test_empty_history(self, test_client):
        resp = await test_client.get("/api/v1/analyze")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    async def test_history_after_submit(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background"):
            await test_client.post("/api/v1/analyze", json={"ticker": "AMZN"})

        resp = await test_client.get("/api/v1/analyze")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    async def test_history_limit_param(self, test_client):
        resp = await test_client.get("/api/v1/analyze?limit=5")
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestExecutionMode:
    async def test_default_execution_mode_is_hybrid(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background"):
            resp = await test_client.post("/api/v1/analyze", json={"ticker": "AAPL"})
        assert resp.status_code == 202
        data = resp.json()
        assert data["execution_mode"] == "hybrid"

    async def test_rag_only_mode_accepted(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background"):
            resp = await test_client.post(
                "/api/v1/analyze",
                json={"ticker": "AAPL", "execution_mode": "rag_only"},
            )
        assert resp.status_code == 202
        assert resp.json()["execution_mode"] == "rag_only"

    async def test_agent_only_mode_accepted(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background"):
            resp = await test_client.post(
                "/api/v1/analyze",
                json={"ticker": "AAPL", "execution_mode": "agent_only"},
            )
        assert resp.status_code == 202
        assert resp.json()["execution_mode"] == "agent_only"

    async def test_invalid_mode_rejected(self, test_client):
        resp = await test_client.post(
            "/api/v1/analyze",
            json={"ticker": "AAPL", "execution_mode": "turbo_mode"},
        )
        assert resp.status_code == 422

    async def test_execution_mode_persisted_in_status(self, test_client):
        with patch("app.api.routes.analysis._run_crew_background"):
            create_resp = await test_client.post(
                "/api/v1/analyze",
                json={"ticker": "TSLA", "execution_mode": "rag_only"},
            )
        run_id = create_resp.json()["run_id"]

        status_resp = await test_client.get(f"/api/v1/analyze/{run_id}/status")
        assert status_resp.status_code == 200
        data = status_resp.json()
        assert data["execution_mode"] == "rag_only"
