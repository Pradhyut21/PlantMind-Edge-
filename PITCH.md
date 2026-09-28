# 🎙️ PlantMind Edge — Pitch Deck & 3-Minute Demo Script

> **"What happens when your best technician of 30 years retires tomorrow, and Line 3 halts in a Wi-Fi dead zone?"**
>
> 🎬 **Watch the 1080p Video:** [**`brag-output/brag.mp4`**](brag-output/brag.mp4) (Narrated by Prabhat in Indian English)  
> 🖥️ **Interactive White-Theme Slide Deck:** [**`presentation/index.html`**](presentation/index.html) or [**`http://localhost:3000/presenter.html`**](http://localhost:3000/presenter.html)

---

## 🕒 The 3-Minute Pitch Script

### 0:00 - 0:30 — The Hook & The Problem
"Good afternoon, judges. 

Every minute of downtime on an automotive stamping line costs **$22,000**. That’s over $1.3 million an hour. 

When Line 3 stalls, the technician pulls out their tablet to look up the fault. But they hit two brutal walls:
1. **The Factory Floor is a Wireless Dead Zone.** Concrete reinforced walls and electromagnetic shielding mean cloud-based AI tools are completely useless.
2. **The Tribal Knowledge Gap.** The OEM manual says *'purge the 110-bar accumulator'*, which takes 4 hours of lost production. But Dave Miller — the master tech who has worked that line for 28 years — knows you just need to swap the Viton bypass seal in Bin 14. 

Dave retires next month. When he walks out the door, his knowledge walks with him.

That is why we built **PlantMind Edge**."

---

### 0:30 - 1:15 — The Solution: PlantMind Edge
"PlantMind Edge is an offline-first industrial knowledge continuity platform powered by **Qdrant Edge**.

Instead of waiting on cloud connectivity, we run an embedded **Qdrant EdgeShard** directly on rugged shop-floor tablets and kiosks. 

When a technician speaks or types a symptom — like *'hydraulic pressure keeps dropping on Line 3 press'* — our local ONNX embedding engine vectors the query on-device and searches the local HNSW vector index in **under 150 milliseconds**. 

Right at the top of their screen, Dave's tribal knowledge appears alongside OEM manuals and past incident logs. With zero Wi-Fi, the technician fixes the press in 12 minutes instead of 4 hours."

---

### 1:15 - 2:00 — Live Demo: Offline Write, Policy, and Auto-Sync
"Let me show you how it works in real-time.

1. **Demonstrable Offline Reality:** We toggle the kiosk into Airplane Mode. Notice the glowing banner. The tablet has zero internet access.
2. **Append-Only Local Write:** The technician logs a new finding about pilot valve cavitation. It is embedded and saved directly to the local EdgeShard.
3. **Deliberate Data Policy:** The technician can mark experimental observations as *'Keep local until reviewed'*. It stays on this tablet only — no premature cloud leaks.
4. **Auto Delta Sync:** The technician walks back into the maintenance bay where LAN connects. PlantMind Edge detects connectivity automatically and negotiates a snapshot/delta sync — pushing local observations and pulling central updates without requiring a manual click."

---

### 2:00 - 2:40 — The Safety Secret: Groq LLaMA Conflict Reasoning
"Now comes the hardest part of edge AI: **conflicting offline updates**.

Suppose two technicians on opposite shifts updated the same safety depressurization procedure while both were offline. One added a digital sensor check; the other bypassed an interlock switch to speed up tool changes.

Most software uses 'last-write-wins'. On a factory floor, **last-write-wins kills people**.

In PlantMind Edge, safety procedures are hard-blocked from auto-overwriting. They are routed to the central office with an automated **Groq LLaMA-3.3-70B reasoning breakdown**. 

The knowledge manager sees:
- The exact parameter differences (omitted 10-minute cool-down).
- The safety risk (500-bar fluid injection and flash fire).
- The recommended action (Enforce Version A, reject bypass).

With one click, the manager reconciles the master standard, and it synchronizes back across the plant fleet."

---

### 2:40 - 3:00 — The Vision & Business Value
"PlantMind Edge isn't just a vector database demo — it is the future of edge-to-cloud industrial intelligence.

- **Market Opportunity:** 10,000 senior manufacturing technicians retire every single day in North America.
- **ROI:** A single prevented 2-hour downtime incident saves $2.6M — paying for PlantMind Edge across an entire factory enterprise for life.

With Qdrant Edge, local AI is no longer a luxury. It is an operational necessity.

Thank you. We welcome your questions."

---

## 📊 Pitch Deck Slide Outline

| Slide # | Slide Title | Key Visual | Supporting Message |
| :---: | :--- | :--- | :--- |
| **1** | **PlantMind Edge** | Logo, Dark rugged UI badge, Qdrant Edge banner | Offline-First Industrial Knowledge Continuity |
| **2** | **The $22,000/Minute Problem** | Factory floor, 'No Internet Connection' error | Wi-Fi dead zones + 10,000 retiring baby-boomer technicians/day |
| **3** | **The Solution: Qdrant on the Floor** | Architecture diagram (Edge tablet ↔ Cloud API) | Local EdgeShard with <150ms semantic search on-device |
| **4** | **Demonstrably Offline** | Screenshot: Airplane mode with 133ms latency | FastEmbed ONNX 384d running on CPU without internet |
| **5** | **Deliberate Data Sovereignty** | Screenshot: 'Keep Local Until Reviewed' policy | Technicians decide what stays local vs. what syncs |
| **6** | **No Last-Write-Wins on Safety** | Screenshot: Groq LLaMA diff analysis & risk report | Guarding human safety against silent data overwrites |
| **7** | **Business Model & Market** | TAM: $14.2B Industrial AI / Connected Worker | Enterprise SaaS tier: $4,500/month per manufacturing facility |
| **8** | **The Future of Factory Intelligence** | Roadmap: Voice AI headsets, thermal sensor sync | PlantMind Edge: Capturing human knowledge before it is lost |
