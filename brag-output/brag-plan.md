# 🎬 PlantMind Edge — Brag Video Production Plan

**Project:** PlantMind Edge (Offline-First Industrial Knowledge Continuity)  
**Hackathon Target:** Qdrant Edge Hackathon 2026  
**Theme:** Professional Executive White Theme  
**Voice Narration:** Indian English Neural Accent (`en-IN-PrabhatNeural`)  
**Resolution:** 1080p Full HD (1920x1080, 30fps)  
**Total Runtime:** ~3.5 minutes (8-Slide Executive Keynote)

---

## 1. Planning Rubric Answers

1. **What is the product?**  
   PlantMind Edge is an offline-first industrial knowledge continuity platform where factory technicians search and update tribal maintenance procedures locally via Qdrant Edge with intelligent, conflict-aware sync to a central Qdrant cloud server.

2. **What is the primary problem?**  
   Factory floors are wireless dead zones where cloud AI fails, and 10,000 senior technicians retire every day taking decades of unwritten workarounds with them. Downtime costs $22,000/minute.

3. **What is the core technical breakthrough?**  
   Embedding Qdrant EdgeShard and FastEmbed ONNX 384d directly on rugged shop floor tablets, achieving sub-150ms semantic search in Airplane Mode without internet access, coupled with Groq LLaMA-3.3-70B conflict reconciliation to prevent fatal last-write-wins overwrites.

4. **Who is the user?**  
   Industrial plant technicians, maintenance managers, and operations directors in automotive, aerospace, and continuous process manufacturing.

5. **What is the video format?**  
   Widescreen (16:9), 1920x1080 Full HD, HTML PPT Presenter recorded with live audio synchronization.

---

## 2. Beat-by-Beat Storyboard

| Scene | Duration | Slide Focus | Audio / Narration Beat |
|---|---|---|---|
| **Scene 1** | 25.4s | Welcome to PlantMind Edge | Keynote intro; offline-first reality on industrial shop floors; edge vector intelligence. |
| **Scene 2** | 27.1s | The $22,000/Minute Downtime Crisis | High stakes metrics: $22K/min downtime, 10,000 retiring techs/day, zero Wi-Fi on floor. |
| **Scene 3** | 26.7s | Architecture: Qdrant on the Floor | Rugged Edge Tablet (FastEmbed + Qdrant EdgeShard) ↔ Central Cloud (Qdrant + Groq LLaMA). |
| **Scene 4** | 27.7s | Live Demo: Sub-150ms Offline Search | Airplane Mode active, 133ms latency, Dave Miller's Viton bypass workaround found. |
| **Scene 5** | 22.4s | Append-Only Write & Data Policy | Technicians log observations directly; "Keep local until reviewed" deliberate data policy. |
| **Scene 6** | 25.3s | Constrained Device Memory Inspector | 184MB RAM usage, 14.2MB disk, automated TTL eviction ensuring zero crashes on tablets. |
| **Scene 7** | 30.0s | Groq LLaMA: No Last-Write-Wins | Critical safety block; LLaMA detects omitted cool-down and flags 500-bar fluid injection risk. |
| **Scene 8** | 26.8s | Enterprise Fleet & Transformational ROI | 18x ROI on one prevented outage, $14.2B market, fleet management, closing punchline. |

---

## 3. Audio & Music Specifications

- **Narration:** Microsoft Neural TTS (`en-IN-PrabhatNeural`) at natural pacing (+3%).
- **Soundtrack:** `happy-beats-business-moves-vol-1-by-ende-dot-app.mp3` ducked to volume 0.08 with 2.0s fade-in and 2.5s fade-out.
- **SFX:** UI switch `transition.ogg` synchronized across scene cuts.
- **Audio Master:** 44.1 kHz, 16-bit Stereo PCM WAV (`master_soundtrack.wav`).
