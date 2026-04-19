import os

from sqlalchemy import text

from app.core.logging import get_logger
from app.db.base import Base
from app.db.session import async_engine, sync_engine

logger = get_logger(__name__)

_USE_ALEMBIC = os.environ.get("USE_ALEMBIC", "false").lower() == "true"


def init_db_sync() -> None:
    """Create/migrate DB tables.

    Production: set USE_ALEMBIC=true — runs `alembic upgrade head`.
    Development default: falls back to SQLAlchemy create_all (safe for fresh DBs only).
    """
    from app.db.models import analysis_run, agent_output, report, ticker  # noqa: F401

    if _USE_ALEMBIC:
        _run_alembic_upgrade()
        return

    with sync_engine.connect() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(bind=sync_engine)
    logger.info("Database tables created (create_all)")


async def init_db_async() -> None:
    """Async variant used by the FastAPI lifespan.

    Delegates to the sync path inside a thread to avoid blocking the event loop.
    """
    import asyncio

    from app.db.models import analysis_run, agent_output, report, ticker  # noqa: F401

    if _USE_ALEMBIC:
        await asyncio.get_event_loop().run_in_executor(None, _run_alembic_upgrade)
        return

    async with async_engine.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        except Exception:
            logger.warning("pgvector extension not available — vector search disabled")
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created (create_all async)")


def _run_alembic_upgrade() -> None:
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Alembic migrations applied (upgrade head)")
