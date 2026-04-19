"""
Integration tests for DB repositories.
Uses in-memory SQLite via conftest.py fixtures.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio

from app.db.models.analysis_run import AnalysisRun, RunStatus
from app.db.models.report import Report


@pytest.mark.asyncio
class TestAnalysisRunRepository:
    async def test_create_run(self, async_db_session):
        from app.db.repositories.analysis_run_repo import AnalysisRunRepository

        repo = AnalysisRunRepository(async_db_session)
        run = await repo.create("AAPL", {"period": "1y"})

        assert run.id is not None
        assert run.ticker == "AAPL"
        assert run.status == RunStatus.PENDING
        assert run.config == {"period": "1y"}

    async def test_create_uppercases_ticker(self, async_db_session):
        from app.db.repositories.analysis_run_repo import AnalysisRunRepository

        repo = AnalysisRunRepository(async_db_session)
        run = await repo.create("aapl", {})
        assert run.ticker == "AAPL"

    async def test_get_existing_run(self, async_db_session):
        from app.db.repositories.analysis_run_repo import AnalysisRunRepository

        repo = AnalysisRunRepository(async_db_session)
        created = await repo.create("MSFT", {})

        fetched = await repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.ticker == "MSFT"

    async def test_get_nonexistent_returns_none(self, async_db_session):
        from app.db.repositories.analysis_run_repo import AnalysisRunRepository

        repo = AnalysisRunRepository(async_db_session)
        result = await repo.get(str(uuid4()))
        assert result is None

    async def test_update_status_to_running(self, async_db_session):
        from app.db.repositories.analysis_run_repo import AnalysisRunRepository

        repo = AnalysisRunRepository(async_db_session)
        run = await repo.create("TSLA", {})
        await repo.update_status(run.id, RunStatus.RUNNING)

        updated = await repo.get(run.id)
        assert updated.status == RunStatus.RUNNING
        assert updated.started_at is not None

    async def test_update_status_to_completed_sets_completed_at(self, async_db_session):
        from app.db.repositories.analysis_run_repo import AnalysisRunRepository

        repo = AnalysisRunRepository(async_db_session)
        run = await repo.create("NVDA", {})
        await repo.update_status(run.id, RunStatus.COMPLETED)

        updated = await repo.get(run.id)
        assert updated.status == RunStatus.COMPLETED
        assert updated.completed_at is not None

    async def test_update_status_to_failed_sets_error(self, async_db_session):
        from app.db.repositories.analysis_run_repo import AnalysisRunRepository

        repo = AnalysisRunRepository(async_db_session)
        run = await repo.create("GOOGL", {})
        await repo.update_status(run.id, RunStatus.FAILED, error_message="API timeout")

        updated = await repo.get(run.id)
        assert updated.status == RunStatus.FAILED
        assert updated.error_message == "API timeout"

    async def test_list_recent_ordered_by_created_at(self, async_db_session):
        from app.db.repositories.analysis_run_repo import AnalysisRunRepository

        repo = AnalysisRunRepository(async_db_session)
        await repo.create("AAPL", {})
        await repo.create("MSFT", {})
        await repo.create("TSLA", {})

        runs = await repo.list_recent(limit=3)
        assert len(runs) >= 3
        # Most recent first
        for i in range(len(runs) - 1):
            assert runs[i].created_at >= runs[i + 1].created_at

    async def test_list_recent_respects_limit(self, async_db_session):
        from app.db.repositories.analysis_run_repo import AnalysisRunRepository

        repo = AnalysisRunRepository(async_db_session)
        for _ in range(5):
            await repo.create("AAPL", {})

        runs = await repo.list_recent(limit=2)
        assert len(runs) <= 2


@pytest.mark.asyncio
class TestReportRepository:
    async def test_get_by_run_id_returns_report(self, async_db_session):
        from app.db.repositories.analysis_run_repo import AnalysisRunRepository
        from app.db.repositories.report_repo import ReportRepository

        run_repo = AnalysisRunRepository(async_db_session)
        run = await run_repo.create("AMZN", {})

        report = Report(
            id=str(uuid4()),
            run_id=run.id,
            ticker_symbol="AMZN",
            content="Test report",
            structured={},
            created_at=datetime.now(timezone.utc),
        )
        async_db_session.add(report)
        await async_db_session.commit()

        report_repo = ReportRepository(async_db_session)
        fetched = await report_repo.get_by_run_id(run.id)

        assert fetched is not None
        assert fetched.ticker_symbol == "AMZN"
        assert fetched.content == "Test report"

    async def test_get_by_run_id_nonexistent_returns_none(self, async_db_session):
        from app.db.repositories.report_repo import ReportRepository

        repo = ReportRepository(async_db_session)
        result = await repo.get_by_run_id(str(uuid4()))
        assert result is None
