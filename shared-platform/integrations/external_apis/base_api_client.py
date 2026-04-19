"""
Base external API client contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAPIClient(ABC):
    @abstractmethod
    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError