from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    role: str
    content: str


@dataclass
class GenerationRequest:
    messages: List[Message]
    model: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class GenerationResponse:
    content: str
    provider: str
    model: str
    raw: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """
    Shared interface for all LLM providers.

    Concrete adapters may wrap OpenAI, Anthropic, Gemini,
    local models, or self-hosted inference endpoints.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError