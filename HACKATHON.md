# 🏆 PlantMind Edge — Hackathon Submission Document

**Track:** Edge AI & Decentralized Semantic Intelligence  
**Author / Team:** Pradhyut ([github.com/Pradhyut21](https://github.com/Pradhyut21))  
**Project Name:** PlantMind Edge  
**Repository:** [github.com/Pradhyut21/PlantMind-Edge](https://github.com/Pradhyut21/PlantMind-Edge)  
**Live Demo:** Localhost (Ports 3000, 8000, 8001) with automated seed data  

---

## 1. Executive Summary

Manufacturing plants lose **$50B annually to unplanned equipment downtime**, largely because factory floors are wireless dead zones and retiring senior technicians take decades of unwritten "tribal knowledge" with them.

**PlantMind Edge** is an offline-first industrial knowledge continuity platform powered by **Qdrant Edge (`EdgeShard`)**. It equips plant-floor maintenance technicians with instant, on-device semantic search (< 150ms) across manuals, incident logs, and field observations — even in complete RF-shielded airplane mode. When connectivity is restored, PlantMind Edge orchestrates an intelligent snapshot/delta sync with a central Qdrant Server, using **Groq LLaMA-3.3-70B** to detect and reason through conflicting procedure updates before they can cause safety hazards.

---

## 2. Problem Statement Addressed

> *"Build an AI-powered edge intelligence platform using Qdrant Edge for local semantic memory and retrieval, that intelligently manages the relationship between on-device data and centralized cloud knowledge — offline-first, low-latency, dynamically decides what stays local vs. syncs, handles intermittent connectivity, resolves conflicting updates, and exposes a UI showing device memory, search results, sync status, and system activity."*

PlantMind Edge directly answers this brief with an end-to-end industrial product, avoiding superficial vector database demos by implementing real factory-floor realities:
- Zero-connectivity environments (stamping bays, subterranean utility tunnels)
- Append-only staging preventing silent data corruption
- Absolute safety rules (no last-write-wins on safety-critical lockout/tagout procedures)
- Granular technician policy controls (*"Keep local until reviewed"*)

---

## 3. Alignment with Judging Criteria

| Criterion | Requirement in Brief | PlantMind Edge Implementation | Proof Location |
| :--- | :--- | :--- | :--- |
| **Qdrant Edge Utilization** | Core vector engine running locally on-device | Implemented `EdgeShard` wrapping embedded Qdrant with persistent HNSW index, cosine similarity, and payload filtering | [`qdrant_edge/shard.py`](file:///d:/Cubicle/qdrant_edge/shard.py) |
| **Offline-First & Low Latency** | Demonstrably works without network (<200ms) | Achieves **133ms** local semantic search on CPU via FastEmbed ONNX BGE model with network severed | [`verify_demo.py`](file:///d:/Cubicle/verify_demo.py) Step 3 |
| **Intelligent Sync Protocol** | Snapshot / delta exchange between edge and cloud | Delta exchange protocol: pushes eligible local updates, pulls server delta, clears staged queue | [`edge_api/sync_client.py`](file:///d:/Cubicle/edge_api/sync_client.py) |
| **Conflict Detection & AI Reasoning** | Reject last-write-wins on safety procedures; reason through conflicts | Detects diverging versions, queues for review, and uses **Groq LLaMA-3.3-70B** to generate plain-language risk diffs | [`cloud_api/conflict_engine.py`](file:///d:/Cubicle/cloud_api/conflict_engine.py) |
| **Device Memory Inspector** | UI showing local memory, storage, and index health | Visual dashboard displaying storage bytes (56 KB), total vectors, and breakdowns | [`DeviceMemoryInspector.tsx`](file:///d:/Cubicle/frontend/src/components/DeviceMemoryInspector.tsx) |
| **Local vs. Cloud Policy** | Dynamically decide what stays local vs. what syncs | Explicit `keep_local_until_reviewed` policy field that isolates drafts from cloud sync | [`KioskWrite.tsx`](file:///d:/Cubicle/frontend/src/components/KioskWrite.tsx) |
| **UI Aesthetics & Polish** | Premium, high-wow-factor industrial interface | Rugged factory tablet dark mode, glowing telemetry indicators, waveform audio input, side-by-side diff | [`frontend/src/app/globals.css`](file:///d:/Cubicle/frontend/src/app/globals.css) |

---

## 4. Key Architectural Innovations

### 1. The Append-Only Staging Queue
Destructive writes on edge nodes make conflict detection impossible. PlantMind Edge writes new observations to a local append-only log (`pending_write_queue.json`) while indexing into `EdgeShard`. This guarantees that if a technician makes changes while offline, the original version vector is preserved to compute exact deltas during cloud synchronization.

### 2. Guardrailed Conflict Architecture
Many edge systems rely on naive "last-write-wins" (LWW). On a factory floor, LWW on an emergency depressurization procedure could lead to high-pressure hydraulic injection or worker fatalities. PlantMind Edge splits updates into two tracks:
- **Operational / Incident logs**: Auto-resolve to newest version while preserving history.
- **Safety Procedures (`safety_procedure`)**: Hard-blocked from auto-overwriting. Automatically routed to the human reconciliation queue with an automated Groq LLaMA risk assessment.

### 3. Deliberate Data Sovereignty Policy
Not all shop-floor notes are ready for company-wide deployment. PlantMind Edge implements an on-device data policy toggle (*"Keep local until reviewed"*). The sync client strictly filters these items out of outgoing deltas until the author or supervisor explicitly promotes them.

---

## 5. Technology Stack Summary

- **Frontend:** Next.js 16 (App Router, Turbopack, TypeScript, Vanilla CSS, Service Worker PWA)
- **Local Edge API:** FastAPI (Port 8000), running alongside the kiosk
- **Central Cloud API:** FastAPI (Port 8001), running centrally
- **Local Vector Engine:** Qdrant Edge (`qdrant-client` embedded local shard, HNSW dense index)
- **Cloud Vector Engine:** Qdrant Server (Central Collection)
- **Local Embedding Pipeline:** FastEmbed (ONNX BAAI/bge-small-en-v1.5, 384 dimensions)
- **Cloud LLM Reasoning:** Groq LLaMA-3.3-70B (`llama-3.3-70b-versatile`)
- **Testing & Tooling:** Playwright, HTTPX, Python 3.13, Node v22.18

---

## 6. How to Run the Evaluation in 60 Seconds

```bash
# 1. Clone repository
git clone https://github.com/Pradhyut21/PlantMind-Edge.git
cd PlantMind-Edge

# 2. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 3. Seed realistic industrial dataset & conflict
python seed_data.py

# 4. Run automated verification suite
python verify_demo.py
```

All 7 verification checkpoints will execute and pass synchronously.
