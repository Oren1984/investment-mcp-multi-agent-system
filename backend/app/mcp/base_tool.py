from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Type

from pydantic import BaseModel


class MCPToolResult(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


class MCPBaseTool(ABC):
    name: str
    description: str
    input_schema: Type[BaseModel]

    def validate_input(self, payload: dict[str, Any]) -> BaseModel:
        return self.input_schema(**payload)

    def execute(self, payload: dict[str, Any]) -> MCPToolResult:
        try:
            validated = self.validate_input(payload)
            data = self.run(validated)
            return MCPToolResult(success=True, data=data)
        except Exception as e:
            return MCPToolResult(success=False, error=str(e))

    @abstractmethod
    def run(self, inputs: BaseModel) -> dict[str, Any]:
        raise NotImplementedError
