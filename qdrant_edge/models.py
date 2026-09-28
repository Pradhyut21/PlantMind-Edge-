from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone


class KnowledgeType(str, Enum):
    MANUAL_SECTION = "manual_section"
    INCIDENT_LOG = "incident_log"
    TRIBAL_NOTE = "tribal_note"
    SAFETY_PROCEDURE = "safety_procedure"


class SyncStatus(str, Enum):
    LOCAL_ONLY = "local_only"
    PENDING_SYNC = "pending_sync"
    SYNCED = "synced"
    CONFLICT = "conflict"


class KnowledgeEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: KnowledgeType = KnowledgeType.TRIBAL_NOTE
    title: str
    body: str
    machine_id: str = "GLOBAL"
    area_tag: str = "General"
    created_by: str = "Technician"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    device_id: str = "kiosk-local"
    version: int = 1
    sync_status: SyncStatus = SyncStatus.LOCAL_ONLY
    keep_local_until_reviewed: bool = False
    tags: List[str] = Field(default_factory=list)
    embedding: Optional[List[float]] = None
    similarity_score: Optional[float] = None


class CompetingVersion(BaseModel):
    version: int
    title: str
    body: str
    created_by: str
    device_id: str
    updated_at: str
    tags: List[str] = Field(default_factory=list)


class ConflictRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entry_id: str
    entity_title: str
    entity_type: KnowledgeType
    machine_id: str = "GLOBAL"
    area_tag: str = "General"
    status: str = "open"  # open | resolved
    competing_versions: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_type: Optional[str] = None  # winner_picked | merged | both_annotated
    resolution_note: Optional[str] = None
    resolved_content: Optional[Dict[str, Any]] = None
    ai_summary: Optional[str] = None


class SyncDelta(BaseModel):
    device_id: str
    pushed_entries: List[KnowledgeEntry] = Field(default_factory=list)
    last_known_version: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SyncResponse(BaseModel):
    success: bool = True
    device_id: str
    entries_pushed: int = 0
    entries_pulled: int = 0
    conflicts_raised: int = 0
    pulled_entries: List[KnowledgeEntry] = Field(default_factory=list)
    conflicts: List[ConflictRecord] = Field(default_factory=list)
    cloud_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    message: str = "Sync complete"


class SyncSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    entries_pushed: int = 0
    entries_pulled: int = 0
    conflicts_raised: int = 0
    status: str = "in_progress"  # in_progress | completed | failed
    notes: Optional[str] = None


class DeviceMemoryStats(BaseModel):
    device_id: str
    total_entries: int = 0
    local_only_count: int = 0
    pending_sync_count: int = 0
    synced_count: int = 0
    conflict_count: int = 0
    storage_bytes: int = 0
    storage_formatted: str = "0 KB"
    vector_dim: int = 384
    hnsw_indexed_vectors: int = 0
    last_sync_time: Optional[str] = None
    collection_status: str = "green"
    is_offline: bool = False
    pending_queue_size: int = 0


class ActivityEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str  # search | write | sync_start | sync_complete | conflict_raised | conflict_resolved | network_toggle
    title: str
    description: str
    device_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
