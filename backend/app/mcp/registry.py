from __future__ import annotations

from app.mcp.base_tool import MCPBaseTool
from app.core.errors import ToolNotFoundError


class MCPRegistry:
    def __init__(self):
        self._tools: dict[str, MCPBaseTool] = {}

    def register(self, tool: MCPBaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> MCPBaseTool:
        tool = self._tools.get(name)
        if tool is None:
            raise ToolNotFoundError(name)
        return tool

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())
