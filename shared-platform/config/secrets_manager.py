"""
Minimal secret access layer for shared platform usage.

Purpose:
- Provide a single place to read secrets from environment variables
- Keep business code away from direct os.getenv calls
- Allow future replacement with Vault / AWS Secrets Manager / Azure Key Vault
"""

from __future__ import annotations

import os
from typing import Optional


class SecretNotFoundError(Exception):
    """Raised when a required secret is missing."""


class SecretsManager:
    """Simple environment-based secret manager."""

    @staticmethod
    def get_secret(name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
        value = os.getenv(name, default)

        if required and not value:
            raise SecretNotFoundError(f"Required secret '{name}' was not found.")

        return value