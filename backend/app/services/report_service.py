from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models.report import Report
from app.db.repositories.report_repo import ReportSyncRepository

logger = get_logger(__name__)


class ReportService:
    def __init__(self, session: Session):
        self.repo = ReportSyncRepository(session)

    def save(self, run_id: str, ticker: str, content: str, structured: dict | None = None) -> Report:
        logger.info("Saving report", extra={"run_id": run_id, "ticker": ticker})
        return self.repo.create(
            run_id=run_id,
            ticker=ticker,
            content=content,
            structured=structured or {},
        )

    def parse_structured(self, report_content: str, ticker: str) -> dict:
        sections = {
            "ticker": ticker,
            "executive_summary": "",
            "fundamentals": "",
            "technical_analysis": "",
            "sector_context": "",
            "risk_profile": "",
            "recommendation": "",
        }

        current_section = None
        lines = report_content.split("\n")

        section_map = {
            "executive summary": "executive_summary",
            "fundamental": "fundamentals",
            "technical": "technical_analysis",
            "sector": "sector_context",
            "risk": "risk_profile",
            "recommendation": "recommendation",
        }

        buffer = []
        for line in lines:
            lower = line.lower().strip()
            matched = False
            for key, field in section_map.items():
                if key in lower and line.startswith("#"):
                    if current_section and buffer:
                        sections[current_section] = "\n".join(buffer).strip()
                        buffer = []
                    current_section = field
                    matched = True
                    break
            if not matched and current_section:
                buffer.append(line)

        if current_section and buffer:
            sections[current_section] = "\n".join(buffer).strip()

        return sections
