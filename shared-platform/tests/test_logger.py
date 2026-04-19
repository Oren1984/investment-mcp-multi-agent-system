import logging

import pytest

from app_logging.logger import get_logger


def test_get_logger_returns_logger_instance(sample_env):
    logger = get_logger("test.module")
    assert isinstance(logger, logging.Logger)


def test_get_logger_uses_correct_name(sample_env):
    logger = get_logger("my.service.name")
    assert logger.name == "my.service.name"


def test_get_logger_different_names_are_independent(sample_env):
    logger_a = get_logger("service.a")
    logger_b = get_logger("service.b")
    assert logger_a is not logger_b
    assert logger_a.name != logger_b.name


def test_logger_emits_info_message(caplog, sample_env):
    logger = get_logger("test.emit")
    with caplog.at_level(logging.INFO, logger="test.emit"):
        logger.info("hello from logger test")
    assert "hello from logger test" in caplog.text


def test_logger_does_not_emit_below_set_level(caplog, monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("LOG_FILE", "logs/test.log")
    logger = get_logger("test.level_filter")
    with caplog.at_level(logging.DEBUG, logger="test.level_filter"):
        logger.debug("this should not appear")
    assert "this should not appear" not in caplog.text
