import os
import subprocess
import json
import soundfile as sf
import numpy as np

def build_soundtrack():
    print("Building synchronized master soundtrack for PlantMind Edge...")
    audio_dir = os.path.abspath("brag-output/audio")
    assets_dir = os.path.abspath("brag-output/assets")
    output_dir = os.path.abspath("brag-output")

    sr = 44100
    slide_durations = []

    # 1. Convert MP3 to standard 44100Hz stereo WAV
    wav_files = []
    for i in range(1, 9):
        mp3_path = os.path.join(audio_dir, f"slide_{i}.mp3")
        wav_path = os.path.join(audio_dir, f"slide_{i}.wav")
        cmd = [
            "ffmpeg", "-y", "-i", mp3_path,
            "-ar", "44100", "-ac", "2",
            wav_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        wav_files.append(wav_path)

        data, _ = sf.read(wav_path)
        dur = len(data) / sr
        slide_durations.append(dur)
        print(f"  Slide {i} narration: {dur:.2f}s")

    # 2. Compute exact slide timeline with 0.8s breathing room
    slide_timings = []
    current_time = 0.0
    pause_between = 0.8

    for i in range(8):
        start = current_time
        dur = slide_durations[i]
        end = start + dur
        slide_timings.append({
            "slide": i + 1,
            "start": round(start, 2),
            "narration_duration": round(dur, 2),
            "slide_duration": round(dur + pause_between, 2),
            "end": round(end, 2)
        })
        current_time = end + pause_between

    # Add 1.5s outro pause
    total_duration = current_time + 1.0
    print(f"Total Presentation Duration: {total_duration:.2f}s")

    # Save timings to JSON for video recorder
    timings_path = os.path.join(output_dir, "slide_timings.json")
    with open(timings_path, "w") as f:
        json.dump({
            "total_duration": total_duration,
            "slides": slide_timings
        }, f, indent=2)
    print(f"Saved slide timing manifest to {timings_path}")

    # 3. Create master narration buffer
    total_samples = int(total_duration * sr)
    master_narration = np.zeros((total_samples, 2), dtype=np.float32)

    for i, t in enumerate(slide_timings):
        data, _ = sf.read(wav_files[i])
        if len(data.shape) == 1:
            data = np.stack([data, data], axis=-1)
        
        start_idx = int(t["start"] * sr)
        end_idx = min(total_samples, start_idx + len(data))
        length = end_idx - start_idx
        master_narration[start_idx:end_idx] += data[:length] * 0.98

    narration_out = os.path.join(audio_dir, "master_narration.wav")
    sf.write(narration_out, master_narration, sr)
    print(f"Master narration saved: {narration_out}")

    # 4. Mix with Background Music & Transition SFX
    bg_music = os.path.join(assets_dir, "music", "bg_music.mp3")
    sfx_click = os.path.join(assets_dir, "sfx", "transition.ogg")
    master_soundtrack = os.path.join(output_dir, "master_soundtrack.wav")

    # Build filter complex for background music ducking & fade
    filter_complex = (
        f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration:.1f},"
        f"volume=0.08,afade=t=in:ss=0:d=2.0,afade=t=out:st={total_duration-2.5:.1f}:d=2.5[music];"
        f"[0:a]volume=1.0[voice];"
        f"[voice][music]amix=inputs=2:duration=first:dropout_transition=2[outa]"
    )

    cmd_mix = [
        "ffmpeg", "-y",
        "-i", narration_out,
        "-i", bg_music,
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        "-t", f"{total_duration:.2f}",
        "-ar", "44100",
        "-ac", "2",
        master_soundtrack
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Master soundtrack mixed successfully: {master_soundtrack} ({os.path.getsize(master_soundtrack)} bytes)")

if __name__ == "__main__":
    build_soundtrack()
