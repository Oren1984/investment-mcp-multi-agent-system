import time

import pytest

from resilience.timeout import OperationTimeoutError, run_with_timeout


def test_run_with_timeout_returns_value():
    result = run_with_timeout(lambda: 42, timeout_seconds=5.0)
    assert result == 42


def test_run_with_timeout_returns_string():
    result = run_with_timeout(lambda: "hello", timeout_seconds=2.0)
    assert result == "hello"


def test_run_with_timeout_raises_on_slow_operation():
    with pytest.raises(OperationTimeoutError):
        run_with_timeout(lambda: time.sleep(10), timeout_seconds=0.05)


def test_run_with_timeout_lets_fast_operation_complete():
    result = run_with_timeout(lambda: sum(range(100)), timeout_seconds=5.0)
    assert result == 4950


def test_operation_timeout_error_is_exception():
    assert issubclass(OperationTimeoutError, Exception)
