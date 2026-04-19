"""Unit tests for config loading and defaults."""
import os
import pytest
from unittest.mock import patch


class TestSettings:
    def test_default_app_name(self):
        from app.core.config import Settings
        s = Settings()
        assert s.app_name == "investment-mcp-system"

    def test_default_period(self):
        from app.core.config import Settings
        s = Settings()
        assert s.default_analysis_period == "1y"

    def test_debug_default_true_in_development(self):
        from app.core.config import Settings
        s = Settings(_env_file=None)
        assert s.debug is True

    def test_env_override(self):
        from app.core.config import Settings
        with patch.dict(os.environ, {"APP_ENV": "production", "DEBUG": "false"}):
            s = Settings(_env_file=None)
            assert s.app_env == "production"
            assert s.debug is False

    def test_anthropic_model_default(self):
        from app.core.config import Settings
        s = Settings()
        assert "claude" in s.anthropic_model

    def test_max_concurrent_runs_positive(self):
        from app.core.config import Settings
        s = Settings()
        assert s.max_concurrent_runs > 0


class TestErrors:
    def test_app_error_has_status_code(self):
        from app.core.errors import AppError, NotFoundError, ValidationError

        e = NotFoundError("test")
        assert e.status_code == 404
        assert "test" in str(e)

        e2 = ValidationError("bad input")
        assert e2.status_code == 422

    def test_tool_not_found_error(self):
        from app.core.errors import ToolNotFoundError

        e = ToolNotFoundError("my_tool")
        assert "my_tool" in str(e)
        assert e.status_code == 404

    def test_tool_execution_error(self):
        from app.core.errors import ToolExecutionError

        e = ToolExecutionError("get_price", "timeout")
        assert "get_price" in str(e)
        assert "timeout" in str(e)
        assert e.status_code == 500
