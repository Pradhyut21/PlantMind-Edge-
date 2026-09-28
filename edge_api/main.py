import os
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from qdrant_edge.models import (
    KnowledgeEntry,
    KnowledgeType,
    SyncStatus,
    DeviceMemoryStats,
)
from qdrant_edge.shard import EdgeShard
from .config import edge_settings
from .sync_client import EdgeSyncClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("edge_api")

app = FastAPI(
    title="PlantMind Edge Kiosk API",
    description="Offline-first on-device API running Qdrant Edge local shard and pending-write queue",
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

from fastapi.staticfiles import StaticFiles
if os.path.exists("presentation"):
    app.mount("/presentation", StaticFiles(directory="presentation", html=True), name="presentation")
if os.path.exists("brag-output"):
    app.mount("/brag", StaticFiles(directory="brag-output", html=True), name="brag")


# Active shard registry (supports multi-device demo switching)
active_shards: Dict[str, EdgeShard] = {}

def get_current_shard(device_id: Optional[str] = None) -> EdgeShard:
    dev_id = device_id or edge_settings.device_id
    if dev_id not in active_shards:
        path = edge_settings.get_device_storage_path(dev_id)
        active_shards[dev_id] = EdgeShard(storage_path=path, device_id=dev_id)
    return active_shards[dev_id]

sync_client = EdgeSyncClient(cloud_url=edge_settings.cloud_api_url)


class NetworkToggleRequest(BaseModel):
    is_offline: bool


class DeviceSwitchRequest(BaseModel):
    device_id: str


class EntryCreateRequest(BaseModel):
    type: KnowledgeType = KnowledgeType.TRIBAL_NOTE
    title: str
    body: str
    machine_id: str = "PRESS-03"
    area_tag: str = "Stamping Line 3"
    created_by: str = "Tech-Dave (Senior)"
    tags: List[str] = []
    keep_local_until_reviewed: bool = False


@app.get("/health")
def health_check(device_id: Optional[str] = Query(None)):
    shard = get_current_shard(device_id)
    state = shard.get_state()
    return {
        "status": "healthy",
        "service": "edge-api",
        "device_id": shard.device_id,
        "is_offline_simulation": state.get("is_offline_simulation", False),
        "storage_path": shard.storage_path,
    }


@app.get("/api/status")
def get_edge_status(device_id: Optional[str] = Query(None)):
    shard = get_current_shard(device_id)
    state = shard.get_state()
    return {
        "device_id": shard.device_id,
        "is_offline_simulation": state.get("is_offline_simulation", False),
        "last_sync_time": state.get("last_sync_time"),
        "pending_queue_count": len(shard.get_pending_writes()),
        "cloud_api_url": edge_settings.cloud_api_url,
    }


@app.post("/api/network/toggle")
def toggle_network(req: NetworkToggleRequest, device_id: Optional[str] = Query(None)):
    """
    Toggle simulated offline / airplane mode on the kiosk.
    When set to True, all network calls to cloud are blocked immediately.
    """
    shard = get_current_shard(device_id)
    shard.update_state({"is_offline_simulation": req.is_offline})
    status_str = "OFFLINE (Airplane Mode Enabled)" if req.is_offline else "ONLINE (Connected to Plant LAN)"
    shard.log_activity(
        event_type="network_toggle",
        title=f"Network Status Changed: {status_str}",
        description=f"Technician switched kiosk network mode to {status_str}",
        metadata={"is_offline": req.is_offline},
    )
    return {"device_id": shard.device_id, "is_offline": req.is_offline, "status": status_str}


@app.post("/api/device/switch")
def switch_device(req: DeviceSwitchRequest):
    """Switch active simulated device (e.g. kiosk-1, kiosk-2, kiosk-3)."""
    edge_settings.device_id = req.device_id
    shard = get_current_shard(req.device_id)
    return {
        "active_device_id": shard.device_id,
        "storage_path": shard.storage_path,
    }


@app.get("/api/search", response_model=List[KnowledgeEntry])
def search_local(
    q: str = Query(..., description="Technician spoken or typed symptom/query"),
    machine_id: Optional[str] = Query(None),
    area_tag: Optional[str] = Query(None),
    entry_type: Optional[str] = Query(None),
    limit: int = Query(10),
    device_id: Optional[str] = Query(None),
):
    """
    100% Offline Semantic Search on Qdrant EdgeShard.
    Works with network completely severed; executes in <200ms.
    """
    import time
    start = time.time()
    shard = get_current_shard(device_id)
    results = shard.search(
        query=q,
        machine_id=machine_id,
        area_tag=area_tag,
        entry_type=entry_type,
        limit=limit,
    )
    elapsed_ms = round((time.time() - start) * 1000, 2)
    logger.info(f"Offline search for '{q}' took {elapsed_ms}ms, returned {len(results)} results")
    return results


@app.get("/api/entries", response_model=List[KnowledgeEntry])
def list_entries(
    machine_id: Optional[str] = Query(None),
    entry_type: Optional[str] = Query(None),
    sync_status: Optional[str] = Query(None),
    limit: int = Query(100),
    device_id: Optional[str] = Query(None),
):
    shard = get_current_shard(device_id)
    return shard.list_entries(
        machine_id=machine_id,
        entry_type=entry_type,
        sync_status=sync_status,
        limit=limit,
    )


@app.get("/api/entries/{entry_id}", response_model=KnowledgeEntry)
def get_entry(entry_id: str, device_id: Optional[str] = Query(None)):
    shard = get_current_shard(device_id)
    entry = shard.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found in local EdgeShard")
    return entry


@app.post("/api/entries", response_model=KnowledgeEntry)
def create_local_entry(req: EntryCreateRequest, device_id: Optional[str] = Query(None)):
    """
    Technician writes an incident log or tribal knowledge note offline.
    Appends to local EdgeShard and queues in pending_write_queue.json.
    """
    shard = get_current_shard(device_id)
    entry = KnowledgeEntry(
        type=req.type,
        title=req.title,
        body=req.body,
        machine_id=req.machine_id,
        area_tag=req.area_tag,
        created_by=req.created_by,
        device_id=shard.device_id,
        version=1,
        keep_local_until_reviewed=req.keep_local_until_reviewed,
        tags=req.tags,
    )
    return shard.add_entry(entry)


@app.get("/api/memory/inspect", response_model=DeviceMemoryStats)
def inspect_device_memory(device_id: Optional[str] = Query(None)):
    """
    Device Memory Inspector:
    Reports local entry counts, local_only vs synced vs conflict, disk usage,
    and HNSW vector metrics.
    """
    shard = get_current_shard(device_id)
    return shard.get_memory_stats()


@app.post("/api/sync/trigger")
async def trigger_sync(device_id: Optional[str] = Query(None)):
    """Manually or automatically trigger sync with central cloud."""
    shard = get_current_shard(device_id)
    return await sync_client.sync(shard)


@app.get("/api/activity")
def get_activity(limit: int = Query(50), device_id: Optional[str] = Query(None)):
    shard = get_current_shard(device_id)
    return shard.get_activity_log(limit=limit)


@app.post("/api/policy/toggle_local")
def toggle_keep_local(entry_id: str = Body(..., embed=True), device_id: Optional[str] = Query(None)):
    """Toggle the 'keep local until reviewed' data policy on an entry."""
    shard = get_current_shard(device_id)
    entry = shard.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    new_val = not entry.keep_local_until_reviewed
    entry.keep_local_until_reviewed = new_val
    if new_val:
        entry.sync_status = SyncStatus.LOCAL_ONLY
    else:
        entry.sync_status = SyncStatus.PENDING_SYNC

    shard.client.set_payload(
        collection_name="plantmind_knowledge",
        payload={
            "keep_local_until_reviewed": new_val,
            "sync_status": entry.sync_status.value,
        },
        points=[entry_id],
    )
    # Also update in queue
    queue = shard._read_queue()
    for item in queue:
        if item.get("id") == entry_id:
            item["keep_local_until_reviewed"] = new_val
            item["sync_status"] = entry.sync_status.value
    shard._write_queue(queue)

    return {
        "entry_id": entry_id,
        "keep_local_until_reviewed": new_val,
        "sync_status": entry.sync_status.value,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("edge_api.main:app", host=edge_settings.host, port=edge_settings.port, reload=True)
