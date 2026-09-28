import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from qdrant_edge.models import (
    KnowledgeEntry,
    ConflictRecord,
    SyncDelta,
    SyncResponse,
)
from .config import cloud_settings
from .central_store import CentralStore
from .conflict_engine import ConflictEngine
from .sync_handler import SyncHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("cloud_api")

app = FastAPI(
    title="PlantMind Central Cloud API",
    description="Central office AI platform coordinating Qdrant Server, conflict resolution, and edge synchronization",
    version="1.0.0",
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

central_store = CentralStore()
conflict_engine = ConflictEngine()
sync_handler = SyncHandler(central_store, conflict_engine)


class ConflictResolveRequest(BaseModel):
    resolution_type: str  # winner_picked | merged | both_annotated
    winner_version_index: Optional[int] = 0
    merged_title: Optional[str] = None
    merged_body: Optional[str] = None
    merged_tags: Optional[List[str]] = None
    resolution_note: str = ""
    resolved_by: str = "Knowledge Manager"


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cloud-api",
        "target": "central-office",
        "qdrant": cloud_settings.qdrant_url or "embedded-central",
        "groq_configured": bool(cloud_settings.groq_api_key),
    }


@app.get("/api/stats")
def get_stats():
    return central_store.get_cloud_stats()


@app.get("/api/entries", response_model=List[KnowledgeEntry])
def list_entries(
    machine_id: Optional[str] = Query(None),
    entry_type: Optional[str] = Query(None),
    sync_status: Optional[str] = Query(None),
    limit: int = Query(100),
):
    return central_store.list_entries(
        machine_id=machine_id,
        entry_type=entry_type,
        sync_status=sync_status,
        limit=limit,
    )


@app.get("/api/entries/{entry_id}", response_model=KnowledgeEntry)
def get_entry(entry_id: str):
    entry = central_store.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@app.post("/api/entries", response_model=KnowledgeEntry)
def create_or_update_entry(entry: KnowledgeEntry):
    return central_store.upsert_entry(entry)


@app.get("/api/search", response_model=List[KnowledgeEntry])
def search_entries(
    q: str = Query(..., description="Semantic search query"),
    machine_id: Optional[str] = Query(None),
    area_tag: Optional[str] = Query(None),
    entry_type: Optional[str] = Query(None),
    limit: int = Query(10),
):
    return central_store.search_central(
        query=q,
        machine_id=machine_id,
        area_tag=area_tag,
        entry_type=entry_type,
        limit=limit,
    )


@app.post("/api/sync/delta", response_model=SyncResponse)
def sync_delta(delta: SyncDelta):
    """
    Sync endpoint invoked by edge kiosks when connectivity is available.
    Processes pushed entries, detects conflicts, and returns server updates.
    """
    try:
        return sync_handler.process_sync(delta)
    except Exception as e:
        logger.error(f"Sync error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conflicts", response_model=List[ConflictRecord])
def list_conflicts(status: Optional[str] = Query("open")):
    return central_store.list_conflicts(status=status)


@app.get("/api/conflicts/{conflict_id}", response_model=ConflictRecord)
def get_conflict(conflict_id: str):
    record = central_store.get_conflict(conflict_id)
    if not record:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return record


@app.post("/api/conflicts/{conflict_id}/resolve", response_model=ConflictRecord)
def resolve_conflict(conflict_id: str, req: ConflictResolveRequest):
    record = central_store.resolve_conflict(
        conflict_id=conflict_id,
        resolution_type=req.resolution_type,
        winner_version_index=req.winner_version_index,
        merged_title=req.merged_title,
        merged_body=req.merged_body,
        merged_tags=req.merged_tags,
        resolution_note=req.resolution_note,
        resolved_by=req.resolved_by,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Conflict record not found")
    return record


@app.post("/api/conflicts/{conflict_id}/reason")
def rerun_conflict_reasoning(conflict_id: str):
    """Rerun Groq LLaMA reasoning on a specific conflict."""
    record = central_store.get_conflict(conflict_id)
    if not record or len(record.competing_versions) < 2:
        raise HTTPException(status_code=404, detail="Conflict or competing versions not found")

    v_a = record.competing_versions[0]
    v_b = record.competing_versions[1]

    dummy_a = KnowledgeEntry(
        id=record.entry_id,
        type=record.entity_type,
        title=v_a.get("title", ""),
        body=v_a.get("body", ""),
        machine_id=record.machine_id,
        area_tag=record.area_tag,
        created_by=v_a.get("created_by", ""),
        device_id=v_a.get("device_id", ""),
        version=v_a.get("version", 1),
        tags=v_a.get("tags", []),
    )
    dummy_b = KnowledgeEntry(
        id=record.entry_id,
        type=record.entity_type,
        title=v_b.get("title", ""),
        body=v_b.get("body", ""),
        machine_id=record.machine_id,
        area_tag=record.area_tag,
        created_by=v_b.get("created_by", ""),
        device_id=v_b.get("device_id", ""),
        version=v_b.get("version", 2),
        tags=v_b.get("tags", []),
    )

    new_summary = conflict_engine.generate_conflict_summary(dummy_a, dummy_b)
    record.ai_summary = new_summary
    central_store.add_conflict(record)
    return {"conflict_id": conflict_id, "ai_summary": new_summary}


@app.get("/api/sync/sessions")
def list_sync_sessions(limit: int = Query(20)):
    return central_store.get_sync_sessions(limit=limit)


@app.get("/api/activity")
def get_activity_feed(limit: int = Query(50)):
    return central_store.get_activity_log(limit=limit)


@app.get("/api/devices")
def get_devices():
    return central_store.get_devices()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("cloud_api.main:app", host=cloud_settings.host, port=cloud_settings.port, reload=True)
