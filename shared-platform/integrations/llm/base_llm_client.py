"""
Base LLM client contract.

Implementations should subclass BaseLLMClient and override generate().
The message format follows the OpenAI chat-completion convention, which is
supported by Anthropic, Google Gemini, and most modern LLM providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMClient(ABC):
    @abstractmethod
    def generate(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
        """
        Generate a text response from a list of chat messages.

        Args:
            messages: Ordered list of message dicts, each with at minimum:
                      {"role": "user" | "assistant" | "system", "content": str}
            **kwargs: Provider-specific options such as temperature, max_tokens,
                      stop sequences, or tool definitions.

        Returns:
            The model's response as a plain string.

        Raises:
            NotImplementedError: If the subclass has not implemented this method.
        """
        raise NotImplementedError
