from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ShortTermMemory:
    messages: List[str] = field(default_factory=list)

    def add(self, item: str) -> None:
        self.messages.append(item)

    def recent(self, limit: int = 10) -> List[str]:
        return self.messages[-limit:]


@dataclass
class LongTermMemory:
    facts: Dict[str, str] = field(default_factory=dict)

    def remember(self, key: str, value: str) -> None:
        self.facts[key] = value

    def recall(self, key: str) -> str | None:
        return self.facts.get(key)