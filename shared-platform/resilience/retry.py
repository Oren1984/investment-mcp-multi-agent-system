"""
Canonical retry utility for unstable operations such as:
- LLM API requests
- Vector database calls
- External HTTP services

Provides both a decorator form and a functional call form.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

T = TypeVar("T")


def retry(
    attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator that retries the wrapped function on transient failures.

    Args:
        attempts: Maximum number of tries (including the first attempt).
        delay: Seconds to wait between retries.
        exceptions: Exception types that trigger a retry.

    Example::

        @retry(attempts=3, delay=0.5)
        def call_llm(prompt: str) -> str:
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: Exception | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_error = exc
                    if attempt < attempts:
                        time.sleep(delay)
            raise last_error  # type: ignore[misc]

        return wrapper

    return decorator


def retry_call(
    func: Callable[[], T],
    attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """
    Functional-style retry — call a zero-argument callable with retry logic.

    Useful when you cannot use the decorator (e.g., inline lambdas).

    Args:
        func: A zero-argument callable to execute.
        attempts: Maximum number of tries.
        delay: Seconds to wait between retries.
        exceptions: Exception types that trigger a retry.

    Returns:
        The return value of func on success.

    Raises:
        The last caught exception after all attempts are exhausted.

    Example::

        result = retry_call(lambda: requests.get(url), attempts=3, delay=1.0)
    """
    return retry(attempts=attempts, delay=delay, exceptions=exceptions)(func)()
