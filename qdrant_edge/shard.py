import os
import json
import shutil
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
)

from .models import (
    KnowledgeEntry,
    KnowledgeType,
    SyncStatus,
    DeviceMemoryStats,
    ActivityEvent,
)
from .embeddings import EdgeEmbedder, EMBEDDING_DIM

logger = logging.getLogger("qdrant_edge.shard")

COLLECTION_NAME = "plantmind_knowledge"


class EdgeShard:
    """
    Qdrant Edge local shard abstraction.
    Runs entirely on-device with persistent local storage, HNSW dense vector index,
    payload filtering, append-only pending-write queue, and snapshot export.
    """

    def __init__(self, storage_path: str = "./data/edge_shard", device_id: str = "kiosk-1"):
        self.storage_path = os.path.abspath(storage_path)
        self.device_id = device_id
        self.qdrant_path = os.path.join(self.storage_path, "qdrant_data")
        self.queue_file = os.path.join(self.storage_path, "pending_write_queue.json")
        self.activity_file = os.path.join(self.storage_path, "activity_log.json")
        self.state_file = os.path.join(self.storage_path, "edge_state.json")

        os.makedirs(self.qdrant_path, exist_ok=True)
        self.embedder = EdgeEmbedder()
        self._init_client()
        self._ensure_files()

    def _init_client(self):
        """Initialize or reopen local persistent QdrantClient."""
        self.client = QdrantClient(path=self.qdrant_path)
        existing = [c.name for c in self.client.get_collections().collections]
        if COLLECTION_NAME not in existing:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )

    def _ensure_files(self):
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
        """Append an event to local edge activity log."""
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
            # Keep last 150 events
            events = events[:150]
            with open(self.activity_file, "w", encoding="utf-8") as f:
                json.dump(events, f, indent=2)
        except Exception as e:
            logger.error(f"Error logging activity: {e}")

    def get_activity_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            with open(self.activity_file, "r", encoding="utf-8") as f:
                events = json.load(f)
            return events[:limit]
        except Exception:
            return []

    # --- PENDING WRITE LOG ---
    def _read_queue(self) -> List[Dict[str, Any]]:
        try:
            with open(self.queue_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_queue(self, queue: List[Dict[str, Any]]):
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)

    def get_pending_writes(self) -> List[KnowledgeEntry]:
        """Return pending write items that should be pushed to cloud."""
        raw = self._read_queue()
        return [KnowledgeEntry(**item) for item in raw]

    def clear_pending_writes(self, synced_ids: List[str]):
        """Remove successfully synced entries from local pending-write queue."""
        queue = self._read_queue()
        updated = [item for item in queue if item.get("id") not in synced_ids]
        self._write_queue(updated)

    # --- SEARCH & RETRIEVAL (100% OFFLINE) ---
    def search(
        self,
        query: str,
        machine_id: Optional[str] = None,
        area_tag: Optional[str] = None,
        entry_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[KnowledgeEntry]:
        """
        Fast local semantic search on EdgeShard.
        Never makes network calls; operates on local HNSW index.
        """
        query_vector = self.embedder.embed_text(query)

        filter_conditions = []
        if machine_id and machine_id != "ALL":
            filter_conditions.append(
                FieldCondition(key="machine_id", match=MatchValue(value=machine_id))
            )
        if area_tag and area_tag != "ALL":
            filter_conditions.append(
                FieldCondition(key="area_tag", match=MatchValue(value=area_tag))
            )
        if entry_type and entry_type != "ALL":
            filter_conditions.append(
                FieldCondition(key="type", match=MatchValue(value=entry_type))
            )

        q_filter = Filter(must=filter_conditions) if filter_conditions else None

        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=q_filter,
            limit=limit,
        )

        entries = []
        for point in results.points:
            payload = dict(point.payload or {})
            payload["id"] = str(point.id)
            payload["similarity_score"] = round(float(point.score), 4)
            entries.append(KnowledgeEntry(**payload))

        self.log_activity(
            event_type="search",
            title=f"Offline Search: '{query[:30]}...'",
            description=f"Returned {len(entries)} local results for machine '{machine_id or 'ALL'}'",
            metadata={"query": query, "count": len(entries), "machine_id": machine_id},
        )
        return entries

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        try:
            pts = self.client.retrieve(
                collection_name=COLLECTION_NAME,
                ids=[entry_id],
                with_payload=True,
                with_vectors=False,
            )
            if pts:
                p = pts[0]
                payload = dict(p.payload or {})
                payload["id"] = str(p.id)
                return KnowledgeEntry(**payload)
        except Exception:
            pass
        return None

    def list_entries(
        self,
        machine_id: Optional[str] = None,
        entry_type: Optional[str] = None,
        sync_status: Optional[str] = None,
        limit: int = 100,
    ) -> List[KnowledgeEntry]:
        """List local entries with optional filters."""
        filter_conditions = []
        if machine_id and machine_id != "ALL":
            filter_conditions.append(
                FieldCondition(key="machine_id", match=MatchValue(value=machine_id))
            )
        if entry_type and entry_type != "ALL":
            filter_conditions.append(
                FieldCondition(key="type", match=MatchValue(value=entry_type))
            )
        if sync_status and sync_status != "ALL":
            filter_conditions.append(
                FieldCondition(key="sync_status", match=MatchValue(value=sync_status))
            )

        q_filter = Filter(must=filter_conditions) if filter_conditions else None

        pts, _ = self.client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=q_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        entries = []
        for p in pts:
            payload = dict(p.payload or {})
            payload["id"] = str(p.id)
            entries.append(KnowledgeEntry(**payload))
        return entries

    # --- LOCAL WRITE (APPEND-ONLY QUEUE) ---
    def add_entry(
        self,
        entry: KnowledgeEntry,
        is_from_sync: bool = False,
    ) -> KnowledgeEntry:
        """
        Store entry in local EdgeShard and append to pending write queue.
        Enforces policy: if keep_local_until_reviewed is True, status remains local_only.
        """
        text_to_embed = f"{entry.title}\n{entry.body}\nTags: {', '.join(entry.tags)}"
        vector = entry.embedding or self.embedder.embed_text(text_to_embed)

        if not is_from_sync:
            # New local entry authoring
            entry.device_id = self.device_id
            entry.updated_at = datetime.now(timezone.utc).isoformat()
            if entry.keep_local_until_reviewed:
                entry.sync_status = SyncStatus.LOCAL_ONLY
            else:
                entry.sync_status = SyncStatus.PENDING_SYNC

        payload = entry.model_dump(exclude={"embedding", "similarity_score"})

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=entry.id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

        if not is_from_sync:
            # Append to pending-write log
            queue = self._read_queue()
            # If entry already in queue, update it
            queue = [item for item in queue if item.get("id") != entry.id]
            queue.append(entry.model_dump(exclude={"embedding", "similarity_score"}))
            self._write_queue(queue)

            self.log_activity(
                event_type="write",
                title=f"Local Write: {entry.title}",
                description=f"Appended {entry.type.value} to local EdgeShard (Status: {entry.sync_status.value})",
                metadata={"entry_id": entry.id, "type": entry.type.value, "status": entry.sync_status.value},
            )

        return entry

    def update_entry_status(self, entry_id: str, new_status: SyncStatus):
        """Update sync status of an entry locally."""
        entry = self.get_entry(entry_id)
        if entry:
            entry.sync_status = new_status
            self.client.set_payload(
                collection_name=COLLECTION_NAME,
                payload={"sync_status": new_status.value},
                points=[entry_id],
            )

    # --- DEVICE MEMORY INSPECTION ---
    def get_memory_stats(self) -> DeviceMemoryStats:
        """Calculate on-disk memory usage, vector counts, and sync breakdown."""
        all_pts, _ = self.client.scroll(
            collection_name=COLLECTION_NAME,
            limit=5000,
            with_payload=True,
            with_vectors=False,
        )

        total = len(all_pts)
        local_only = 0
        pending_sync = 0
        synced = 0
        conflict = 0

        for p in all_pts:
            st = (p.payload or {}).get("sync_status", "local_only")
            if st == SyncStatus.LOCAL_ONLY.value:
                local_only += 1
            elif st == SyncStatus.PENDING_SYNC.value:
                pending_sync += 1
            elif st == SyncStatus.SYNCED.value:
                synced += 1
            elif st == SyncStatus.CONFLICT.value:
                conflict += 1

        # Calculate physical disk usage
        storage_bytes = 0
        if os.path.exists(self.storage_path):
            for dirpath, _, filenames in os.walk(self.storage_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        storage_bytes += os.path.getsize(fp)
                    except OSError:
                        pass

        # Human-readable size
        if storage_bytes < 1024:
            formatted = f"{storage_bytes} B"
        elif storage_bytes < 1024 * 1024:
            formatted = f"{storage_bytes / 1024:.1f} KB"
        else:
            formatted = f"{storage_bytes / (1024 * 1024):.2f} MB"

        state = self.get_state()
        pending_queue = self._read_queue()

        return DeviceMemoryStats(
            device_id=self.device_id,
            total_entries=total,
            local_only_count=local_only,
            pending_sync_count=pending_sync,
            synced_count=synced,
            conflict_count=conflict,
            storage_bytes=storage_bytes,
            storage_formatted=formatted,
            vector_dim=EMBEDDING_DIM,
            hnsw_indexed_vectors=total,
            last_sync_time=state.get("last_sync_time"),
            collection_status="green",
            is_offline=state.get("is_offline_simulation", False),
            pending_queue_size=len(pending_queue),
        )

    def close(self):
        """Safely close client handles."""
        try:
            self.client.close()
        except Exception:
            pass
