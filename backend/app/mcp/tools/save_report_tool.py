from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.db.models.analysis_run import RunStatus
from app.db.repositories.analysis_run_repo import AnalysisRunSyncRepository
from app.db.repositories.report_repo import ReportSyncRepository
from app.db.session import get_sync_session
from app.mcp.base_tool import MCPBaseTool
from app.services.report_service import ReportService
from app.utils.report_validator import validate_report_sections

logger = get_logger(__name__)


class SaveReportInput(BaseModel):
    run_id: str = Field(..., description="Analysis run UUID")
    ticker: str = Field(..., description="Ticker symbol")
    content: str = Field(..., description="Full markdown report content")
    structured: dict[str, Any] = Field(default_factory=dict, description="Parsed report sections")


class SaveReportTool(MCPBaseTool):
    name = "save_report"
    description = "Persist the final investment report to the database and mark the run as complete."
    input_schema = SaveReportInput

    def run(self, inputs: SaveReportInput) -> dict[str, Any]:
        from sqlalchemy.exc import IntegrityError
        from sqlalchemy import select
        from app.db.models.report import Report

        # Validate that the report contains all required sections before persisting
        is_valid, missing = validate_report_sections(inputs.content)
        if not is_valid:
            logger.warning(
                "Report is missing required sections — saving with validation warning",
                extra={"run_id": inputs.run_id, "missing_sections": missing},
            )
            # Annotate structured data so consumers can detect the degraded state
            inputs.structured = {**inputs.structured, "_validation_warnings": {"missing_sections": missing}}

        session = get_sync_session()
        try:
            # Check for existing report (idempotent — re-save if report already exists)
            existing = session.execute(select(Report).where(Report.run_id == inputs.run_id)).scalar_one_or_none()
            if existing:
                logger.info("Report already exists, updating", extra={"run_id": inputs.run_id})
                existing.content = inputs.content
                existing.structured = inputs.structured
                session.commit()
                report = existing
            else:
                report_svc = ReportService(session)
                report = report_svc.save(
                    run_id=inputs.run_id,
                    ticker=inputs.ticker,
                    content=inputs.content,
                    structured=inputs.structured,
                )

            run_repo = AnalysisRunSyncRepository(session)
            run_repo.update_status(inputs.run_id, RunStatus.COMPLETED)

            logger.info("Report saved", extra={"run_id": inputs.run_id, "ticker": inputs.ticker})
            return {"report_id": report.id, "run_id": inputs.run_id, "status": "COMPLETED"}
        except IntegrityError as e:
            session.rollback()
            logger.exception("IntegrityError saving report", extra={"run_id": inputs.run_id})
            raise
        finally:
            session.close()
