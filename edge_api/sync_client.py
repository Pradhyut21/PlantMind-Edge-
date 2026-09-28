import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
import httpx

from plantmind_core.models import (
    KnowledgeEntry,
    SyncStatus,
    SyncDelta,
    SyncResponse,
)
from plantmind_core.shard import EdgeShard

logger = logging.getLogger("edge_api.sync_client")


class EdgeSyncClient:
    """
    Edge-side snapshot/delta synchronizer.
    Pushes pending local writes and pulls central updates when connectivity is active.
    Demonstrably respects airplane mode / offline simulation.
    """

    def __init__(self, cloud_url: str = "http://127.0.0.1:8001"):
        self.cloud_url = cloud_url.rstrip("/")

    async def sync(self, shard: EdgeShard) -> Dict[str, Any]:
        state = shard.get_state()
        if state.get("is_offline_simulation", False):
            logger.info("Sync blocked: Kiosk is in offline / airplane simulation mode.")
            return {
                "success": False,
                "offline": True,
                "message": "Kiosk is in offline / airplane mode. Sync deferred until network is toggled on.",
                "entries_pushed": 0,
                "entries_pulled": 0,
                "conflicts_raised": 0,
            }

        # Gather eligible pending writes
        all_pending = shard.get_pending_writes()
        # Deliberate local-vs-cloud policy: omit entries marked keep_local_until_reviewed
        eligible_to_push = [e for e in all_pending if not e.keep_local_until_reviewed]
        held_local_count = len(all_pending) - len(eligible_to_push)

        delta = SyncDelta(
            device_id=shard.device_id,
            pushed_entries=eligible_to_push,
            last_known_version=state.get("last_known_server_version", 0),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        shard.log_activity(
            event_type="sync_start",
            title=f"Sync Initiated with Central Office",
            description=f"Attempting to push {len(eligible_to_push)} pending writes (held local: {held_local_count})",
            metadata={"eligible_push": len(eligible_to_push), "held_local": held_local_count},
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    f"{self.cloud_url}/api/sync/delta",
                    json=delta.model_dump(),
                )

            if res.status_code != 200:
                err_msg = f"Cloud sync error: HTTP {res.status_code} - {res.text}"
                shard.log_activity(
                    event_type="sync_error",
                    title="Sync Rejected by Cloud",
                    description=err_msg,
                    metadata={"status_code": res.status_code},
                )
                return {"success": False, "offline": False, "message": err_msg}

            data = res.json()
            sync_resp = SyncResponse(**data)

            # 1. Update local storage with pulled entries from cloud
            for p_entry in sync_resp.pulled_entries:
                shard.add_entry(p_entry, is_from_sync=True)

            # 2. Mark conflict status on local entries if any were flagged
            conflict_entry_ids = {c.entry_id for c in sync_resp.conflicts}
            for c_id in conflict_entry_ids:
                shard.update_entry_status(c_id, SyncStatus.CONFLICT)

            # 3. Clear pushed entries from local pending-write queue & mark synced
            pushed_ids = [e.id for e in eligible_to_push]
            # If an entry was flagged as conflict, do not mark as synced
            clean_synced_ids = [eid for eid in pushed_ids if eid not in conflict_entry_ids]
            shard.clear_pending_writes(clean_synced_ids)
            for eid in clean_synced_ids:
                shard.update_entry_status(eid, SyncStatus.SYNCED)

            # 4. Update shard state
            now_iso = datetime.now(timezone.utc).isoformat()
            shard.update_state({"last_sync_time": now_iso})

            shard.log_activity(
                event_type="sync_complete",
                title="Sync Session Successful",
                description=f"Pushed: {sync_resp.entries_pushed} | Pulled: {sync_resp.entries_pulled} | Conflicts: {sync_resp.conflicts_raised}",
                metadata={
                    "pushed": sync_resp.entries_pushed,
                    "pulled": sync_resp.entries_pulled,
                    "conflicts": sync_resp.conflicts_raised,
                },
            )

            return {
                "success": True,
                "offline": False,
                "message": sync_resp.message,
                "entries_pushed": sync_resp.entries_pushed,
                "entries_pulled": sync_resp.entries_pulled,
                "conflicts_raised": sync_resp.conflicts_raised,
                "last_sync_time": now_iso,
                "held_local_count": held_local_count,
            }

        except httpx.RequestError as exc:
            logger.warning(f"Sync connection failure: {exc}")
            shard.log_activity(
                event_type="sync_offline",
                title="Network Unreachable",
                description="Unable to reach central cloud API; pending writes safely preserved on local EdgeShard.",
                metadata={"error": str(exc)},
            )
            return {
                "success": False,
                "offline": True,
                "message": "Cannot reach central cloud server. All changes preserved safely in local EdgeShard.",
                "entries_pushed": 0,
                "entries_pulled": 0,
                "conflicts_raised": 0,
            }
