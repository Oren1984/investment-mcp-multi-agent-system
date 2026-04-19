from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PlanStep:
    step_id: str
    description: str
    tool_name: str | None = None


@dataclass
class ExecutionPlan:
    goal: str
    steps: List[PlanStep] = field(default_factory=list)


class Planner:
    """
    Minimal planning placeholder for the agent template.
    This is intentionally lightweight and framework-agnostic.
    """

    def build_plan(self, goal: str) -> ExecutionPlan:
        return ExecutionPlan(
            goal=goal,
            steps=[
                PlanStep(step_id="1", description="Understand the goal"),
                PlanStep(step_id="2", description="Choose the next best action"),
                PlanStep(step_id="3", description="Execute or request approval if needed"),
            ],
        )