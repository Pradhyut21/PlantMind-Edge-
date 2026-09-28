import os
import subprocess
import time
import json
import shutil

def render_video():
    print("============================================================")
    print("RENDERING PLANTMIND EDGE PRO BRAG VIDEO (1080p, Indian Accent)")
    print("============================================================")
    start_time = time.time()

    output_dir = os.path.abspath("brag-output")
    frames_dir = os.path.join(output_dir, "slides")
    soundtrack = os.path.join(output_dir, "master_soundtrack.wav")
    timings_path = os.path.join(output_dir, "slide_timings.json")

    with open(timings_path, "r") as f:
        data = json.load(f)
        slides_info = data["slides"]

    # 1. Generate 30fps video clips for each slide matching exact audio duration
    clips = []
    print("\n--- Step 1: Rendering 1080p slide clips ---")
    for s in slides_info:
        idx = s["slide"]
        dur = s["slide_duration"]
        img_path = os.path.join(frames_dir, f"slide_{idx}.png")
        clip_path = os.path.join(output_dir, f"clip_{idx}.mp4")

        print(f"  Rendering Slide {idx} (duration: {dur:.2f}s)...")
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-c:v", "libx264",
            "-t", f"{dur:.2f}",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-vf", "scale=1920:1080",
            clip_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        clips.append(clip_path)

    # 2. Concat list file
    print("\n--- Step 2: Preparing concatenation list ---")
    concat_list_path = os.path.join(output_dir, "concat_list.txt")
    with open(concat_list_path, "w") as f:
        for c in clips:
            f.write(f"file '{c.replace(os.sep, '/')}'\n")

    # 3. Concatenate video clips with master soundtrack
    print("\n--- Step 3: Muxing video clips with master soundtrack ---")
    raw_video_path = os.path.join(output_dir, "brag_raw.mp4")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-i", soundtrack,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        raw_video_path
    ]
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"  Raw video muxed: {raw_video_path} ({os.path.getsize(raw_video_path)} bytes)")

    # 4. Extract best poster frame (Slide 4 Live Offline Search at ~85s)
    print("\n--- Step 4: Extracting poster frame ---")
    poster_path = os.path.join(output_dir, "brag.jpg")
    poster_cmd = [
        "ffmpeg", "-y",
        "-ss", "85.0",
        "-i", raw_video_path,
        "-frames:v", "1",
        "-q:v", "2",
        poster_path
    ]
    subprocess.run(poster_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"  Poster frame extracted to {poster_path} ({os.path.getsize(poster_path)} bytes)")

    # 5. Bake poster frame as frame 0 (per brag specification in step-4-deliver.md)
    print("\n--- Step 5: Baking poster frame 0 into final release ---")
    final_video_path = os.path.join(output_dir, "brag.mp4")
    bake_cmd = [
        "ffmpeg", "-y",
        "-i", raw_video_path,
        "-i", poster_path,
        "-filter_complex", "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]",
        "-map", "[v]",
        "-map", "0:a",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        final_video_path
    ]
    subprocess.run(bake_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"  Final video created: {final_video_path} ({os.path.getsize(final_video_path)} bytes)")

    # 6. Copy to public/ for web app access and docs/video/
    os.makedirs("public/video", exist_ok=True)
    os.makedirs("docs/video", exist_ok=True)
    shutil.copy2(final_video_path, "public/brag.mp4")
    shutil.copy2(poster_path, "public/brag.jpg")
    shutil.copy2(final_video_path, "docs/video/plantmind_edge_demo.mp4")
    shutil.copy2(poster_path, "docs/video/poster.jpg")
    print("  Copied artifacts to public/ and docs/video/")

    # Clean up intermediate files
    for c in clips:
        if os.path.exists(c):
            os.remove(c)
    if os.path.exists(concat_list_path):
        os.remove(concat_list_path)
    if os.path.exists(raw_video_path):
        os.remove(raw_video_path)

    elapsed = time.time() - start_time
    print(f"\nRender completed in {elapsed:.1f}s! Video ready at {final_video_path}")

if __name__ == "__main__":
    render_video()
