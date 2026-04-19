"""
Base evaluator contract for shared usage across system types.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseEvaluator(ABC):
    @abstractmethod
    def evaluate(self, predictions: list[Any], references: list[Any]) -> dict[str, float]:
        """
        Return evaluation metrics in a flat dictionary.
        """
        raise NotImplementedError