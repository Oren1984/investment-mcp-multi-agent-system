import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.limiter import limiter
from app.core.config import settings
from app.core.errors import AnalysisRunNotFoundError
from app.core.logging import get_logger, run_id_var
from app.crews.investment_crew import AnalysisConfig, InvestmentCrew
from app.db.models.analysis_run import RunStatus
from app.db.repositories import AnalysisRunRepository, ReportRepository
from app.db.session import get_async_session
from app.mcp.gateway import get_gateway
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatusResponse,
    HistoryItem,
    HistoryResponse,
    ReportResponse,
)

router = APIRouter(prefix="/analyze", tags=["analysis"])
logger = get_logger(__name__)
_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="crew_worker")


def _run_crew_sync(run_id: str, ticker: str, period: str, execution_mode: str) -> None:
    gateway = get_gateway()
    crew = InvestmentCrew(gateway=gateway)
    config = AnalysisConfig(
        ticker=ticker,
        run_id=run_id,
        period=period,
        execution_mode=execution_mode,
    )
    crew.run(config)


async def _run_crew_background(run_id: str, ticker: str, period: str, execution_mode: str) -> None:
    run_id_var.set(run_id)
    loop = asyncio.get_event_loop()
    ctx = copy_context()
    await loop.run_in_executor(
        _executor, ctx.run, _run_crew_sync, run_id, ticker, period, execution_mode
    )


def shutdown_executor() -> None:
    _executor.shutdown(wait=False)


@router.post("", response_model=AnalysisResponse, status_code=202)
@limiter.limit(settings.rate_limit_analyze)
async def create_analysis(
    request: Request,
    body: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
):
    repo = AnalysisRunRepository(db)
    run = await repo.create(
        ticker=body.ticker,
        config={"period": body.period, "execution_mode": body.execution_mode.value},
    )
    logger.info(
        "Analysis created",
        extra={"run_id": run.id, "ticker": run.ticker, "mode": body.execution_mode.value},
    )
    background_tasks.add_task(
        _run_crew_background, run.id, run.ticker, body.period, body.execution_mode.value
    )
    return AnalysisResponse(
        run_id=run.id,
        ticker=run.ticker,
        status=run.status.value,
        execution_mode=body.execution_mode.value,
        created_at=run.created_at,
    )


@router.get("/{run_id}/status", response_model=AnalysisStatusResponse)
async def get_status(run_id: str, db: AsyncSession = Depends(get_async_session)):
    repo = AnalysisRunRepository(db)
    run = await repo.get(run_id)
    if run is None:
        raise AnalysisRunNotFoundError(run_id)
    execution_mode = run.config.get("execution_mode") if run.config else None
    return AnalysisStatusResponse(
        run_id=run.id,
        ticker=run.ticker,
        status=run.status.value,
        execution_mode=execution_mode,
        created_at=run.created_at,
        started_at=run.started_at,
        completed_at=run.completed_at,
        error_message=run.error_message,
    )


@router.get("/{run_id}/report", response_model=ReportResponse)
async def get_report(run_id: str, db: AsyncSession = Depends(get_async_session)):
    run_repo = AnalysisRunRepository(db)
    run = await run_repo.get(run_id)
    if run is None:
        raise AnalysisRunNotFoundError(run_id)
    if run.status != RunStatus.COMPLETED:
        raise HTTPException(
            status_code=202,
            detail=f"Analysis is not complete yet. Current status: {run.status.value}",
        )
    report_repo = ReportRepository(db)
    report = await report_repo.get_by_run_id(run_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found for this run")
    execution_mode = run.config.get("execution_mode") if run.config else None
    return ReportResponse(
        report_id=report.id,
        run_id=report.run_id,
        ticker=report.ticker_symbol,
        content=report.content,
        structured=report.structured,
        execution_mode=execution_mode,
        created_at=report.created_at,
    )


@router.get("", response_model=HistoryResponse)
async def list_history(limit: int = 20, db: AsyncSession = Depends(get_async_session)):
    repo = AnalysisRunRepository(db)
    runs = await repo.list_recent(limit=limit)
    items = [
        HistoryItem(
            run_id=r.id,
            ticker=r.ticker,
            status=r.status.value,
            execution_mode=r.config.get("execution_mode") if r.config else None,
            created_at=r.created_at,
            completed_at=r.completed_at,
            has_report=(r.report is not None),
        )
        for r in runs
    ]
    return HistoryResponse(items=items, total=len(items))
