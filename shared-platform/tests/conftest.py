"""
Shared test fixtures for shared-platform.

Fixtures are available to all test files without explicit import.
"""

import pytest


@pytest.fixture
def sample_env(monkeypatch):
    """Set a minimal, predictable environment for settings-dependent tests."""
    monkeypatch.setenv("APP_NAME", "test-app")
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOG_FILE", "logs/test.log")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("RETRY_ATTEMPTS", "3")
    monkeypatch.setenv("RETRY_DELAY", "0")
    monkeypatch.setenv("API_TIMEOUT", "10")
    monkeypatch.setenv("ENABLE_VALIDATION", "true")
    monkeypatch.setenv("ENABLE_RETRY", "true")
