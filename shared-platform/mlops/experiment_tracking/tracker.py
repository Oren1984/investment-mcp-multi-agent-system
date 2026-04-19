"""
Minimal experiment tracker abstraction.

This is intentionally lightweight and template-friendly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExperimentRun:
    run_name: str
    parameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)


class ExperimentTracker:
    def start_run(self, run_name: str) -> ExperimentRun:
        return ExperimentRun(run_name=run_name)

    def log_param(self, run: ExperimentRun, key: str, value: Any) -> None:
        run.parameters[key] = value

    def log_metric(self, run: ExperimentRun, key: str, value: float) -> None:
        run.metrics[key] = value

    def log_artifact(self, run: ExperimentRun, artifact_path: str) -> None:
        run.artifacts.append(artifact_path)