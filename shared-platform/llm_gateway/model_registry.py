from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ModelConfig:
    provider: str
    model_name: str
    supports_tools: bool = False
    supports_json_mode: bool = False
    supports_vision: bool = False


class ModelRegistry:
    """
    Minimal registry used by templates to keep provider/model
    selection out of business logic.
    """

    def __init__(self) -> None:
        self._models: Dict[str, ModelConfig] = {}

    def register(self, alias: str, config: ModelConfig) -> None:
        self._models[alias] = config

    def get(self, alias: str) -> Optional[ModelConfig]:
        return self._models.get(alias)

    def require(self, alias: str) -> ModelConfig:
        config = self.get(alias)
        if config is None:
            raise KeyError(f"Model alias '{alias}' is not registered.")
        return config