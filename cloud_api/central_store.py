import os
import json
import logging
import shutil
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
)

from qdrant_edge.models import (
    KnowledgeEntry,
    KnowledgeType,
    SyncStatus,
    ConflictRecord,
    SyncSession,
    ActivityEvent,
)
from qdrant_edge.embeddings import EdgeEmbedder, EMBEDDING_DIM
from .config import cloud_settings

logger = logging.getLogger("cloud_api.store")
COLLECTION_NAME = "plantmind_central_knowledge"


class CentralStore:
    """
    Central Office Knowledge & Metadata Store.
    Connects to central Qdrant (remote server or persistent local instance),
    maintains relational metadata (procedures, conflict queue, sync history, audit log),
    and interfaces with Supabase if configured.
    """

    def __init__(self):
        self.storage_dir = os.path.abspath(cloud_settings.storage_dir)
        os.makedirs(self.storage_dir, exist_ok=True)
        self.meta_file = os.path.join(self.storage_dir, "central_metadata.json")
        self.embedder = EdgeEmbedder()
        self._init_qdrant()
        self._init_metadata()

    def _init_qdrant(self):
        """Connect to Qdrant Cloud or initialize embedded persistent instance."""
        if cloud_settings.qdrant_url:
            logger.info(f"Connecting to remote Qdrant Server at {cloud_settings.qdrant_url}")
            self.client = QdrantClient(
                url=cloud_settings.qdrant_url,
                api_key=cloud_settings.qdrant_api_key or None,
            )
        else:
            q_path = os.path.join(self.storage_dir, "qdrant_central")
            os.makedirs(q_path, exist_ok=True)
            logger.info(f"Running embedded Central Qdrant instance at {q_path}")
            self.client = QdrantClient(path=q_path)

        existing = [c.name for c in self.client.get_collections().collections]
        if COLLECTION_NAME not in existing:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )

    def _init_metadata(self):
        if not os.path.exists(self.meta_file):
            initial = {
                "entries": {},
                "conflicts": {},
                "sync_sessions": [],
                "activity_log": [],
                "devices": {
                    "kiosk-1": {"name": "Stamping Bay Kiosk #1", "status": "online", "last_sync": None},
                    "kiosk-2": {"name": "Machining Line Kiosk #2", "status": "online", "last_sync": None},
                    "kiosk-3": {"name": "Packaging Kiosk #3", "status": "idle", "last_sync": None},
                },
            }
            self._save_metadata(initial)

    def _load_metadata(self) -> Dict[str, Any]:
        try:
            with open(self.meta_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"entries": {}, "conflicts": {}, "sync_sessions": [], "activity_log": [], "devices": {}}

    def _save_metadata(self, data: Dict[str, Any]):
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def log_activity(self, event_type: str, title: str, description: str, device_id: str = "central-office", metadata: Dict[str, Any] = None):
        event = ActivityEvent(
            event_type=event_type,
            title=title,
            description=description,
            device_id=device_id,
            metadata=metadata or {},
        )
        meta = self._load_metadata()
        meta.setdefault("activity_log", []).insert(0, event.model_dump())
        meta["activity_log"] = meta["activity_log"][:200]
        self._save_metadata(meta)

    def get_activity_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        meta = self._load_metadata()
        return meta.get("activity_log", [])[:limit]

    # --- ENTRIES & VECTOR STORE ---
    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        meta = self._load_metadata()
        raw = meta.get("entries", {}).get(entry_id)
        if raw:
            return KnowledgeEntry(**raw)
        return None

    def upsert_entry(self, entry: KnowledgeEntry, sync_status: SyncStatus = SyncStatus.SYNCED) -> KnowledgeEntry:
        """Upsert knowledge entry into central Qdrant vector collection and metadata store."""
        entry.sync_status = sync_status
        text_to_embed = f"{entry.title}\n{entry.body}\nTags: {', '.join(entry.tags)}"
        vector = entry.embedding or self.embedder.embed_text(text_to_embed)

        payload = entry.model_dump(exclude={"embedding", "similarity_score"})

        # Upsert in central Qdrant
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

        # Upsert in relational metadata store
        meta = self._load_metadata()
        meta.setdefault("entries", {})[entry.id] = payload
        self._save_metadata(meta)
        return entry

    def list_entries(
        self,
        machine_id: Optional[str] = None,
        entry_type: Optional[str] = None,
        sync_status: Optional[str] = None,
        limit: int = 100,
    ) -> List[KnowledgeEntry]:
        meta = self._load_metadata()
        all_entries = [KnowledgeEntry(**v) for v in meta.get("entries", {}).values()]

        if machine_id and machine_id != "ALL":
            all_entries = [e for e in all_entries if e.machine_id == machine_id]
        if entry_type and entry_type != "ALL":
            all_entries = [e for e in all_entries if e.type.value == entry_type]
        if sync_status and sync_status != "ALL":
            all_entries = [e for e in all_entries if e.sync_status.value == sync_status]

        return sorted(all_entries, key=lambda x: x.updated_at, reverse=True)[:limit]

    def search_central(
        self,
        query: str,
        machine_id: Optional[str] = None,
        area_tag: Optional[str] = None,
        entry_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[KnowledgeEntry]:
        """Search central Qdrant server index."""
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
        return entries

    # --- CONFLICT QUEUE & RESOLUTION ---
    def add_conflict(self, conflict: ConflictRecord):
        meta = self._load_metadata()
        meta.setdefault("conflicts", {})[conflict.id] = conflict.model_dump()
        self._save_metadata(meta)

        self.log_activity(
            event_type="conflict_raised",
            title=f"Conflict Queued: {conflict.entity_title}",
            description=f"Diverging updates on {conflict.entity_type.value} ({conflict.machine_id}) flagged for review",
            device_id="cloud-engine",
            metadata={"conflict_id": conflict.id, "entry_id": conflict.entry_id},
        )

    def get_conflict(self, conflict_id: str) -> Optional[ConflictRecord]:
        meta = self._load_metadata()
        raw = meta.get("conflicts", {}).get(conflict_id)
        if raw:
            return ConflictRecord(**raw)
        return None

    def list_conflicts(self, status: Optional[str] = "open") -> List[ConflictRecord]:
        meta = self._load_metadata()
        all_conflicts = [ConflictRecord(**v) for v in meta.get("conflicts", {}).values()]
        if status and status != "ALL":
            all_conflicts = [c for c in all_conflicts if c.status == status]
        return sorted(all_conflicts, key=lambda x: x.created_at, reverse=True)

    def resolve_conflict(
        self,
        conflict_id: str,
        resolution_type: str,  # winner_picked | merged | both_annotated
        winner_version_index: Optional[int] = 0,
        merged_title: Optional[str] = None,
        merged_body: Optional[str] = None,
        merged_tags: Optional[List[str]] = None,
        resolution_note: str = "",
        resolved_by: str = "Plant Knowledge Manager",
    ) -> Optional[ConflictRecord]:
        """Resolve conflict record and update central knowledge base accordingly."""
        meta = self._load_metadata()
        conf_dict = meta.get("conflicts", {}).get(conflict_id)
        if not conf_dict:
            return None

        conflict = ConflictRecord(**conf_dict)
        now_str = datetime.now(timezone.utc).isoformat()
        conflict.status = "resolved"
        conflict.resolved_at = now_str
        conflict.resolved_by = resolved_by
        conflict.resolution_type = resolution_type
        conflict.resolution_note = resolution_note

        base_entry = self.get_entry(conflict.entry_id)

        if resolution_type == "winner_picked":
            competing = conflict.competing_versions[winner_version_index]
            winner_entry = KnowledgeEntry(
                id=conflict.entry_id,
                type=conflict.entity_type,
                title=competing.get("title", ""),
                body=competing.get("body", ""),
                machine_id=conflict.machine_id,
                area_tag=conflict.area_tag,
                created_by=competing.get("created_by", resolved_by),
                created_at=base_entry.created_at if base_entry else now_str,
                updated_at=now_str,
                device_id="central-resolved",
                version=(base_entry.version if base_entry else 1) + 1,
                sync_status=SyncStatus.SYNCED,
                tags=competing.get("tags", []),
            )
            self.upsert_entry(winner_entry)
            conflict.resolved_content = winner_entry.model_dump(exclude={"embedding", "similarity_score"})

        elif resolution_type == "merged":
            merged_entry = KnowledgeEntry(
                id=conflict.entry_id,
                type=conflict.entity_type,
                title=merged_title or conflict.entity_title,
                body=merged_body or "",
                machine_id=conflict.machine_id,
                area_tag=conflict.area_tag,
                created_by=resolved_by,
                created_at=base_entry.created_at if base_entry else now_str,
                updated_at=now_str,
                device_id="central-merged",
                version=(base_entry.version if base_entry else 1) + 1,
                sync_status=SyncStatus.SYNCED,
                tags=merged_tags or (base_entry.tags if base_entry else []),
            )
            self.upsert_entry(merged_entry)
            conflict.resolved_content = merged_entry.model_dump(exclude={"embedding", "similarity_score"})

        elif resolution_type == "both_annotated":
            # Keep Version A as standard, create second entry for Version B with variant tag
            comp_a = conflict.competing_versions[0]
            comp_b = conflict.competing_versions[1] if len(conflict.competing_versions) > 1 else comp_a

            entry_a = KnowledgeEntry(
                id=conflict.entry_id,
                type=conflict.entity_type,
                title=f"{comp_a.get('title')} (Variant A)",
                body=comp_a.get("body"),
                machine_id=conflict.machine_id,
                area_tag=conflict.area_tag,
                created_by=comp_a.get("created_by"),
                updated_at=now_str,
                version=(base_entry.version if base_entry else 1) + 1,
                sync_status=SyncStatus.SYNCED,
                tags=comp_a.get("tags", []) + ["variant-A"],
            )
            self.upsert_entry(entry_a)

            # Secondary entry
            import uuid
            entry_b = KnowledgeEntry(
                id=str(uuid.uuid4()),
                type=conflict.entity_type,
                title=f"{comp_b.get('title')} (Variant B)",
                body=comp_b.get("body"),
                machine_id=conflict.machine_id,
                area_tag=conflict.area_tag,
                created_by=comp_b.get("created_by"),
                updated_at=now_str,
                version=1,
                sync_status=SyncStatus.SYNCED,
                tags=comp_b.get("tags", []) + ["variant-B"],
            )
            self.upsert_entry(entry_b)
            conflict.resolved_content = {
                "variant_a_id": entry_a.id,
                "variant_b_id": entry_b.id,
            }

        meta["conflicts"][conflict.id] = conflict.model_dump()
        self._save_metadata(meta)

        self.log_activity(
            event_type="conflict_resolved",
            title=f"Conflict Resolved: {conflict.entity_title}",
            description=f"Manager resolved via '{resolution_type}'. Note: {resolution_note}",
            device_id="central-office",
            metadata={"conflict_id": conflict.id, "resolution_type": resolution_type},
        )
        return conflict

    # --- SYNC SESSIONS & DEVICE REGISTRY ---
    def record_sync_session(self, session: SyncSession):
        meta = self._load_metadata()
        meta.setdefault("sync_sessions", []).insert(0, session.model_dump())
        meta["sync_sessions"] = meta["sync_sessions"][:100]

        # Update device registry
        dev = meta.setdefault("devices", {}).setdefault(session.device_id, {})
        dev["last_sync"] = session.completed_at or session.started_at
        dev["status"] = "online"
        self._save_metadata(meta)

    def get_sync_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        meta = self._load_metadata()
        return meta.get("sync_sessions", [])[:limit]

    def get_devices(self) -> Dict[str, Any]:
        meta = self._load_metadata()
        return meta.get("devices", {})

    def get_cloud_stats(self) -> Dict[str, Any]:
        meta = self._load_metadata()
        entries = list(meta.get("entries", {}).values())
        conflicts = list(meta.get("conflicts", {}).values())
        open_conflicts = [c for c in conflicts if c.get("status") == "open"]

        return {
            "total_entries": len(entries),
            "open_conflicts": len(open_conflicts),
            "total_conflicts": len(conflicts),
            "active_devices": len(meta.get("devices", {})),
            "total_sync_sessions": len(meta.get("sync_sessions", [])),
            "vector_dimension": EMBEDDING_DIM,
            "qdrant_target": cloud_settings.qdrant_url or "Embedded Central Qdrant",
        }
