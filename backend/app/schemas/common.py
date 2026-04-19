from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"


class ReadyResponse(BaseModel):
    status: str
    db: str
    mcp_tools: list[str]


class ErrorResponse(BaseModel):
    detail: str
