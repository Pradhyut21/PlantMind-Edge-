import asyncio
import os
import edge_tts

SLIDES_DATA = [
    {
        "index": 1,
        "title": "Welcome to PlantMind Edge",
        "narration": "Welcome to PlantMind Edge. An offline-first industrial knowledge continuity platform powered by Qdrant Edge. On modern manufacturing plant floors, connectivity is never guaranteed. PlantMind Edge brings real-time vector intelligence directly onto rugged edge tablets, ensuring mission-critical maintenance knowledge is always accessible."
    },
    {
        "index": 2,
        "title": "The $22,000 Per Minute Problem",
        "narration": "Every minute of downtime on an automotive stamping line costs twenty-two thousand dollars. That is over one point three million dollars an hour. Technicians face two brutal walls: factory floors are wireless dead zones where cloud AI fails, and senior technicians with decades of tribal knowledge are retiring every single day, taking critical plant memory with them."
    },
    {
        "index": 3,
        "title": "Architecture: Qdrant on the Floor",
        "narration": "PlantMind Edge solves this with a purpose-built edge architecture. We run an embedded Qdrant EdgeShard and a local FastEmbed ONNX model directly on the shop floor tablet. Queries are vectorized and matched against local HNSW vector indexes in under one hundred and fifty milliseconds on CPU, with zero reliance on cloud connectivity."
    },
    {
        "index": 4,
        "title": "Live Demo: Sub-150ms Offline Semantic Search",
        "narration": "Here is our live offline search in action. Notice the airplane mode indicator: the tablet is completely isolated from the internet. When the technician searches for 'hydraulic pressure dropping on Line 3 press', our local engine returns Dave Miller's tribal workaround in just one hundred and thirty-three milliseconds, cutting repair time from four hours down to twelve minutes."
    },
    {
        "index": 5,
        "title": "On-Floor Capture & Deliberate Data Policy",
        "narration": "Technicians can log immediate observations directly on the floor. PlantMind Edge provides deliberate data sovereignty. A technician can flag an unverified observation to 'keep local until reviewed', preventing unvalidated notes from polluting the central repository until peer review is complete."
    },
    {
        "index": 6,
        "title": "Constrained Device Memory & Footprint Inspector",
        "narration": "Industrial edge tablets have strict hardware limits. PlantMind Edge includes an on-device Memory Inspector that continuously monitors native EdgeShard health, Write-Ahead Logs, and pending sync queues, guaranteeing predictable performance on rugged floor hardware."
    },
    {
        "index": 7,
        "title": "Groq LLaMA: No Last-Write-Wins on Safety",
        "narration": "When tablets reconnect, conflicting offline updates are intelligently reconciled. Most edge databases rely on last-write-wins. In industrial manufacturing, last-write-wins on safety procedures creates unacceptable hazards. PlantMind Edge quarantines competing safety updates and invokes Groq LLaMA-3.3-70B to synthesize plain-language risk breakdowns."
    },
    {
        "index": 8,
        "title": "Enterprise Fleet & Transformational ROI",
        "narration": "From individual floor tablets to enterprise fleet management, PlantMind Edge scales seamlessly across multi-plant operations. Preventing just one two-hour downtime incident saves two point six million dollars, paying for PlantMind Edge across an entire enterprise. Capturing human expertise before it walks out the door. This is PlantMind Edge."
    }
]

VOICE = "en-IN-PrabhatNeural"  # Professional, articulate Indian English male voice

async def generate_all_audio():
    print(f"Generating Indian English audio using {VOICE}...")
    os.makedirs("brag-output/audio", exist_ok=True)
    os.makedirs("presentation/audio", exist_ok=True)

    for item in SLIDES_DATA:
        idx = item["index"]
        text = item["narration"]
        out_file1 = f"brag-output/audio/slide_{idx}.mp3"
        out_file2 = f"presentation/audio/slide_{idx}.mp3"
        
        print(f"Synthesizing Slide {idx}: {item['title']}...")
        tts = edge_tts.Communicate(text, VOICE, rate="+3%", volume="+0%")
        await tts.save(out_file1)
        
        # Copy to presentation/audio
        with open(out_file1, "rb") as f_in, open(out_file2, "wb") as f_out:
            f_out.write(f_in.read())
            
        print(f"  -> Saved {out_file1} ({os.path.getsize(out_file1)} bytes)")

    print("All slide narration audio generated successfully!")

if __name__ == "__main__":
    asyncio.run(generate_all_audio())
