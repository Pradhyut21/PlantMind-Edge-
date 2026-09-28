# PlantMind Edge 🏭⚡

**An offline-first industrial knowledge-continuity platform where factory-floor technicians search and update maintenance knowledge locally via Qdrant Edge, with intelligent, conflict-aware sync to a central Qdrant Server when connectivity returns.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Vector DB: Qdrant](https://img.shields.io/badge/Vector_DB-Qdrant_Edge-red.svg)](https://qdrant.tech)
[![AI Reasoning: Groq LLaMA-3.3-70B](https://img.shields.io/badge/Reasoning-Groq_LLaMA_3.3_70B-orange.svg)](https://groq.com)
[![Next.js: 16](https://img.shields.io/badge/Frontend-Next.js_PWA-black.svg)](https://nextjs.org)
[![FastAPI: 0.115](https://img.shields.io/badge/Backend-FastAPI-teal.svg)](https://fastapi.tiangolo.com)

---

## 1. Problem Statement & Mission

Industrial factory floors (stamping presses, 5-axis CNC cells, automated packaging bays) frequently suffer from zero or intermittent Wi-Fi connectivity. When critical equipment halts, technicians cannot wait on network connections or loss of tribal knowledge from retiring senior specialists.

**PlantMind Edge** answers this by running **Qdrant Edge (`EdgeShard`)** directly on the local tablet / kiosk:
- **100% Offline Semantic Search (< 150ms)**: Technicians query symptoms (spoken or typed) against local dense vector indexes without network dependencies.
- **Append-Only Local Writes**: Observations and incident logs are committed locally on-device and queued in an append-only log.
- **Intelligent Snapshot / Delta Sync**: Automatic network detection pushes pending updates and pulls central delta packages when connection returns.
- **Conflict Detection with Groq LLaMA Reasoning**: Safety-critical procedures **never** silently overwrite via last-write-wins. Diverging revisions are queued for human review with an AI-generated plain-language difference and risk summary.
- **Deliberate Local-vs-Cloud Data Policy**: Technicians can flag tribal notes as *"Keep local until reviewed"*, giving granular control over what stays on-device vs. what broadcasts to the cloud.

---

## 2. Core Architecture

```
┌────────────────────────────────────────┐        ┌────────────────────────────────────────┐
│          EDGE (Kiosk / Tablet)         │        │         CLOUD (Central Office)         │
│                                        │        │                                        │
│  Next.js / TS PWA (Offline Shell)      │        │  Next.js / TS Admin Dashboard          │
│    ↕                                   │        │    ↕                                   │
│  FastAPI (edge-api, Port 8000)         │  sync  │  FastAPI (cloud-api, Port 8001)        │
│  Runs on device or LAN kiosk box       │ <────> │    ↕                                   │
│    ↕                                   │snapshot│  Qdrant Server (Central Collection)    │
│  Qdrant Edge (EdgeShard)               │exchange│  Supabase / Central Metadata Store     │
│  - HNSW 384-dim dense vectors          │        │  - Master procedures & audit log       │
│  - Maintenance manuals & incident logs │        │  - Open safety conflict queue          │
│  - Tribal-knowledge field notes        │        │    ↕                                   │
│  - Local append-only pending queue     │        │  Groq LLaMA (Reasoning + Diff Engine)  │
└────────────────────────────────────────┘        └────────────────────────────────────────┘
```

### Architectural Safeguards
1. **Edge node = Source of truth for reads while offline**: Every technician query hits the local `EdgeShard` first — never blocks on the network.
2. **Writes are append-only locally**: Changes are staged in a persistent `pending_write_queue.json` log on disk, enabling multi-device conflict detection.
3. **Sync = Snapshot / Delta exchange**: Edge pushes eligible pending entries and pulls central delta updates since last sync timestamp.
4. **Safety Procedure Protection**: If two edge nodes update a `safety_procedure` while offline, the cloud creates a `ConflictRecord` requiring human reconciliation. Non-safety entries can auto-resolve to newest while preserving full audit history.

---

## 3. Tech Stack

- **Frontend:** Next.js (App Router, TypeScript, PWA Service Worker, Industrial Vanilla CSS design system)
- **Local Edge API:** Python 3.13 + FastAPI running on Port `8000`
- **Central Cloud API:** Python 3.13 + FastAPI running on Port `8001`
- **Local Vector DB:** Qdrant Edge (`qdrant-client` embedded local shard with HNSW cosine index)
- **Central Vector DB:** Qdrant Server / Qdrant Cloud snapshot-compatible
- **Embeddings Pipeline:** FastEmbed (ONNX BAAI/bge-small-en-v1.5, 384 dimensions, < 5ms local CPU execution) with deterministic industrial n-gram fallback
- **AI Reasoning:** Groq LLaMA-3.3-70B for plain-language conflict summaries and safety risk evaluation
- **Metadata Store:** Relational metadata store with Supabase integration support

---

## 4. Quick Start & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Node.js 18+ (Tested on Node v22.18)
- Git

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/Pradhyut21/PlantMind-Edge.git
cd PlantMind-Edge

# Install Python backend requirements
pip install -r requirements.txt

# Install frontend requirements
cd frontend
npm install
cd ..
```

### 2. Seed Realistic Demo Data
Seeds the central store and local EdgeShards (`kiosk-1`, `kiosk-2`) with maintenance manuals, tribal tips, and a pre-configured conflicting safety procedure:
```bash
python seed_data.py
```

### 3. Launch Services

Run the services in three terminal tabs:

**Terminal 1 — Central Cloud API (Port 8001):**
```bash
uvicorn cloud_api.main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 — Edge Kiosk API (Port 8000):**
```bash
uvicorn edge_api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 3 — Next.js Frontend (Port 3000):**
```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## 5. End-to-End Demo Walkthrough (Judged Script)

Follow this 5-step script to demonstrate the full edge-to-cloud workflow:

### Step 1: Kiosk in Airplane Mode & < 150ms Offline Search
1. Open the UI at `http://localhost:3000`. You are on the **Technician Kiosk (Edge)** view.
2. In the top-right header, click **"ONLINE (LAN)"** to toggle into **"OFFLINE (Airplane)"** mode. Notice the glowing red banner confirming zero network calls.
3. Type or speak the fault symptom:
   ```
   hydraulic pressure keeps dropping on line 3 press
   ```
4. Observe the result in **< 150ms** directly from the local `EdgeShard`. Notice the top match:
   - *Tribal Knowledge: Line 3 Press Hydraulic Drop Under Deep Draw* by Senior Master Tech Dave Miller.
   - Match score: **78% Semantic Match**.
   - Note the technical advice: *"Don't purge the accumulator; replace manifold B-2 bypass seal with high-temp polyurethane ring in Bin 14."*

### Step 2: Offline Local Write & Append-Only Log
1. Click the **"Log Observation (Append-Only)"** tab.
2. Click the quick demo button **"+ Relief Valve Tip"** (or type a new observation).
3. Click **"Commit to Local EdgeShard"**.
4. Switch to the **"Device Memory Inspector"** tab:
   - Notice the pending queue count incremented to `1`.
   - Entry sync status is displayed as `pending_sync`.
   - All vectors and metadata are stored on local disk without cloud interaction.

### Step 3: Deliberate Local-vs-Cloud Data Policy
1. On the **"Log Observation"** tab, click **"+ Local Policy Draft"**.
2. Notice the checkbox **"Deliberate Local-Only Policy: Keep local until reviewed"** is checked.
3. Commit the entry.
4. On the **"Device Memory Inspector"**, see that this entry is tagged `local_only` (Held by Policy) and will not be pushed during automatic sync.

### Step 4: Reconnect & Automatic Delta Sync
1. In the header or sync card, click **"Disable Airplane Mode"** (Reconnect LAN).
2. The platform automatically detects network re-establishment and triggers a delta sync session.
3. Observe the activity ticker:
   - *"Sync Session Successful: Pushed 1 | Pulled X | Conflicts 1"*.
   - The pending queue clears, and entries transition to `synced`.

### Step 5: Safety Conflict Reconciliation (Central Office)
1. In the header mode switcher, click **"Central Office (Cloud)"**.
2. Notice the red alert badge **"1 Pending Safety Conflict"**.
3. Under the **"Conflict Reconciliation Queue"**, view the conflicting procedure for `PRESS-03`:
   - **Version A** (Dave Miller, Kiosk-1): Strict LOTO with 10-minute cool-down and zero-energy gauge verification.
   - **Version B** (Frank Briggs, Kiosk-2): High-flow dump valve shortcut bypassing interlock sensors.
4. Read the **Groq LLaMA Plain-Language Reasoning Card**:
   - *Critical Differences*: Identifies sensor bypass and omitted 10-minute thermal wait.
   - *Safety Risk*: High risk of high-pressure fluid injection and thermal burns.
   - *Recommended Action*: Enforce Version A's lockout protocols; reject sensor override.
5. Click **"Pick Version A (Enforce Master)"** or **"Merge Manually"**.
6. The conflict is marked resolved, and the master standard updates in the central Qdrant database!

---

## 6. Project Structure

```
PlantMind-Edge/
├── README.md                      # Complete architecture & walkthrough documentation
├── requirements.txt               # Python package dependencies
├── seed_data.py                   # Automated seeder for EdgeShards & Central Qdrant
│
├── qdrant_edge/                   # Core Qdrant Edge local shard library
│   ├── __init__.py
│   ├── models.py                  # KnowledgeEntry, ConflictRecord, SyncDelta models
│   ├── shard.py                   # EdgeShard persistent HNSW vector store & queue
│   └── embeddings.py              # FastEmbed BGE ONNX local pipeline + fallback
│
├── edge_api/                      # Edge Node FastAPI service (Port 8000)
│   ├── config.py                  # Edge configuration & offline mode simulation
│   ├── sync_client.py             # Delta synchronizer & conflict marker
│   └── main.py                    # Edge search, write, memory inspect endpoints
│
├── cloud_api/                     # Central Cloud FastAPI service (Port 8001)
│   ├── config.py                  # Cloud configuration (Qdrant, Groq, Supabase)
│   ├── central_store.py           # Central Qdrant vector & metadata repository
│   ├── conflict_engine.py         # Groq LLaMA reasoning & conflict evaluator
│   ├── sync_handler.py            # Push/pull delta handler & session recorder
│   └── main.py                    # Cloud admin REST API
│
└── frontend/                      # Next.js 16 + TypeScript PWA
    ├── public/
    │   ├── manifest.json          # PWA manifest
    │   └── sw.js                  # Service Worker shell caching
    └── src/
        ├── app/
        │   ├── layout.tsx         # PWA Root layout & telemetry metadata
        │   ├── page.tsx           # Kiosk vs Cloud dual-view application
        │   └── globals.css        # Rugged industrial design system
        ├── components/
        │   ├── NavigationHeader.tsx            # Header, mode switcher, offline toggle
        │   ├── KioskSearch.tsx                 # Offline search, voice input, cards
        │   ├── KioskWrite.tsx                  # Append-only entry authoring
        │   ├── DeviceMemoryInspector.tsx       # Local memory inspection & policy
        │   ├── SyncControl.tsx                 # Delta sync controls & counters
        │   ├── ActivityFeed.tsx                # Live system telemetry ticker
        │   ├── CloudConflictReconciliation.tsx # Groq LLaMA diff & conflict resolver
        │   └── CloudKnowledgeExplorer.tsx      # Master knowledge repository
        └── lib/
            ├── api.ts             # Typed client for Edge (8000) & Cloud (8001)
            └── types.ts           # Shared TypeScript models
```

---

## 7. Deliverables & Assumptions

1. **Self-Contained Offline Execution**: Embedded Qdrant Edge (`EdgeShard`) and FastEmbed run on CPU without requiring an external Docker container or Internet access during offline mode.
2. **Groq LLaMA Integration**: When `GROQ_API_KEY` is provided, conflict reasoning utilizes `llama-3.3-70b-versatile`. When running offline or without an API key, an intelligent local heuristic diff engine generates structured safety breakdowns.
3. **Multi-Kiosk Simulation**: The header includes a device switcher (`kiosk-1`, `kiosk-2`, `kiosk-3`) allowing full multi-device demonstration on a single laptop without needing multiple physical tablets.
