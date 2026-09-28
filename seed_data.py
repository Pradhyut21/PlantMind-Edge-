"""
PlantMind Edge - Realistic Industrial Knowledge Base Seeder
Seeds local EdgeShards (kiosk-1, kiosk-2) and Central Cloud store
Includes pre-configured conflicting safety procedures for the demo script.
"""

import os
import sys
import shutil
from datetime import datetime, timezone

# Ensure stdout handles UTF-8 on Windows cp1252 consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


from qdrant_edge.models import (
    KnowledgeEntry,
    KnowledgeType,
    SyncStatus,
    ConflictRecord,
)
from qdrant_edge.shard import EdgeShard
from cloud_api.central_store import CentralStore
from cloud_api.conflict_engine import ConflictEngine

# Realistic Industrial Knowledge Dataset
DEMO_ENTRIES = [
    {
        "id": "e1111111-1111-4111-8111-111111111111",
        "type": KnowledgeType.MANUAL_SECTION,
        "title": "Hydraulic Power Unit Pressure Maintenance & Accumulator Check",
        "body": """Standard operating pressure for Stamping Line 3 Press (PRESS-03) is 210 bar (+/- 5 bar).
If hydraulic pressure keeps dropping on Line 3 press during continuous cycling:
1. Inspect the nitrogen pre-charge pressure on accumulator ACC-3A. Nominal pre-charge is 110 bar at 20°C.
2. Check proportional pressure reducing valve PRV-12 for particulate contamination in pilot spool.
3. Verify main hydraulic pump displacement servo piston response. Replace 10-micron return line filter if differential pressure gauge exceeds 2.5 bar.
4. Check relief valve RV-04 setting: ensure relief seat is not scored causing bypass leakage back to the central sump.""",
        "machine_id": "PRESS-03",
        "area_tag": "Stamping Line 3",
        "created_by": "OEM Manual - Schuler Press Corp",
        "tags": ["hydraulic", "pressure-drop", "accumulator", "pump", "press-03"],
        "version": 1,
    },
    {
        "id": "e2222222-2222-4222-8222-222222222222",
        "type": KnowledgeType.TRIBAL_NOTE,
        "title": "Tribal Knowledge: Line 3 Press Hydraulic Drop Under Deep Draw",
        "body": """Note from Dave (Senior Tech, 28 yrs on floor): The OEM manual tells you to check accumulator ACC-3A, but 9 times out of 10 when the Line 3 hydraulic pressure drops after 45 minutes of run time, it is NOT the accumulator.
The manifold block valve B-2 bypass seal swells when the fluid hits 55°C. Feel the return pipe from manifold block B-2 with an IR thermometer. If the pipe is over 50°C while idle, the internal Viton O-ring has flattened. Don't waste 4 hours purging the main accumulator — just swap the B-2 cartridge seal with the blue high-temp polyurethane ring in Bin 14.""",
        "machine_id": "PRESS-03",
        "area_tag": "Stamping Line 3",
        "created_by": "Dave Miller (Senior Master Tech)",
        "tags": ["tribal-knowledge", "hydraulic", "pressure-drop", "seal", "bypass", "press-03"],
        "version": 1,
    },
    {
        "id": "e3333333-3333-4333-8333-333333333333",
        "type": KnowledgeType.INCIDENT_LOG,
        "title": "Incident Log: Unplanned Stoppage - Line 3 Press Pressure Loss",
        "body": """Date: 2026-08-14 | Shift 2 | Technician: Alex M.
Symptom: Hydraulic pressure collapsed from 205 bar to 80 bar during high-tonnage stamping cycle. Machine tripped E-stop with Error Code E-774 (Pressure Delta Fault).
Root Cause: Debris in pilot orifice of cartridge valve CV-3. Flushed manifold, replaced pilot filter screen (part #HP-882). Press restored to service after 42 minutes downtime.""",
        "machine_id": "PRESS-03",
        "area_tag": "Stamping Line 3",
        "created_by": "Alex Mercer (L2 Tech)",
        "tags": ["incident", "downtime", "pressure-drop", "cartridge-valve"],
        "version": 1,
    },
    {
        "id": "e4444444-4444-4444-8444-444444444444",
        "type": KnowledgeType.MANUAL_SECTION,
        "title": "CNC Spindle Bearing Thermal Drift & High-Speed Vibration Limits",
        "body": """For CNC Milling Center CNC-01 (Mori Seiki 5-Axis):
Maximum permissible spindle runout is 0.003 mm. If chattering or harmonic whining occurs at speeds exceeding 7,500 RPM:
1. Measure spindle temperature delta between front bearing collar and rear housing. Delta should not exceed 8°C.
2. Inspect oil-air lubrication delivery pressure. Target: 0.25 MPa with 1 droplet per 8 minutes.
3. Calibrate dynamic toolholder balance to G2.5 standard at 12,000 RPM.""",
        "machine_id": "CNC-01",
        "area_tag": "Machining Cell A",
        "created_by": "OEM Manual - Mori Seiki",
        "tags": ["cnc", "spindle", "bearing", "vibration", "chatter"],
        "version": 1,
    },
    {
        "id": "e5555555-5555-4555-8555-555555555555",
        "type": KnowledgeType.TRIBAL_NOTE,
        "title": "Tribal Knowledge: CNC-01 Chattering Fix on Inconel Milling",
        "body": """When milling Inconel 718 on CNC-01, harmonic vibration develops at 6,200 RPM due to foundation resonance with Bay 2 conveyor.
Fix: Do not alter feed rate. Instead, adjust spindle speed modulation switch SSM-1 to +/- 150 RPM cyclic dither. This breaks up the harmonic standing wave without reducing tool life.""",
        "machine_id": "CNC-01",
        "area_tag": "Machining Cell A",
        "created_by": "Elena Rostova (Lead CNC Specialist)",
        "tags": ["cnc", "tribal-knowledge", "harmonic", "resonance"],
        "version": 1,
    },
    {
        "id": "e6666666-6666-4666-8666-666666666666",
        "type": KnowledgeType.TRIBAL_NOTE,
        "title": "Local Tribal Note: Press-03 Proximity Switch Sticking (Draft Review)",
        "body": """Unverified shop observation: On rainy humid days, the lower safety curtain magnetic reed switch on Line 3 sticks in OPEN state. Spraying WD-40 Specialist Dry Contact Cleaner on pin 3 fixed it twice.
Marked for supervisor review before standardizing.""",
        "machine_id": "PRESS-03",
        "area_tag": "Stamping Line 3",
        "created_by": "Junior Tech Leo",
        "tags": ["sensor", "reed-switch", "humidity", "draft"],
        "version": 1,
        "keep_local_until_reviewed": True,
        "sync_status": SyncStatus.LOCAL_ONLY,
    },
]

