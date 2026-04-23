from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.api.routes.health import router as health_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.sources import router as sources_router

api_router = APIRouter()
# Health/ready/metrics remain public
api_router.include_router(health_router)
# Sources status is informational — public, no auth needed
api_router.include_router(sources_router)
# All analysis routes require API key when API_KEY env var is set
api_router.include_router(analysis_router, dependencies=[Depends(require_api_key)])
