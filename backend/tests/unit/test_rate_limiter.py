"""Unit tests for rate limiter configuration."""
from __future__ import annotations

import pytest


class TestRateLimiterConfig:
    def test_limiter_is_configured(self):
        from app.api.limiter import limiter
        assert limiter is not None

    def test_rate_limit_setting_has_sensible_default(self):
        from app.core.config import Settings
        s = Settings()
        assert "/" in s.rate_limit_analyze  # e.g. "10/minute"
        parts = s.rate_limit_analyze.split("/")
        assert int(parts[0]) > 0, "Rate limit count must be positive"
        assert parts[1] in {"second", "minute", "hour", "day"}

    def test_limiter_key_func_is_remote_address(self):
        from app.api.limiter import limiter
        from slowapi.util import get_remote_address
        assert limiter._key_func is get_remote_address
