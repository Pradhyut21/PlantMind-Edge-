# 🏭 PlantMind Edge

> **Offline-first industrial knowledge-continuity platform where factory-floor technicians search and update maintenance knowledge locally via Qdrant Edge, with intelligent, conflict-aware sync to a central Qdrant Server when connectivity returns.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Vector Engine: Qdrant Edge](https://img.shields.io/badge/Vector_DB-Qdrant_Edge-red.svg)](https://qdrant.tech)
[![AI Reasoning: Groq LLaMA-3.3-70B](https://img.shields.io/badge/Reasoning-Groq_LLaMA_3.3_70B-orange.svg)](https://groq.com)
[![Next.js: 16](https://img.shields.io/badge/Frontend-Next.js_16_PWA-black.svg)](https://nextjs.org)
[![FastAPI: 0.115](https://img.shields.io/badge/Backend-FastAPI-teal.svg)](https://fastapi.tiangolo.com)
[![Latency: Sub-150ms](https://img.shields.io/badge/Search_Latency-%3C150ms_Offline-emerald.svg)](#offline-search)
[![Offline Capable: 100%](https://img.shields.io/badge/Offline_Capable-100%25-blue.svg)](#architecture)

---

### 📚 Quick Links & Hackathon Documentation
| Document | Focus & Content |
| :--- | :--- |
| 🏆 **[`HACKATHON.md`](HACKATHON.md)** | **Official Submission Guide** — Problem statement alignment, judging criteria matrix, and 60-second verification instructions. |
| 🎙️ **[`PITCH.md`](PITCH.md)** | **3-Minute Pitch Script & Slide Deck** — Compelling presentation script, factory downtime ROI ($22k/min), and DeadMind knowledge continuity narrative. |
| 🛠️ **[`APPROACH_AND_CHALLENGES.md`](APPROACH_AND_CHALLENGES.md)** | **Engineering Deep-Dive & Post-Mortem** — Why Qdrant Edge, Windows symlink workarounds, deterministic n-gram vectorizer fallbacks, and safety guards. |

---


## 📸 Visual Showcase & UI Tour

### 1. Offline Semantic Search (< 150ms on Factory Floor)
> **Airplane Mode Active** — All queries hit the local on-device `EdgeShard` dense HNSW vector index with zero network dependencies. Spoken voice input or typed symptoms return ranked procedures, incident logs, and senior technician tribal tips.

![Offline Semantic Search](docs/screenshots/01_offline_search.png)

---

### 2. Append-Only Local Write Log & Deliberate Data Policy
> Technicians author field observations while offline. The entry is vectorized on CPU in ~5ms, committed to the local `EdgeShard`, and queued in `pending_write_queue.json`. Includes the **"Keep local until reviewed"** policy checkbox to prevent unverified drafts from broadcasting to the plant fleet.

![Append-Only Local Write](docs/screenshots/02_append_only_write.png)

---

### 3. Device Memory Inspector & On-Device Storage Metrics
> Provides transparent visibility into local device telemetry: physical disk usage, total entries, vector dimensions (384d), and breakdown of **Synced**, **Pending Sync**, and **Local-Only** entries. Includes an interactive catalog to toggle data policies directly per entry.

![Device Memory Inspector](docs/screenshots/03_device_memory_inspector.png)

---

### 4. Central Office Safety Conflict Reconciliation (Groq LLaMA-3.3-70B)
> When two technicians update a safety procedure offline, **PlantMind Edge strictly prohibits silent last-write-wins overwriting**. Diverging versions are queued for human review with a **Groq LLaMA-3.3-70B plain-language reasoning breakdown** of parameter differences, safety risks, and recommended actions.

![Conflict Reconciliation](docs/screenshots/04_conflict_reconciliation.png)

---

### 5. Central Knowledge Explorer & Fleet Node Inventory
> Knowledge managers oversee the master plant repository across all connected edge kiosks (`kiosk-1`, `kiosk-2`, `kiosk-3`). Provides global search, machine filtering, version lineage inspection, and live network status.

![Central Knowledge Explorer](docs/screenshots/05_central_knowledge_explorer.png)

---

## ⚡ Core Problem & Architectural Intent

### The Industrial Reality
Factory floors (stamping presses, 5-axis CNC cells, automated packaging bays) frequently suffer from severe RF shielding, dead zones, and zero Wi-Fi connectivity. When a high-tonnage press halts or a spindle chatters, technicians cannot wait on network connections or lose the irreplaceable tribal knowledge of retiring senior specialists.

### The Solution: Qdrant Edge-to-Cloud Workflow
1. **Edge Node = Source of Truth for Reads While Offline**: Every technician query hits the local `EdgeShard` first — queries never stall on network latency.
2. **Append-Only Staging**: Writes are appended to a persistent local transaction queue rather than destructive edits, ensuring conflict detection is mathematically deterministic.
3. **Intelligent Delta Sync**: When LAN connectivity is detected, the kiosk automatically negotiates a snapshot/delta exchange: pushing eligible local observations and pulling central updates.
4. **Safety Procedure Safeguard**: Procedures tagged `safety_procedure` are protected by a safety barrier: concurrent edits are never resolved by newest timestamp, but are escalated to the human reconciliation queue with AI reasoning.
5. **Deliberate Local-vs-Cloud Policy**: Technicians can explicitly mark sensitive notes as *"Keep local until reviewed"*, directly answering the mandate to dynamically decide what stays local vs. what syncs.

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────┐
│                  EDGE (Kiosk / Tablet)                 │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │     Next.js / TS Progressive Web App (PWA)       │  │
│  │  - Service Worker Shell Caching (sw.js)          │  │
│  │  - Offline Semantic Search & Voice Input         │  │
│  │  - Device Memory Inspector & Policy Controls     │  │
│  └──────────────────────────┬───────────────────────┘  │
│                             │ HTTP (Port 8000)         │
│  ┌──────────────────────────▼───────────────────────┐  │
│  │              FastAPI (edge_api)                  │  │
│  │  - On-Device Daemon (runs on kiosk box)          │  │
│  │  - Airplane Mode Network Simulator               │  │
│  │  - Staging Queue (pending_write_queue.json)      │  │
│  └──────────────────────────┬───────────────────────┘  │
│                             │                          │
│  ┌──────────────────────────▼───────────────────────┐  │
│  │        Qdrant Edge Engine (qdrant_edge)          │  │
│  │  - EdgeShard: Persistent local HNSW storage      │  │
│  │  - FastEmbed: 384d BGE ONNX local pipeline       │  │
│  │  - Deterministic n-gram offline fallback         │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────────────▲────────────────────────────┘
                            │
              Snapshot / Delta Sync Protocol
           (Auto-detected on LAN reconnection)
                            │
┌───────────────────────────▼────────────────────────────┐
│                 CLOUD (Central Office)                 │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │           FastAPI (cloud_api, Port 8001)         │  │
│  │  - Delta Processor & Snapshot Handler            │  │
│  │  - Device Registry & Fleet Synchronizer          │  │
│  │  - Central Audit & Event Telemetry Stream        │  │
│  └─────────────┬───────────────────────┬────────────┘  │
│                │                       │               │
│  ┌─────────────▼─────────┐   ┌─────────▼────────────┐  │
│  │ Qdrant Server         │   │ Groq LLaMA Engine    │  │
│  │ - Central Collection  │   │ - llama-3.3-70b      │  │
│  │ - Snapshot Compatible │   │ - Parameter Diffing  │  │
│  │ - Payload Filtering   │   │ - Safety Risk Reason │  │
│  └───────────────────────┘   └──────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack & Directory Structure

- **Frontend:** Next.js 16 (Turbopack, TypeScript, Service Worker PWA, Industrial Vanilla CSS)
- **Local Edge API:** Python 3.13 + FastAPI on Port `8000`
- **Central Cloud API:** Python 3.13 + FastAPI on Port `8001`
- **Local Vector DB:** Qdrant Edge (`qdrant-client` embedded local shard with HNSW cosine index)
- **Central Vector DB:** Qdrant Server / Embedded Central Qdrant snapshot-compatible
- **Embeddings Pipeline:** FastEmbed (ONNX BAAI/bge-small-en-v1.5, 384d, < 5ms CPU execution) + Deterministic fallback
- **AI Reasoning:** Groq LLaMA-3.3-70B for plain-language conflict diff and safety risk assessment

```
PlantMind-Edge/
├── README.md                      # Comprehensive documentation & visual showcase
├── requirements.txt               # Python backend dependencies
├── seed_data.py                   # Automated industrial dataset & conflict seeder
├── verify_demo.py                 # End-to-end automated integration test suite
├── capture_screenshots.py         # Playwright automated UI screenshot capture
│
├── docs/
│   └── screenshots/               # High-DPI captured application screenshots
│       ├── 01_offline_search.png
│       ├── 02_append_only_write.png
│       ├── 03_device_memory_inspector.png
│       ├── 04_conflict_reconciliation.png
│       └── 05_central_knowledge_explorer.png
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
        │   ├── page.tsx           # Dual-view application shell (Kiosk vs Cloud)
        │   └── globals.css        # Rugged industrial dark-mode design system
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
            └── types.ts           # Shared TypeScript models & runtime enums
```

---

## 🚀 Quick Start (Run Locally)

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Node.js 18+ (Tested on Node v22.18)

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/Pradhyut21/PlantMind-Edge.git
cd PlantMind-Edge

# Install Python backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Seed Realistic Industrial Knowledge & Demo Conflict
Populates the central repository and local EdgeShards (`kiosk-1`, `kiosk-2`) with OEM manuals, tribal tips, and the pre-configured divergent safety procedure:
```bash
python seed_data.py
```

### 4. Launch Services

Run the three services across terminal windows:

**Terminal 1 — Central Cloud API (Port 8001):**
```bash
python -m uvicorn cloud_api.main:app --host 127.0.0.1 --port 8001
```

**Terminal 2 — Edge Kiosk API (Port 8000):**
```bash
python -m uvicorn edge_api.main:app --host 127.0.0.1 --port 8000
```

**Terminal 3 — Next.js PWA Frontend (Port 3000):**
```bash
cd frontend
npm run dev
```

Open your browser to: **`http://localhost:3000`**

### 5. Run Automated Verification Test
Verify all 7 core edge-to-cloud features in one command:
```bash
python verify_demo.py
```

---

## 🎯 Step-by-Step Demo Walkthrough

Follow this 5-step script to reproduce the evaluated edge-to-cloud workflow:

### Step 1: Kiosk in Airplane Mode & Sub-150ms Offline Search
1. In the top-right header, click **"ONLINE (LAN)"** to toggle into **"OFFLINE (Airplane)"** mode.
2. Notice the glowing red banner confirming zero network calls:
   ```
   AIRPLANE MODE SIMULATED — Network severed. All reads & writes served 100% locally via Qdrant Edge (EdgeShard).
   ```
3. In the search input, type or speak:
   ```
   hydraulic pressure keeps dropping on line 3 press
   ```
4. Observe the result returned in **< 150ms** directly from the local `EdgeShard`. Notice the top match:
   - **Title:** *Tribal Knowledge: Line 3 Press Hydraulic Drop Under Deep Draw*
   - **Author:** Senior Master Tech Dave Miller (28 years experience)
   - **Match Score:** 78% Semantic Match
   - **Guidance:** *"Don't waste 4 hours purging the accumulator — swap the B-2 cartridge seal with the high-temp polyurethane ring in Bin 14."*

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
   - *"Sync Session Successful: Pushed 1 | Pulled 7 | Conflicts 0"*.
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

## 📡 API Reference

### Edge API (`http://127.0.0.1:8000`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check & device ID |
| `GET` | `/api/status` | Network mode, queue size, last sync |
| `POST` | `/api/network/toggle` | Toggles simulated airplane mode (`is_offline`) |
| `POST` | `/api/device/switch` | Switches active simulated kiosk (`kiosk-1`, `kiosk-2`, `kiosk-3`) |
| `GET` | `/api/search` | **100% Offline Semantic Search** on local `EdgeShard` (< 150ms) |
| `POST` | `/api/entries` | Staged local write with append-only log |
| `GET` | `/api/memory/inspect` | Returns storage bytes, breakdown, HNSW specs |
| `POST` | `/api/sync/trigger` | Manually or automatically kicks off snapshot/delta sync |
| `POST` | `/api/policy/toggle_local` | Toggles `keep_local_until_reviewed` per entry |

### Central Cloud API (`http://127.0.0.1:8001`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Cloud health & Qdrant/Groq readiness |
| `GET` | `/api/stats` | Global metrics, active kiosks, open conflicts |
| `POST` | `/api/sync/delta` | Receives edge delta, detects conflicts, returns cloud delta |
| `GET` | `/api/conflicts` | Lists open safety conflict records |
| `POST` | `/api/conflicts/{id}/resolve` | Resolves conflict via `winner_picked`, `merged`, or `both_annotated` |
| `POST` | `/api/conflicts/{id}/reason` | Triggers Groq LLaMA re-analysis of competing versions |
| `GET` | `/api/devices` | Lists registered edge nodes across the factory |
| `GET` | `/api/activity` | Live system-wide audit and telemetry log |

---

## ⚖️ License & Attribution

- Built under **MIT License** for the Google Antigravity & Qdrant Edge Hackathon.
- Author: **Pradhyut** ([github.com/Pradhyut21](https://github.com/Pradhyut21))
