"""
Minimal tracing context manager.

Emits structured log messages at DEBUG level.
Replace or wrap with OpenTelemetry, Arize Phoenix, or LangSmith when the
project requires distributed tracing or AI observability tooling.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from time import perf_counter
from typing import Iterator

logger = logging.getLogger(__name__)


@contextmanager
def trace_block(name: str) -> Iterator[None]:
    """
    Time and log a named code block.

    Args:
        name: A descriptive label for the operation being traced.

    Example::

        with trace_block("llm.generate"):
            response = llm.generate(messages)
    """
    start = perf_counter()
    logger.debug("[TRACE START] %s", name)
    try:
        yield
    finally:
        duration = perf_counter() - start
        logger.debug("[TRACE END] %s duration=%.4fs", name, duration)
