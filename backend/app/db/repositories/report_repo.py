from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db.models.report import Report


class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_run_id(self, run_id: str) -> Report | None:
        result = await self.session.execute(select(Report).where(Report.run_id == run_id))
        return result.scalar_one_or_none()

    async def list_by_ticker(self, ticker: str, limit: int = 10) -> list[Report]:
        result = await self.session.execute(
            select(Report)
            .where(Report.ticker_symbol == ticker.upper())
            .order_by(Report.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class ReportSyncRepository:
    """Sync repository used inside CrewAI tool execution."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, run_id: str, ticker: str, content: str, structured: dict) -> Report:
        report = Report(
            run_id=run_id,
            ticker_symbol=ticker.upper(),
            content=content,
            structured=structured,
        )
        self.session.add(report)
        self.session.commit()
        self.session.refresh(report)
        return report
