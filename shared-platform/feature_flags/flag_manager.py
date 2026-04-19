"""
Minimal feature flag manager.

For template usage, flags are read from environment variables.
"""

from __future__ import annotations

import os


class FeatureFlagManager:
    @staticmethod
    def is_enabled(flag_name: str, default: bool = False) -> bool:
        raw_value = os.getenv(flag_name)

        if raw_value is None:
            return default

        return raw_value.strip().lower() in {"1", "true", "yes", "on"}