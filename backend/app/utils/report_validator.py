from __future__ import annotations

REQUIRED_SECTIONS = [
    "Executive Summary",
    "Fundamental Analysis",
    "Technical Analysis",
    "Sector Analysis",
    "Risk Assessment",
    "Recommendation",
]


def validate_report_sections(content: str) -> tuple[bool, list[str]]:
    """Return (is_valid, missing_sections).

    Checks that every required section header appears in the report content.
    Uses case-insensitive matching so minor LLM formatting variations pass.
    """
    content_lower = content.lower()
    missing = [s for s in REQUIRED_SECTIONS if s.lower() not in content_lower]
    return (len(missing) == 0, missing)
