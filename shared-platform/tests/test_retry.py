import pytest

from resilience.retry import retry, retry_call


def test_retry_decorator_eventually_succeeds():
    state = {"count": 0}

    @retry(attempts=3, delay=0)
    def flaky():
        state["count"] += 1
        if state["count"] < 2:
            raise ValueError("temporary failure")
        return "ok"

    assert flaky() == "ok"
    assert state["count"] == 2


def test_retry_decorator_raises_after_exhausting_attempts():
    @retry(attempts=2, delay=0)
    def always_fails():
        raise RuntimeError("permanent failure")

    with pytest.raises(RuntimeError, match="permanent failure"):
        always_fails()


def test_retry_decorator_succeeds_on_first_try():
    @retry(attempts=3, delay=0)
    def reliable():
        return "success"

    assert reliable() == "success"


def test_retry_call_eventually_succeeds():
    state = {"count": 0}

    def flaky():
        state["count"] += 1
        if state["count"] < 2:
            raise ValueError("temporary")
        return "done"

    result = retry_call(flaky, attempts=3, delay=0)
    assert result == "done"
    assert state["count"] == 2


def test_retry_call_raises_after_exhausting():
    def always_fails():
        raise OSError("connection refused")

    with pytest.raises(OSError):
        retry_call(always_fails, attempts=2, delay=0)


def test_retry_only_catches_specified_exceptions():
    @retry(attempts=3, delay=0, exceptions=(ValueError,))
    def raises_key_error():
        raise KeyError("unexpected")

    with pytest.raises(KeyError):
        raises_key_error()
