from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from backend.app.ingestion.sources import SourceEntry, SourceRegistry
from backend.app.worker import run_fxtwitter_once
router=APIRouter(tags=["sources"])
def registry(request: Request) -> SourceRegistry: return request.app.state.source_registry
class SourceInput(BaseModel):
    handle: str = Field(min_length=1, max_length=50); label: str = Field(min_length=1, max_length=100); category: str = Field(pattern="^(exchange|security|regulator|project)$"); trust: str = Field(pattern="^(high|medium)$")
class SourcePatch(BaseModel): enabled: bool
@router.get("/sources")
def list_sources(request: Request) -> dict[str, list[dict[str, object]]]: return {"items":[entry.as_json() for entry in registry(request).list()]}
@router.post("/sources", status_code=201)
def add_source(payload: SourceInput, request: Request) -> dict[str, object]:
    try: return registry(request).add(SourceEntry(**payload.model_dump())).as_json()
    except ValueError as error: raise HTTPException(status_code=409, detail=str(error)) from error
@router.patch("/sources/{handle}")
def patch_source(handle: str, payload: SourcePatch, request: Request) -> dict[str, object]:
    try: return registry(request).update(handle, payload.enabled).as_json()
    except KeyError as error: raise HTTPException(status_code=404, detail="source not found") from error

@router.post("/sources/scan")
def scan_sources(request: Request) -> dict[str, int]:
    """Run a manual, bounded scan of enabled FxTwitter sources."""
    processed = run_fxtwitter_once(request.app.state.event_pipeline, registry(request))
    return {"processed": len(processed)}