# The Seeded Conflict Entity: Safety Procedure for Hydraulic Press Depressurization
CONFLICT_ENTRY_ID = "c7777777-7777-4777-8777-777777777777"

SAFETY_PROCEDURE_BASE = {
    "id": CONFLICT_ENTRY_ID,
    "type": KnowledgeType.SAFETY_PROCEDURE,
    "title": "LOTO Safety Procedure: Hydraulic Press 03 Emergency Depressurization",
    "body": """MANDATORY LOCKOUT/TAGOUT (LOTO) SAFETY PROCEDURE - PRESS-03:
1. Push red Master Control Stop (MCP-01) and isolate electrical disconnect Breaker 4B with OSHA padlock.
2. Turn manual hydraulic isolation valve V-101 90 degrees clockwise to LOCKED-CLOSED position.
3. Open manual needle drain valve NV-02 slowly to bleed accumulator ACC-3A pressure down to exactly 0.0 bar.
4. Visually verify pressure gauge PG-1 reads 0 bar.
5. WAIT MANDATORY 10 MINUTES for manifold thermal dissipation before loosening any hydraulic fitting. Wear full face shield and 500-bar rated puncture gloves.""",
    "machine_id": "PRESS-03",
    "area_tag": "Stamping Line 3",
    "created_by": "Plant Safety Committee",
    "tags": ["safety", "loto", "depressurization", "lockout", "press-03"],
    "version": 1,
}

