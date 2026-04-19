"""
Shared document schema example for RAG and knowledge systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentRecord:
    document_id: str
    content: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)