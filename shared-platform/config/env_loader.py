"""
Minimal environment loading helper.

This file intentionally stays lightweight.
If python-dotenv is added later, this file is the correct place to integrate it.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_env_file(env_path: str = ".env") -> None:
    """
    Very small .env loader for template purposes.
    Reads KEY=VALUE lines and injects them into os.environ if not already set.
    """
    path = Path(env_path)

    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value