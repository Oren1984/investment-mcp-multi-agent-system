from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ApprovalResult:
    allowed: bool
    reason: str


class ApprovalGate:
    """
    Minimal approval gate for template use.
    Replace with UI approval, policy engine, or human review flow.
    """

    def evaluate(self, action_name: str, payload: Dict[str, Any], read_only: bool) -> ApprovalResult:
        if read_only:
            return ApprovalResult(allowed=True, reason="Read-only action auto-approved.")

        return ApprovalResult(
            allowed=False,
            reason=f"Action '{action_name}' requires explicit approval.",
        )