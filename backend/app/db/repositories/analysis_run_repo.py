from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.db.models.analysis_run import AnalysisRun, RunStatus
from app.db.models.agent_output import AgentOutput


class AnalysisRunRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, ticker: str, config: dict) -> AnalysisRun:
        run = AnalysisRun(ticker=ticker.upper(), config=config)
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def get(self, run_id: str) -> AnalysisRun | None:
        result = await self.session.execute(select(AnalysisRun).where(AnalysisRun.id == run_id))
        return result.scalar_one_or_none()

    async def list_recent(self, limit: int = 20) -> list[AnalysisRun]:
        result = await self.session.execute(
            select(AnalysisRun)
            .options(selectinload(AnalysisRun.report))
            .order_by(AnalysisRun.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        run_id: str,
        status: RunStatus,
        error_message: str | None = None,
    ) -> None:
        result = await self.session.execute(select(AnalysisRun).where(AnalysisRun.id == run_id))
        run = result.scalar_one_or_none()
        if run is None:
            return
        run.status = status
        if status == RunStatus.RUNNING:
            run.started_at = datetime.now(timezone.utc)
        elif status in (RunStatus.COMPLETED, RunStatus.FAILED):
            run.completed_at = datetime.now(timezone.utc)
        if error_message:
            run.error_message = error_message
        await self.session.commit()


class AnalysisRunSyncRepository:
    """Sync repository used inside CrewAI tool execution."""

    def __init__(self, session: Session):
        self.session = session

    def update_status(self, run_id: str, status: RunStatus, error_message: str | None = None) -> None:
        run = self.session.get(AnalysisRun, run_id)
        if run is None:
            return
        run.status = status
        if status == RunStatus.RUNNING:
            run.started_at = datetime.now(timezone.utc)
        elif status in (RunStatus.COMPLETED, RunStatus.FAILED):
            run.completed_at = datetime.now(timezone.utc)
        if error_message:
            run.error_message = error_message
        self.session.commit()

    def save_agent_output(self, run_id: str, agent_name: str, output_data: dict) -> None:
        output = AgentOutput(run_id=run_id, agent_name=agent_name, output_data=output_data)
        self.session.add(output)
        self.session.commit()
