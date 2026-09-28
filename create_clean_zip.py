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
    ".idea"
}

EXCLUDE_EXTS = {
    ".pyc",
    ".pyo",
    ".log",
    ".tmp",
    ".swp",
    ".lock"
}

EXCLUDE_FILES = {
    "thumbs.db",
    ".ds_store",
    ".lock",
    "plantmind_edge_submission.zip",
    "plantmind_edge.zip"
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
                if file_lower in EXCLUDE_FILES:
                    continue
                if file_lower.endswith(".zip"):
                    continue

                abs_file_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_file_path, workspace_dir)

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
    print(f"Compression Ratio:  {(1 - compressed_size/total_uncompressed_bytes)*100:.1f}% space saved")
    print(f"Time Taken:         {elapsed:.1f}s")
    print("=" * 65)

if __name__ == "__main__":
    make_clean_zip()
