"""
Reading and Writing Files
=========================

Python's built-in ``open()`` handles text and binary files.
Always use ``with`` so the file is closed automatically.

Run:
    python reading_writing_files.py

Files created in this script are placed in a ``_output/`` subfolder
so they are easy to find and clean up.
"""

from __future__ import annotations

import os
from pathlib import Path

OUT = Path(__file__).parent / "_output"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Writing a text file
# ---------------------------------------------------------------------------
print("--- 1. Writing a text file ---")

path = OUT / "hello.txt"
with open(path, "w") as f:
    f.write("Hello, file!\n")
    f.write("This is line 2.\n")
    f.write("And line 3.\n")

print(f"  Wrote {path}")
print()

# ---------------------------------------------------------------------------
# 2. Reading the whole file at once
# ---------------------------------------------------------------------------
print("--- 2. Reading the whole file ---")

with open(path) as f:
    content = f.read()
print(f"  Content:\n{content}")

# ---------------------------------------------------------------------------
# 3. Reading line by line
# ---------------------------------------------------------------------------
print("--- 3. Reading line by line ---")

with open(path) as f:
    for i, line in enumerate(f, 1):
        print(f"  Line {i}: {line.rstrip()!r}")
print()

# ---------------------------------------------------------------------------
# 4. readlines() — list of lines
# ---------------------------------------------------------------------------
print("--- 4. readlines() ---")

with open(path) as f:
    lines = f.readlines()
print(f"  lines = {lines}")
print()

# ---------------------------------------------------------------------------
# 5. Appending to a file
# ---------------------------------------------------------------------------
print("--- 5. Appending ---")

with open(path, "a") as f:
    f.write("Appended line 4.\n")

with open(path) as f:
    print(f"  After append:\n{f.read()}")

# ---------------------------------------------------------------------------
# 6. writelines()
# ---------------------------------------------------------------------------
print("--- 6. writelines() ---")

path2 = OUT / "numbers.txt"
lines = [f"{n}\n" for n in range(1, 6)]
with open(path2, "w") as f:
    f.writelines(lines)

with open(path2) as f:
    print(f"  {path2.name}: {f.read().strip()!r}")
print()

# ---------------------------------------------------------------------------
# 7. File modes summary
# ---------------------------------------------------------------------------
print("--- 7. File modes ---")
modes = {
    "r": "read (default, file must exist)",
    "w": "write (creates or truncates)",
    "a": "append (creates or adds to end)",
    "x": "exclusive create (fails if exists)",
    "rb": "read binary",
    "wb": "write binary",
}
for mode, desc in modes.items():
    print(f"  {mode:4s} — {desc}")
print()

# ---------------------------------------------------------------------------
# 8. Checking if a file exists
# ---------------------------------------------------------------------------
print("--- 8. File existence ---")
print(f"  {path} exists? {path.exists()}")
print(f"  {path} is file? {path.is_file()}")
print(f"  nonexistent.txt exists? {Path('nonexistent.txt').exists()}")
print()

# ---------------------------------------------------------------------------
# 9. Using pathlib for paths
# ---------------------------------------------------------------------------
print("--- 9. pathlib basics ---")
p = Path("/home/user/docs/report.txt")
print(f"  Path        : {p}")
print(f"  .name       : {p.name}")
print(f"  .stem       : {p.stem}")
print(f"  .suffix     : {p.suffix}")
print(f"  .parent     : {p.parent}")
print()

# ---------------------------------------------------------------------------
# 10. Encoding
# ---------------------------------------------------------------------------
print("--- 10. Encoding ---")
path3 = OUT / "unicode.txt"
with open(path3, "w", encoding="utf-8") as f:
    f.write("Café, naïve, résumé\n")
with open(path3, encoding="utf-8") as f:
    print(f"  {f.read().strip()}")
print()

print("=" * 50)
print("Key ideas:  open(), with, read/write/append,")
print("            readlines, pathlib.Path, encoding")
print("=" * 50)
