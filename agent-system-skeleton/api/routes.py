from __future__ import annotations


def health() -> dict:
    return {"status": "ok", "service": "agent-template"}


def submit_task(payload: dict) -> dict:
    """
    Thin placeholder route for agent task submission.
    Real planning/execution should live outside the API layer.
    """
    return {
        "message": "Agent task route placeholder",
        "received": payload,
    }