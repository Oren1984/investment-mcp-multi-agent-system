from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    detail = "Resource not found"


class ValidationError(AppError):
    status_code = 422
    detail = "Validation error"


class ExternalAPIError(AppError):
    status_code = 502
    detail = "External API error"


class ToolNotFoundError(AppError):
    status_code = 404

    def __init__(self, tool_name: str):
        super().__init__(f"Tool not found: {tool_name}")


class ToolExecutionError(AppError):
    status_code = 500

    def __init__(self, tool_name: str, reason: str):
        super().__init__(f"Tool '{tool_name}' execution failed: {reason}")


class AnalysisRunNotFoundError(NotFoundError):
    def __init__(self, run_id: str):
        super().__init__(f"Analysis run not found: {run_id}")


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Unexpected internal error"})
