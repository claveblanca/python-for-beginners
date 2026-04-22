"""
Automating Repetitive Tasks
============================

Python replaces manual work: renaming files, organising folders,
processing batches, and scheduling simple jobs.

Run:
    python automation.py

Demo files are created inside ``_output/`` so nothing real is touched.
"""

from __future__ import annotations

import os
import shutil
import time
from datetime import datetime
from pathlib import Path

OUT = Path(__file__).parent / "_output"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Creating folders
# ---------------------------------------------------------------------------
print("--- 1. Creating folders ---")

dirs = ["reports", "logs", "backups"]
for d in dirs:
    p = OUT / d
    p.mkdir(exist_ok=True)
    print(f"  Created: {p}")
print()

# ---------------------------------------------------------------------------
# 2. Generating files in bulk
# ---------------------------------------------------------------------------
print("--- 2. Generating files in bulk ---")

for i in range(1, 6):
    path = OUT / "reports" / f"report_{i:03d}.txt"
    path.write_text(f"Report #{i}\nGenerated at {datetime.now()}\n")
    print(f"  Wrote {path.name}")
print()

# ---------------------------------------------------------------------------
# 3. Listing and filtering files
# ---------------------------------------------------------------------------
print("--- 3. Listing files ---")

all_txt = sorted((OUT / "reports").glob("*.txt"))
print(f"  .txt files in reports/: {[f.name for f in all_txt]}")
print()

# ---------------------------------------------------------------------------
# 4. Renaming files in batch
# ---------------------------------------------------------------------------
print("--- 4. Batch rename ---")

for f in all_txt:
    new_name = f.stem.replace("report_", "monthly_report_") + f.suffix
    new_path = f.parent / new_name
    f.rename(new_path)
    print(f"  {f.name} -> {new_name}")
print()

# ---------------------------------------------------------------------------
# 5. Moving files
# ---------------------------------------------------------------------------
print("--- 5. Moving files ---")

src = list((OUT / "reports").glob("monthly_report_001*"))[0]
dst = OUT / "backups" / src.name
shutil.move(str(src), str(dst))
print(f"  Moved {src.name} -> backups/")
print()

# ---------------------------------------------------------------------------
# 6. Copying files
# ---------------------------------------------------------------------------
print("--- 6. Copying files ---")

original = OUT / "backups" / "monthly_report_001.txt"
copy = OUT / "backups" / "monthly_report_001_copy.txt"
shutil.copy2(str(original), str(copy))
print(f"  Copied {original.name} -> {copy.name}")
print()

# ---------------------------------------------------------------------------
# 7. Deleting files safely
# ---------------------------------------------------------------------------
print("--- 7. Deleting files ---")

if copy.exists():
    copy.unlink()
    print(f"  Deleted {copy.name}")
print()

# ---------------------------------------------------------------------------
# 8. Walking a directory tree
# ---------------------------------------------------------------------------
print("--- 8. Walking a directory tree ---")

for root, dirs_list, files in os.walk(OUT):
    level = str(root).replace(str(OUT), ".").count(os.sep)
    indent = "  " * (level + 1)
    print(f"{indent}{Path(root).name}/")
    for fname in files:
        print(f"{indent}  {fname}")
print()

# ---------------------------------------------------------------------------
# 9. Simple timestamp logger
# ---------------------------------------------------------------------------
print("--- 9. Timestamp logger ---")

log_path = OUT / "logs" / "app.log"


def log(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a") as f:
        f.write(f"[{ts}] {message}\n")


log("Application started")
log("Processing batch")
log("Batch complete")

with open(log_path) as f:
    print(f.read())

# ---------------------------------------------------------------------------
# 10. Batch text replacement
# ---------------------------------------------------------------------------
print("--- 10. Batch text replacement ---")

for path in sorted((OUT / "reports").glob("*.txt")):
    text = path.read_text()
    new_text = text.replace("Report", "Summary")
    path.write_text(new_text)
    print(f"  Replaced 'Report' -> 'Summary' in {path.name}")
print()

print("=" * 50)
print("Key ideas:  pathlib, mkdir, glob, rename,")
print("            shutil (move/copy), os.walk,")
print("            batch processing, logging to file")
print("=" * 50)
