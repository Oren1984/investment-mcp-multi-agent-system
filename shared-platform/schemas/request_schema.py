"""
Shared request schema example.

Use these schemas to keep API, agents, RAG, and UI aligned.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BaseRequest:
    request_id: str
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)