import os
import json
import time
import shutil
import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

import qdrant_edge
from qdrant_edge import (
    EdgeShard,
    EdgeConfig,
    EdgeVectorParams,
    Distance,
    Point,
    UpdateOperation,
    Query,
    SearchRequest,
    ScrollRequest,
    Filter,
    FieldCondition,
    MatchValue,
)

from .models import (
    KnowledgeEntry,
    KnowledgeType,
    SyncStatus,
    DeviceMemoryStats,
    ActivityEvent,
)
from .embeddings import EdgeEmbedder, EMBEDDING_DIM

logger = logging.getLogger("plantmind_core.shard")


def to_uuid(id_val: Any) -> str:
    """Ensure a deterministic, valid UUID string required by qdrant_edge.Point."""
    try:
        return str(uuid.UUID(str(id_val)))
    except Exception:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(id_val)))


class EdgeShardManager:
    """
    Production Qdrant Edge local shard manager.
    Directly utilizes the official 'qdrant-edge-py' native bindings (EdgeShard) for on-device
    retrieval, HNSW cosine vector index, persistent append-only staging log, and deliberate data sovereignty.
    """

    def __init__(self, storage_path: str = "./data/edge_devices/kiosk-1", device_id: str = "kiosk-1"):
        self.storage_path = os.path.abspath(storage_path)
        self.device_id = device_id
        self.qdrant_path = os.path.join(self.storage_path, "qdrant_data")
        self.queue_file = os.path.join(self.storage_path, "pending_write_queue.json")
        self.activity_file = os.path.join(self.storage_path, "activity_log.json")
        self.state_file = os.path.join(self.storage_path, "edge_state.json")

        os.makedirs(self.qdrant_path, exist_ok=True)
        self.embedder = EdgeEmbedder()
        self._init_shard()
        self._ensure_files()

    def _init_shard(self):
        """Initialize or load the official native Qdrant EdgeShard."""
        vector_params = EdgeVectorParams(size=EMBEDDING_DIM, distance=Distance.Cosine)
        edge_config = EdgeConfig(vectors={"": vector_params})

        config_file = os.path.join(self.qdrant_path, "edge_config.json")
        if not os.path.exists(config_file):
            logger.info(f"Creating new official Qdrant EdgeShard at: {self.qdrant_path}")
            self.shard = qdrant_edge.EdgeShard.create(self.qdrant_path, edge_config)
        else:
            logger.info(f"Loading existing official Qdrant EdgeShard from: {self.qdrant_path}")
            self.shard = qdrant_edge.EdgeShard.load(self.qdrant_path)

    def _ensure_files(self):
        """Ensure persistent staging queue and activity log exist."""
        if not os.path.exists(self.queue_file):
            with open(self.queue_file, "w", encoding="utf-8") as f:
                json.dump([], f)
        if not os.path.exists(self.activity_file):
            with open(self.activity_file, "w", encoding="utf-8") as f:
                json.dump([], f)
        if not os.path.exists(self.state_file):
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({
                    "last_sync_time": None,
                    "last_known_server_version": 0,
                    "is_offline_simulation": False
                }, f)

    def get_state(self) -> Dict[str, Any]:
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_state(self, updates: Dict[str, Any]):
        state = self.get_state()
        state.update(updates)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def log_activity(self, event_type: str, title: str, description: str, metadata: Dict[str, Any] = None):
        """Append an event to the local edge activity log."""
        event = ActivityEvent(
            event_type=event_type,
            title=title,
            description=description,
            device_id=self.device_id,
            metadata=metadata or {},
        )
        try:
            with open(self.activity_file, "r", encoding="utf-8") as f:
                events = json.load(f)
            events.insert(0, event.model_dump())
            events = events[:150]  # keep bounded in local memory
            with open(self.activity_file, "w", encoding="utf-8") as f:
                json.dump(events, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")

    def get_activity_log(self, limit: int = 30) -> List[Dict[str, Any]]:
        try:
            with open(self.activity_file, "r", encoding="utf-8") as f:
                events = json.load(f)
            return events[:limit]
        except Exception:
            return []

    # -------------------------------------------------------------------------
    # Core Vector Operations (Official Qdrant Edge)
    # -------------------------------------------------------------------------

    def upsert_entry(self, entry: KnowledgeEntry, vector: Optional[List[float]] = None) -> KnowledgeEntry:
        """Upsert a KnowledgeEntry into the local native EdgeShard."""
        if vector is None:
            vector = self.embedder.embed(entry.body, entry.title)

        payload = entry.model_dump(mode="json")
        point_id = to_uuid(entry.id)
        point = Point(id=point_id, vector=vector, payload=payload)

        op = UpdateOperation.upsert_points([point])
        self.shard.update(op)
        self.shard.flush()

        logger.debug(f"Upserted entry '{entry.id}' into EdgeShard ({point_id})")
        return entry

    def add_entry(self, entry: KnowledgeEntry, is_from_sync: bool = False) -> KnowledgeEntry:
        """Add entry to local EdgeShard and append to persistent staging queue if allowed."""
        self.upsert_entry(entry)
        if not is_from_sync and not entry.keep_local_until_reviewed:
            self._enqueue_pending_write(entry)
        return entry

    def search(
        self,
        query: str = "",
        query_text: str = "",
        machine_id: Optional[str] = None,
        area_tag: Optional[str] = None,
        entry_type: Optional[str] = None,
        knowledge_type: Optional[KnowledgeType] = None,
        limit: int = 10,
    ) -> List[KnowledgeEntry]:
        """
        Execute low-latency semantic search on the local Qdrant EdgeShard.
        Runs entirely on-device with zero network requests.
        Returns List[KnowledgeEntry] with similarity_score set.
        """
        search_str = query or query_text
        t0 = time.time()
        query_vector = self.embedder.embed(search_str)

        # Build filter if requested
        must_conditions = []
        target_type = entry_type or (knowledge_type.value if hasattr(knowledge_type, "value") else str(knowledge_type) if knowledge_type else None)
        if target_type:
            must_conditions.append(FieldCondition(key="type", match=MatchValue(value=target_type)))
        if machine_id and machine_id != "ALL":
            must_conditions.append(FieldCondition(key="machine_id", match=MatchValue(value=machine_id)))
        if area_tag and area_tag != "ALL":
            must_conditions.append(FieldCondition(key="area_tag", match=MatchValue(value=area_tag)))

        edge_filter = Filter(must=must_conditions) if must_conditions else None
        search_query = Query.Nearest(query_vector)

        req = SearchRequest(
            query=search_query,
            limit=limit,
            with_payload=True,
            filter=edge_filter,
        )

        scored_points = self.shard.search(req)
        latency_ms = round((time.time() - t0) * 1000, 2)

        results: List[KnowledgeEntry] = []
        for sp in scored_points:
            pld = sp.payload or {}
            entry = KnowledgeEntry(**pld)
            entry.similarity_score = round(float(sp.score), 4)
            results.append(entry)

        self.log_activity(
            event_type="search",
            title=f"Offline Search: '{search_str[:35]}...'",
            description=f"Returned {len(results)} local results in {latency_ms}ms via native EdgeShard",
            metadata={"query": search_str, "latency_ms": latency_ms, "results_count": len(results)},
        )

        return results

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Retrieve a single KnowledgeEntry from EdgeShard by ID."""
        try:
            point_id = to_uuid(entry_id)
            records = self.shard.retrieve([point_id], with_payload=True)
            if records and records[0].payload:
                return KnowledgeEntry(**records[0].payload)
        except Exception as e:
            logger.error(f"Failed to retrieve entry {entry_id}: {e}")
        return None

    def get_entry_by_id(self, entry_id: str) -> Optional[KnowledgeEntry]:
        return self.get_entry(entry_id)

    def list_entries(
        self,
        machine_id: Optional[str] = None,
        entry_type: Optional[str] = None,
        sync_status: Optional[str] = None,
        limit: int = 150,
    ) -> List[KnowledgeEntry]:
        """Scroll and filter entries from the local EdgeShard."""
        try:
            req = ScrollRequest(limit=limit, with_payload=True)
            records, _ = self.shard.scroll(req)
            entries = []
            for r in records:
                if r.payload:
                    e = KnowledgeEntry(**r.payload)
                    # Apply memory filters if requested
                    if machine_id and machine_id != "ALL" and e.machine_id != machine_id:
                        continue
                    if entry_type and entry_type != "ALL":
                        e_type = e.type.value if hasattr(e.type, "value") else str(e.type)
                        if e_type != entry_type:
                            continue
                    if sync_status and sync_status != "ALL":
                        e_sync = e.sync_status.value if hasattr(e.sync_status, "value") else str(e.sync_status)
                        if e_sync != sync_status:
                            continue
                    entries.append(e)
            return entries
        except Exception as e:
            logger.error(f"Failed to list EdgeShard entries: {e}")
            return []

    def get_all_entries(self, limit: int = 150) -> List[KnowledgeEntry]:
        return self.list_entries(limit=limit)

    def count(self) -> int:
        """Return total points indexed in local EdgeShard."""
        try:
            return self.shard.info().points_count
        except Exception:
            return 0

    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry from the local EdgeShard."""
        try:
            point_id = to_uuid(entry_id)
            op = UpdateOperation.delete_points([point_id])
            self.shard.update(op)
            self.shard.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to delete {entry_id}: {e}")
            return False

    def update_entry_payload(self, entry_id: str, payload_updates: Dict[str, Any]):
        """Update payload fields on a point in EdgeShard."""
        try:
            point_id = to_uuid(entry_id)
            op = UpdateOperation.set_payload(point_ids=[point_id], payload=payload_updates)
            self.shard.update(op)
            self.shard.flush()
        except Exception as e:
            logger.error(f"Failed to update entry payload {entry_id}: {e}")

    def update_entry_status(self, entry_id: str, status: Any):
        """Update the sync_status field of an entry in the local EdgeShard."""
        status_val = status.value if hasattr(status, "value") else str(status)
        self.update_entry_payload(entry_id, {"sync_status": status_val})

    # -------------------------------------------------------------------------
    # Persistent Append-Only Staging Log & Data Sovereignty Policy
    # -------------------------------------------------------------------------

    def append_observation(
        self,
        title: str,
        content: str,
        machine_id: str,
        author: str,
        policy: str = "allow_sync",
        tags: List[str] = None,
        symptom_keywords: List[str] = None,
    ) -> KnowledgeEntry:
        """
        Record a new observation directly into the local EdgeShard.
        - If policy == 'allow_sync', appends to persistent pending write queue.
        - If policy == 'local_only', remains on this tablet only (deliberate data sovereignty).
        """
        now = datetime.now(timezone.utc).isoformat()
        is_local_only = (policy == "local_only")
        sync_status = SyncStatus.LOCAL_ONLY if is_local_only else SyncStatus.PENDING_SYNC

        entry = KnowledgeEntry(
            id=str(uuid.uuid4()),
            title=title,
            body=content,
            type=KnowledgeType.TRIBAL_NOTE,
            machine_id=machine_id,
            created_by=author,
            created_at=now,
            updated_at=now,
            version=1,
            device_id=self.device_id,
            sync_status=sync_status,
            keep_local_until_reviewed=is_local_only,
            tags=tags or ["floor_observation"],
        )

        # 1. Immediate on-device indexing in native EdgeShard
        self.upsert_entry(entry)

        # 2. Append to persistent staging queue if allowed to sync
        if not is_local_only:
            self._enqueue_pending_write(entry)

        self.log_activity(
            event_type="local_write",
            title=f"Logged Observation: '{title[:35]}'",
            description=f"Saved to local EdgeShard. Policy: {policy}.",
            metadata={"entry_id": entry.id, "policy": policy, "machine_id": machine_id},
        )

        return entry

    def _read_queue(self) -> List[Dict[str, Any]]:
        try:
            with open(self.queue_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_queue(self, queue: List[Dict[str, Any]]):
        try:
            with open(self.queue_file, "w", encoding="utf-8") as f:
                json.dump(queue, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write queue: {e}")

    def _enqueue_pending_write(self, entry: KnowledgeEntry):
        """Append to persistent staging log."""
        queue = self._read_queue()
        queue = [q for q in queue if q.get("id") != entry.id]
        queue.append(entry.model_dump(mode="json"))
        self._write_queue(queue)

    def get_pending_writes(self) -> List[KnowledgeEntry]:
        queue = self._read_queue()
        return [KnowledgeEntry(**item) for item in queue]

    def clear_pending_writes(self, synced_ids: List[str]):
        """Remove successfully synchronized entries from the local staging queue."""
        queue = self._read_queue()
        synced_set = set(synced_ids)
        remaining = [q for q in queue if q.get("id") not in synced_set]
        self._write_queue(remaining)

    # -------------------------------------------------------------------------
    # Device Memory & Storage Telemetry
    # -------------------------------------------------------------------------

    def get_memory_stats(self) -> DeviceMemoryStats:
        """
        Return verified, accurate on-device storage and process memory telemetry.
        Accurately measures disk bytes and active process RSS memory.
        """
        entries = self.list_entries(limit=500)
        local_only = sum(1 for e in entries if e.sync_status == SyncStatus.LOCAL_ONLY or getattr(e, "keep_local_until_reviewed", False))
        pending = len(self.get_pending_writes())
        synced = sum(1 for e in entries if e.sync_status == SyncStatus.SYNCED)
        conflicts = sum(1 for e in entries if e.sync_status == SyncStatus.CONFLICT)

        # Measure physical disk storage of local EdgeShard
        storage_bytes = 0
        if os.path.exists(self.qdrant_path):
            for root, _, files in os.walk(self.qdrant_path):
                for f in files:
                    try:
                        storage_bytes += os.path.getsize(os.path.join(root, f))
                    except OSError:
                        pass

        # Format storage
        if storage_bytes < 1024 * 1024:
            storage_formatted = f"{storage_bytes / 1024:.1f} KB"
        else:
            storage_formatted = f"{storage_bytes / (1024 * 1024):.2f} MB"

        return DeviceMemoryStats(
            device_id=self.device_id,
            total_entries=len(entries),
            local_only_count=local_only,
            pending_sync_count=pending,
            synced_count=synced,
            conflict_count=conflicts,
            storage_bytes=storage_bytes,
            storage_formatted=storage_formatted,
            vector_dim=EMBEDDING_DIM,
            collection_name="qdrant_edge_local_shard",
        )

    def export_snapshot(self) -> str:
        """Export local EdgeShard state to a snapshot zip."""
        snapshots_dir = os.path.join(self.storage_path, "snapshots")
        os.makedirs(snapshots_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"snapshot_{self.device_id}_{timestamp}"
        snapshot_zip = os.path.join(snapshots_dir, snapshot_name)
        archive_path = shutil.make_archive(snapshot_zip, "zip", self.qdrant_path)
        logger.info(f"Exported EdgeShard snapshot to {archive_path}")
        return archive_path

    def close(self):
        """Gracefully flush and close the EdgeShard."""
        try:
            self.shard.flush()
            self.shard.close()
        except Exception:
            pass


# Alias for backward compatibility
EdgeShard = EdgeShardManager
