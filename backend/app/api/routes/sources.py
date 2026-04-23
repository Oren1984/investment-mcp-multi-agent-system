from __future__ import annotations

from fastapi import APIRouter

from app.services.source_registry import get_source_registry

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", summary="List all data sources with status and metadata")
async def list_sources() -> dict:
    registry = get_source_registry()
    return {
        "sources": registry.to_dict_list(),
        "summary": registry.summary(),
    }


@router.get("/status", summary="Source health summary")
async def sources_status() -> dict:
    registry = get_source_registry()
    return registry.summary()
