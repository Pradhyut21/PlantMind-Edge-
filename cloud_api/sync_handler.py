import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone

from plantmind_core.models import (
    KnowledgeEntry,
    KnowledgeType,
    SyncStatus,
    SyncDelta,
    SyncResponse,
    SyncSession,
    ConflictRecord,
)
from .central_store import CentralStore
from .conflict_engine import ConflictEngine

logger = logging.getLogger("cloud_api.sync")


class SyncHandler:
    """
    Handles bidirectional delta sync and snapshot exchange with edge kiosks.
    Inspects incoming pushed entries, applies conflict detection rules,
    and returns server-side delta updates to edge nodes.
    """

    def __init__(self, central_store: CentralStore, conflict_engine: ConflictEngine):
        self.store = central_store
        self.conflict_engine = conflict_engine

    def process_sync(self, delta: SyncDelta) -> SyncResponse:
        session_id = f"sync-{delta.device_id}-{int(datetime.now(timezone.utc).timestamp())}"
        start_time = datetime.now(timezone.utc).isoformat()

        pushed_count = 0
        conflicts_raised = []
        synced_entry_ids = []

        # 1. Process entries pushed from edge node
        for entry in delta.pushed_entries:
            # Policy check: ignore if marked keep_local_until_reviewed
            if entry.keep_local_until_reviewed:
                continue

            existing = self.store.get_entry(entry.id)

            if existing is None:
                # Brand new entry authored on edge
                entry.sync_status = SyncStatus.SYNCED
                self.store.upsert_entry(entry)
                pushed_count += 1
                synced_entry_ids.append(entry.id)
                self.store.log_activity(
                    event_type="entry_pushed",
                    title=f"New Edge Entry: {entry.title}",
                    description=f"Received from {delta.device_id} ({entry.type.value})",
                    device_id=delta.device_id,
                    metadata={"entry_id": entry.id, "type": entry.type.value},
                )
            else:
                # Potential conflict or update
                is_conflict, conflict_record, strategy = self.conflict_engine.evaluate_conflict(existing, entry)

                if is_conflict and conflict_record:
                    self.store.add_conflict(conflict_record)
                    conflicts_raised.append(conflict_record)
                    # For safety procedures, do NOT overwrite central store with the unverified edge entry!
                elif strategy in ["incoming_newer", "clean_fast_forward"]:
                    entry.sync_status = SyncStatus.SYNCED
                    self.store.upsert_entry(entry)
                    pushed_count += 1
                    synced_entry_ids.append(entry.id)
                elif strategy == "existing_newer":
                    # Central version is newer; will be pulled back to edge below
                    pass

        # 2. Compute entries to pull back down to edge
        # Pull entries authored or resolved elsewhere that this edge node doesn't have or needs to update
        all_central = self.store.list_entries(limit=1000)
        pulled_entries: List[KnowledgeEntry] = []

        for c_entry in all_central:
            # If the entry was not just authored in this push and differs from edge's origin
            if c_entry.id not in synced_entry_ids and c_entry.device_id != delta.device_id:
                # Mark as synced for edge consumption
                c_entry.sync_status = SyncStatus.SYNCED
                pulled_entries.append(c_entry)

        # 3. Record SyncSession
        end_time = datetime.now(timezone.utc).isoformat()
        session = SyncSession(
            id=session_id,
            device_id=delta.device_id,
            started_at=start_time,
            completed_at=end_time,
            entries_pushed=pushed_count,
            entries_pulled=len(pulled_entries),
            conflicts_raised=len(conflicts_raised),
            status="completed",
            notes=f"Synced successfully. {len(conflicts_raised)} conflicts raised.",
        )
        self.store.record_sync_session(session)

        # Log system activity
        self.store.log_activity(
            event_type="sync_complete",
            title=f"Sync Session Completed: {delta.device_id}",
            description=f"Pushed: {pushed_count} | Pulled: {len(pulled_entries)} | Conflicts: {len(conflicts_raised)}",
            device_id=delta.device_id,
            metadata={"session_id": session_id, "pushed": pushed_count, "pulled": len(pulled_entries)},
        )

        return SyncResponse(
            success=True,
            device_id=delta.device_id,
            entries_pushed=pushed_count,
            entries_pulled=len(pulled_entries),
            conflicts_raised=len(conflicts_raised),
            pulled_entries=pulled_entries,
            conflicts=conflicts_raised,
            cloud_timestamp=end_time,
            message="Delta synchronization completed successfully.",
        )
