from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.db.session import get_async_session

__all__ = ["get_async_session", "require_api_key"]

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """Dependency that enforces API key auth when API_KEY is configured.

    If API_KEY is empty (default dev state), all requests pass through.
    If API_KEY is set, the X-API-Key header must match exactly.
    """
    if not settings.api_key:
        return  # Auth disabled — local/dev mode
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
