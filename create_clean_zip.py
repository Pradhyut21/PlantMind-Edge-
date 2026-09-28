import os
import zipfile
import time

EXCLUDE_DIRS = {
    "node_modules",
    ".next",
    ".git",
    "__pycache__",
    ".gemini",
    ".agents",
    ".vscode",
    ".idea",
    "data",  # Exclude runtime database directories (recreated by seed_data.py)
    "brag-output",
    "public",
}

EXCLUDE_EXTS = {
    ".pyc",
    ".pyo",
    ".log",
    ".tmp",
    ".swp",
    ".lock",
    ".wal",
    ".wav"  # Exclude raw uncompressed audio intermediates
}

EXCLUDE_FILES = {
    "thumbs.db",
    ".ds_store",
    ".lock",
    "plantmind_edge_submission.zip",
    "plantmind_edge.zip",
    # Exclude duplicate media copies (canonical copies exist in docs/video/ and presentation/)
    "frontend/public/brag.mp4",
    "public/brag.mp4",
    "brag-output/brag.mp4",
    "frontend/public/plantmind_edge_executive_deck.pptx",
    "public/plantmind_edge_executive_deck.pptx",
    "brag-output/plantmind_edge_executive_deck.pptx",
    "brag-output/assets/music/bg_music.mp3",
    "frontend/public/audio/bg_music.mp3",
    "brag-output/audio/bg_music.mp3",
}

def make_clean_zip(output_zip_name="PlantMind_Edge_Submission.zip"):
    start_time = time.time()
    workspace_dir = os.path.abspath(".")
    output_zip_path = os.path.join(workspace_dir, output_zip_name)

    print("=" * 65)
    print(f"CREATING CLEAN SUBMISSION ZIP ARCHIVE: {output_zip_name}")
    print("=" * 65)
    print("Excluding: node_modules, .next, .git, __pycache__, locks, logs...\n")

    files_added = 0
    total_uncompressed_bytes = 0

    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(workspace_dir):
            dirs[:] = [d for d in dirs if d.lower() not in EXCLUDE_DIRS]

            for file in files:
                file_lower = file.lower()
                _, ext = os.path.splitext(file_lower)

                if ext in EXCLUDE_EXTS:
                    continue

                abs_file_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_file_path, workspace_dir)
                rel_norm = rel_path.replace("\\", "/").lower()

                if file_lower in EXCLUDE_FILES or rel_norm in EXCLUDE_FILES:
                    continue
                if file_lower.endswith(".zip"):
                    continue

                # Prefix with project folder name for clean extraction
                archive_name = os.path.join("PlantMind_Edge", rel_path)

                try:
                    zipf.write(abs_file_path, archive_name)
                    files_added += 1
                    total_uncompressed_bytes += os.path.getsize(abs_file_path)

                    if files_added % 25 == 0:
                        print(f"  Added {files_added} files... ({archive_name})")
                except (PermissionError, OSError) as e:
                    print(f"  [Skipped locked file]: {rel_path}")

    compressed_size = os.path.getsize(output_zip_path)
    elapsed = time.time() - start_time

    print("\n" + "=" * 65)
    print("ZIP ARCHIVE CREATED SUCCESSFULLY!")
    print("=" * 65)
    print(f"Archive Path:       {output_zip_path}")
    print(f"Files Packaged:     {files_added} files")
    print(f"Uncompressed Size:  {total_uncompressed_bytes / (1024*1024):.2f} MB")
    print(f"Compressed Size:    {compressed_size / (1024*1024):.2f} MB")
    import shutil
    shutil.copy2(output_zip_path, os.path.join(workspace_dir, "PlantMind_Edge.zip"))
    print(f"Copied clean archive to: PlantMind_Edge.zip")
    print("=" * 65)

if __name__ == "__main__":
    make_clean_zip()
