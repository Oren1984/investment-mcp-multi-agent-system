import logging

import pytest

from telemetry.tracing import trace_block


def test_trace_block_executes_body():
    result = []
    with trace_block("test_op"):
        result.append(42)
    assert result == [42]


def test_trace_block_returns_control_after_yield():
    marker = {"done": False}
    with trace_block("control_flow"):
        pass
    marker["done"] = True
    assert marker["done"] is True


def test_trace_block_propagates_exceptions():
    with pytest.raises(ValueError, match="intentional"):
        with trace_block("failing_op"):
            raise ValueError("intentional failure")


def test_trace_block_logs_start_and_end(caplog):
    with caplog.at_level(logging.DEBUG, logger="telemetry.tracing"):
        with trace_block("my_operation"):
            pass

    messages = [r.message for r in caplog.records]
    assert any("my_operation" in m and "START" in m for m in messages)
    assert any("my_operation" in m and "END" in m for m in messages)


def test_trace_block_logs_duration(caplog):
    with caplog.at_level(logging.DEBUG, logger="telemetry.tracing"):
        with trace_block("timed_op"):
            pass

    end_messages = [r.message for r in caplog.records if "END" in r.message]
    assert any("duration" in m for m in end_messages)
