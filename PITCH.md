# 🎙️ PlantMind Edge — Pitch Deck & 3-Minute Demo Script

> **"What happens when your best technician of 30 years retires tomorrow, and Line 3 halts in a Wi-Fi dead zone?"**
> 🎬 **Watch the 1080p Video:** [**`docs/video/plantmind_edge_demo.mp4`**](docs/video/plantmind_edge_demo.mp4) (Narrated by Prabhat in Indian English)  
> 📸 **Visual Application Tour:** [**`docs/screenshots/`**](docs/screenshots/) (5 High-DPI UI Tours)

---

## 🕒 The 3-Minute Pitch Script

### 0:00 - 0:30 — The Hook & The Problem
"Good afternoon, judges. 

Every minute of downtime on an automotive stamping line costs **~$22,000** (an illustrative industry benchmark representing ~$1.3M/hour in heavy automotive manufacturing). 

When Line 3 stalls, the technician pulls out their tablet to look up the fault. But they hit two brutal walls:
1. **The Factory Floor is a Wireless Dead Zone.** Concrete reinforced walls and electromagnetic shielding mean cloud-based AI tools are completely unreachable.
2. **The Tribal Knowledge Gap.** The OEM manual says *'purge the 110-bar accumulator'*, which takes 4 hours of lost production. But Dave Miller — the master tech who has worked that line for 28 years — knows you just need to swap the Viton bypass seal in Bin 14. 

Dave retires next month. When he walks out the door, his knowledge walks with him.

That is why we built **PlantMind Edge**."

---

### 0:30 - 1:15 — The Solution: PlantMind Edge
"PlantMind Edge is an offline-first industrial knowledge continuity platform powered by **official Qdrant Edge (`qdrant-edge-py 0.8.0`)**.

Instead of waiting on cloud connectivity, we run native **`qdrant_edge.EdgeShard`** instances directly on rugged shop-floor tablets and kiosks. 

When a technician speaks or types a symptom — like *'hydraulic pressure keeps dropping on Line 3 press'* — our local ONNX embedding engine vectors the query on-device and searches the local HNSW vector index in **sub-second latency (<150ms warm)**. 

Right at the top of their screen, Dave's tribal knowledge appears alongside OEM manuals and past incident logs. With zero Wi-Fi, the technician fixes the press in 12 minutes instead of 4 hours."

---

### 1:15 - 2:00 — Live Demo: Offline Write, Policy, and Auto-Sync
"Let me show you how it works in real-time.

1. **Demonstrable Offline Reality:** We toggle the kiosk into Airplane Mode. Notice the glowing banner. The tablet has zero internet access.
2. **Persistent Staging Write:** The technician logs a new finding about pilot valve cavitation. It is embedded and saved directly to the local EdgeShard.
3. **Deliberate Data Policy:** The technician can mark experimental observations as *'Keep local until reviewed'*. It stays on this tablet only — no premature cloud leaks.
4. **Auto Delta Sync:** The technician walks back into the maintenance bay where LAN connects. PlantMind Edge detects connectivity automatically and negotiates a snapshot/delta sync — pushing local observations and pulling central updates without requiring a manual click."

---

### 2:00 - 2:40 — The Safety Secret: Groq LLaMA Conflict Reasoning
"Now comes the hardest part of edge AI: **conflicting offline updates**.

Suppose two technicians on opposite shifts updated the same safety depressurization procedure while both were offline. One added a digital sensor check; the other bypassed an interlock switch to speed up tool changes.

Most software uses 'last-write-wins'. On a factory floor, **last-write-wins creates unacceptable risk on industrial safety procedures**.

In PlantMind Edge, safety procedures are hard-blocked from auto-overwriting. They are quarantined and routed to the central office with an automated **Groq LLaMA-3.3-70B reasoning breakdown**. 

The knowledge manager sees:
- The exact parameter differences (omitted 10-minute cool-down).
- The safety risk (500-bar fluid injection and flash fire).
- The recommended action (Enforce Version A, reject bypass).

With one click, the manager reconciles the master standard, and it synchronizes back across the plant fleet."

---

### 2:40 - 3:00 — The Vision & Business Value
"PlantMind Edge isn't just a vector database demo — it is the future of edge-to-cloud industrial intelligence.

- **Market Opportunity:** Experienced technicians are retiring across heavy industry, taking unwritten troubleshooting wisdom with them.
- **Downtime Avoidance:** A single prevented 2-hour downtime incident saves $2.6M in lost throughput, easily justifying plant-wide edge intelligence.

With Qdrant Edge, local AI is no longer a luxury. It is an operational necessity.

Thank you. We welcome your questions."

---

## 📊 Pitch Deck Slide Outline

| Slide # | Slide Title | Key Visual | Supporting Message |
| :---: | :--- | :--- | :--- |
| **1** | **PlantMind Edge** | Logo, Dark rugged UI badge, Qdrant Edge banner | Offline-First Industrial Knowledge Continuity |
| **2** | **The $22,000/Minute Problem** | Factory floor, 'No Internet Connection' error | Wi-Fi dead zones + retirement knowledge loss on plant floors |
| **3** | **The Solution: Qdrant on the Floor** | Architecture diagram (Edge tablet ↔ Cloud API) | Local EdgeShard with sub-second semantic search on-device |
| **4** | **Demonstrably Offline** | Screenshot: Airplane mode with <150ms warm latency | FastEmbed ONNX 384d running on CPU with zero cloud calls |
| **5** | **Deliberate Data Sovereignty** | Screenshot: 'Keep Local Until Reviewed' policy | Technicians decide what stays local vs. what syncs |
| **6** | **Device Memory Telemetry** | Screenshot: Storage breakdown (~14–130 MB shard) | Native shard telemetry, WAL tracking, and memory bounds |
| **7** | **No Silent Safety Overwrites** | Screenshot: Groq LLaMA diff analysis & risk report | Guarding human safety: critical updates require review |
| **8** | **Engineering Proof (7/7 Pass)** | Verification matrix & validated environment box | Programmatic verification passed end-to-end with exit code 0 |
| **9** | **Downtime Avoidance & Scale** | Avoided downtime model ($2.6M per 2-hour outage) | Enterprise deployment across multi-plant fleet facilities |
