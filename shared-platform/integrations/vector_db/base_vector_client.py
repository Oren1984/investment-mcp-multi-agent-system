"""
Base vector database client contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseVectorDBClient(ABC):
    @abstractmethod
    def upsert(self, items: list[dict[str, Any]]) -> None:
        """
        Store or update vector items.
        """
        raise NotImplementedError

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        """
        Perform vector similarity search.
        """
        raise NotImplementedError