# Version A: Modified by Dave Miller on Kiosk-1 (Standard safety enhancement)
VERSION_A = {
    "version": 2,
    "title": "LOTO Safety Procedure: Hydraulic Press 03 Depressurization & Nitrogen Bleed",
    "body": """MANDATORY LOTO PROCEDURE (Rev 2 - Line 3 Press):
1. Push Master Stop (MCP-01) and lock Breaker 4B with red supervisor padlock.
2. Turn manual isolation valve V-101 clockwise to locked-closed.
3. Connect certified bleed hose to NV-02 before opening. Bleed accumulator ACC-3A to 0.0 bar.
4. Verify digital sensor PT-101 and analog dial PG-1 BOTH confirm zero residual energy.
5. MANDATORY 10 MINUTE COOL-DOWN: Do not touch high-pressure manifold until casing is below 35°C.
6. Wear Level-3 Kevlar fluid-shield gauntlets and OSHA safety glasses with side shields.""",
    "created_by": "Dave Miller (Master Tech)",
    "device_id": "kiosk-1",
    "updated_at": "2026-09-28T09:30:00Z",
    "tags": ["safety", "loto", "press-03", "zero-energy"],
}

# Version B: Modified by Frank (Rapid maintenance shortcut on Kiosk-2)
VERSION_B = {
    "version": 2,
    "title": "LOTO Safety Procedure: Quick Depressurization Sequence Line 3 Press",
    "body": """RAPID LINE 3 DEPRESSURIZATION FOR DIE SWAPS:
1. Trip emergency e-stop switch E-03.
2. Directly open high-flow dump valve V-104 to dump pressure straight to reservoir in 15 seconds.
3. Override safety interlock bypass switch SW-8 to allow immediate tool change without waiting for 10-minute manifold cool-down.
4. Check gauge PG-1 quickly, then begin unbolting die clamp bolts. Standard nitrile gloves are sufficient.""",
    "created_by": "Frank Briggs (Contract Shift Lead)",
    "device_id": "kiosk-2",
    "updated_at": "2026-09-28T09:45:00Z",
    "tags": ["safety", "rapid-turnaround", "dump-valve", "press-03"],
}


