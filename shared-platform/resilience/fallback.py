"""
Fallback helper for degraded execution flows.

Useful when a preferred provider fails and a secondary option should be used.
"""

from __future__ import annotations

from typing import Callable, TypeVar

T = TypeVar("T")


def run_with_fallback(primary: Callable[[], T], fallback: Callable[[], T]) -> T:
    """
    Try primary callable first. If it fails, run fallback callable.
    """
    try:
        return primary()
    except Exception:
        return fallback()