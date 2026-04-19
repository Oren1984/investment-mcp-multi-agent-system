from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.limiter import limiter
from app.api.middleware import CorrelationIDMiddleware
from app.api.routes import api_router
from app.core.config import settings
from app.core.errors import AppError, app_error_handler, generic_error_handler
from app.core.logging import get_logger, setup_logging
from app.db.init_db import init_db_async
from app.mcp.gateway import create_gateway

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(level=settings.log_level, fmt=settings.log_format)
    logger.info("Starting up Investment MCP System", extra={"env": settings.app_env})

    await init_db_async()

    import app.mcp.gateway as gw_module
    gw_module._gateway_instance = create_gateway()
    logger.info("MCP Gateway initialized", extra={"tools": gw_module._gateway_instance.list_tools()})

    from app.services.llm_service import is_demo_mode, is_placeholder_key
    if is_placeholder_key(settings.anthropic_api_key):
        logger.warning(
            "ANTHROPIC_API_KEY is not set or is a placeholder value. "
            "Real LLM analysis will fail with a 401 authentication error. "
            "Set a valid key in .env to enable live analysis. "
            "Running in DEMO MODE — analysis runs will return synthetic reports.",
        )
    elif settings.demo_mode:
        logger.warning(
            "DEMO_MODE=true is set. Analysis runs will return synthetic reports "
            "without calling the Anthropic API.",
        )

    yield

    logger.info("Shutting down")
    from app.api.routes.analysis import shutdown_executor
    shutdown_executor()

    from app.db.session import async_engine, sync_engine
    await async_engine.dispose()
    sync_engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Investment MCP Multi-Agent System",
        description="AI-powered investment analysis via multi-agent orchestration",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(CorrelationIDMiddleware)

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    return app


app = create_app()
