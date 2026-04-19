"""
Timeout execution helper.

Template note:
This is a thread-based timeout wrapper, meant as a simple shared utility.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Callable, TypeVar

T = TypeVar("T")


class OperationTimeoutError(Exception):
    """Raised when an operation exceeds the configured timeout."""


def run_with_timeout(func: Callable[[], T], timeout_seconds: float) -> T:
    """
    Run a callable and fail if it exceeds timeout_seconds.
    """
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func)
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeoutError as exc:
            raise OperationTimeoutError(
                f"Operation exceeded timeout of {timeout_seconds} seconds."
            ) from exc