from __future__ import annotations

import anthropic

from app.core.config import settings
from app.core.errors import ExternalAPIError
from app.core.logging import get_logger

logger = get_logger(__name__)

_PLACEHOLDER_PREFIXES = ("sk-ant-your", "your-key", "your_key", "placeholder", "changeme")


def is_placeholder_key(key: str) -> bool:
    """Return True if the key is empty or a known placeholder value."""
    if not key or not key.strip():
        return True
    lower = key.strip().lower()
    return any(lower.startswith(p) or p in lower for p in _PLACEHOLDER_PREFIXES)


def is_demo_mode() -> bool:
    """Return True if the system should run in demo mode (no real LLM calls)."""
    return settings.demo_mode or is_placeholder_key(settings.anthropic_api_key)


class LLMService:
    def __init__(self):
        self._client: anthropic.Anthropic | None = None

    @property
    def client(self) -> anthropic.Anthropic:
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    def complete(self, system_prompt: str, user_message: str, max_tokens: int = 2048) -> str:
        try:
            message = self.client.messages.create(
                model=settings.anthropic_model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return message.content[0].text
        except anthropic.APIError as e:
            logger.exception("llm_service error")
            raise ExternalAPIError(f"LLM completion failed: {e}") from e

    def get_crewai_llm(self):
        from crewai import LLM
        return LLM(
            model=f"anthropic/{settings.anthropic_model}",
            api_key=settings.anthropic_api_key,
        )
