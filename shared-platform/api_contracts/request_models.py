from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class QueryRequest:
    query: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TaskRequest:
    task: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class GenericResponse:
    success: bool
    message: str
    payload: Optional[Dict[str, Any]] = None