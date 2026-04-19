from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ApprovalRequest:
    action_name: str
    reason: str
    payload: Dict[str, Any]
    risk_level: str = "medium"


@dataclass
class ApprovalDecision:
    approved: bool
    reviewer: str = "system"
    note: str = ""