def seed():
    print("==================================================")
    print(" PlantMind Edge — Industrial Knowledge Base Seeder")
    print("==================================================")

    # 1. Initialize Central Store
    print("\n[1/4] Seeding Central Store (Port 8001)...")
    central = CentralStore()

    # Clear previous seed for clean test run
    # (Optional: preserve structure)
    for raw in DEMO_ENTRIES:
        entry = KnowledgeEntry(
            id=raw["id"],
            type=raw["type"],
            title=raw["title"],
            body=raw["body"],
            machine_id=raw["machine_id"],
            area_tag=raw["area_tag"],
            created_by=raw["created_by"],
            tags=raw["tags"],
            version=raw["version"],
            device_id="central-office",
            sync_status=raw.get("sync_status", SyncStatus.SYNCED),
            keep_local_until_reviewed=raw.get("keep_local_until_reviewed", False),
        )
        central.upsert_entry(entry)
        print(f"  ✓ Central Entry: [{entry.type.value}] {entry.title[:50]}...")

    # Insert base safety procedure into central
    base_safety = KnowledgeEntry(
        id=SAFETY_PROCEDURE_BASE["id"],
        type=SAFETY_PROCEDURE_BASE["type"],
        title=SAFETY_PROCEDURE_BASE["title"],
        body=SAFETY_PROCEDURE_BASE["body"],
        machine_id=SAFETY_PROCEDURE_BASE["machine_id"],
        area_tag=SAFETY_PROCEDURE_BASE["area_tag"],
        created_by=SAFETY_PROCEDURE_BASE["created_by"],
        tags=SAFETY_PROCEDURE_BASE["tags"],
        version=SAFETY_PROCEDURE_BASE["version"],
        device_id="central-office",
        sync_status=SyncStatus.SYNCED,
    )
    central.upsert_entry(base_safety)
    print(f"  ✓ Central Base Safety: {base_safety.title}")

    # 2. Seed Pre-existing Conflict Record in Central Store
    print("\n[2/4] Seeding Pre-existing Divergent Safety Conflict (Demo Step 4)...")
    conflict_engine = ConflictEngine()

    dummy_existing = KnowledgeEntry(
        id=CONFLICT_ENTRY_ID,
        type=KnowledgeType.SAFETY_PROCEDURE,
        title=VERSION_A["title"],
        body=VERSION_A["body"],
        machine_id="PRESS-03",
        area_tag="Stamping Line 3",
        created_by=VERSION_A["created_by"],
        device_id=VERSION_A["device_id"],
        version=VERSION_A["version"],
        tags=VERSION_A["tags"],
    )
    dummy_incoming = KnowledgeEntry(
        id=CONFLICT_ENTRY_ID,
        type=KnowledgeType.SAFETY_PROCEDURE,
        title=VERSION_B["title"],
        body=VERSION_B["body"],
        machine_id="PRESS-03",
        area_tag="Stamping Line 3",
        created_by=VERSION_B["created_by"],
        device_id=VERSION_B["device_id"],
        version=VERSION_B["version"],
        tags=VERSION_B["tags"],
    )

    is_conflict, conflict_record, strat = conflict_engine.evaluate_conflict(dummy_existing, dummy_incoming)
    if conflict_record:
        central.add_conflict(conflict_record)
        print(f"  ✓ Conflict Record Queued: ID={conflict_record.id[:12]}...")
        print(f"  ✓ Safety Conflict Reasoning generated (Summary length: {len(conflict_record.ai_summary or '')} chars)")

    # 3. Seed Edge Kiosk 1 (Stamping Bay Kiosk)
    print("\n[3/4] Seeding Local EdgeShard for Kiosk-1 (Port 8000)...")
    shard_kiosk1 = EdgeShard(storage_path="./data/edge_devices/kiosk-1", device_id="kiosk-1")

    for raw in DEMO_ENTRIES:
        entry = KnowledgeEntry(
            id=raw["id"],
            type=raw["type"],
            title=raw["title"],
            body=raw["body"],
            machine_id=raw["machine_id"],
            area_tag=raw["area_tag"],
            created_by=raw["created_by"],
            tags=raw["tags"],
            version=raw["version"],
            device_id="kiosk-1" if "Dave" in raw["created_by"] else "central-office",
            sync_status=raw.get("sync_status", SyncStatus.SYNCED),
            keep_local_until_reviewed=raw.get("keep_local_until_reviewed", False),
        )
        shard_kiosk1.add_entry(entry, is_from_sync=True)
        print(f"  ✓ Kiosk-1 Shard: {entry.title[:45]}... (Status: {entry.sync_status.value})")

    # Add the base safety procedure on Kiosk-1
    shard_kiosk1.add_entry(base_safety, is_from_sync=True)

    # 4. Seed Edge Kiosk 2 (Machining Line Kiosk)
    print("\n[4/4] Seeding Local EdgeShard for Kiosk-2...")
    shard_kiosk2 = EdgeShard(storage_path="./data/edge_devices/kiosk-2", device_id="kiosk-2")
    for raw in DEMO_ENTRIES[:4]:
        entry = KnowledgeEntry(
            id=raw["id"],
            type=raw["type"],
            title=raw["title"],
            body=raw["body"],
            machine_id=raw["machine_id"],
            area_tag=raw["area_tag"],
            created_by=raw["created_by"],
            tags=raw["tags"],
            version=raw["version"],
            device_id="central-office",
            sync_status=SyncStatus.SYNCED,
        )
        shard_kiosk2.add_entry(entry, is_from_sync=True)

    print("\n==================================================")
    print(" Seed Complete! PlantMind Edge environment is ready.")
    print(" - Central Qdrant & SQLite initialized")
    print(" - Kiosk-1 & Kiosk-2 local EdgeShards seeded")
    print(" - Pre-configured safety conflict queued for review")
    print("==================================================")


if __name__ == "__main__":
    seed()
