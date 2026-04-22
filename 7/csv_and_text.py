"""
Working with CSV and Text Files
================================

CSV (Comma-Separated Values) is the most common format for tabular data.
Python's ``csv`` module handles reading and writing; for larger datasets
consider ``pandas`` (not covered here).

Run:
    python csv_and_text.py

Demo files are created inside ``_output/``.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

OUT = Path(__file__).parent / "_output"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Writing a CSV file
# ---------------------------------------------------------------------------
print("--- 1. Writing a CSV file ---")

csv_path = OUT / "students.csv"
header = ["name", "age", "grade", "score"]
rows = [
    ["Alice", 20, "A", 92],
    ["Bob", 22, "B", 78],
    ["Charlie", 21, "A", 95],
    ["Diana", 23, "C", 68],
    ["Eve", 20, "B", 82],
]

with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print(f"  Wrote {csv_path.name} ({len(rows)} rows)")
print()

# ---------------------------------------------------------------------------
# 2. Reading a CSV file (csv.reader)
# ---------------------------------------------------------------------------
print("--- 2. Reading with csv.reader ---")

with open(csv_path, newline="") as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i == 0:
            print(f"  Header: {row}")
        else:
            print(f"  Row {i}: {row}")
print()

# ---------------------------------------------------------------------------
# 3. Reading into dictionaries (csv.DictReader)
# ---------------------------------------------------------------------------
print("--- 3. csv.DictReader ---")

with open(csv_path, newline="") as f:
    reader = csv.DictReader(f)
    students = list(reader)

for s in students[:3]:
    print(f"  {s}")
print(f"  ... ({len(students)} total)")
print()

# ---------------------------------------------------------------------------
# 4. Writing with DictWriter
# ---------------------------------------------------------------------------
print("--- 4. csv.DictWriter ---")

csv_path2 = OUT / "products.csv"
products = [
    {"id": 1, "name": "Widget", "price": 9.99, "stock": 150},
    {"id": 2, "name": "Gadget", "price": 24.50, "stock": 80},
    {"id": 3, "name": "Doohickey", "price": 4.75, "stock": 300},
]

with open(csv_path2, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "price", "stock"])
    writer.writeheader()
    writer.writerows(products)

print(f"  Wrote {csv_path2.name}")
print()

# ---------------------------------------------------------------------------
# 5. Processing CSV data
# ---------------------------------------------------------------------------
print("--- 5. Processing CSV: statistics ---")

scores = [int(s["score"]) for s in students]
avg = sum(scores) / len(scores)
top = max(students, key=lambda s: int(s["score"]))
low = min(students, key=lambda s: int(s["score"]))

print(f"  Average score : {avg:.1f}")
print(f"  Highest       : {top['name']} ({top['score']})")
print(f"  Lowest        : {low['name']} ({low['score']})")
print()

# ---------------------------------------------------------------------------
# 6. Filtering and writing a new CSV
# ---------------------------------------------------------------------------
print("--- 6. Filtering rows ---")

honor = [s for s in students if int(s["score"]) >= 80]
honor_path = OUT / "honor_roll.csv"

with open(honor_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    writer.writerows(honor)

print(f"  Honor roll ({len(honor)} students) -> {honor_path.name}")
for s in honor:
    print(f"    {s['name']}: {s['score']}")
print()

# ---------------------------------------------------------------------------
# 7. Custom delimiters (TSV, semicolons)
# ---------------------------------------------------------------------------
print("--- 7. Custom delimiters ---")

tsv_path = OUT / "data.tsv"
with open(tsv_path, "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["city", "country", "population"])
    writer.writerow(["Rome", "Italy", 2_873_000])
    writer.writerow(["Paris", "France", 2_161_000])

with open(tsv_path, newline="") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        print(f"  {row}")
print()

# ---------------------------------------------------------------------------
# 8. Parsing a structured text file
# ---------------------------------------------------------------------------
print("--- 8. Parsing structured text ---")

log_text = """\
2026-04-10 08:00:01 INFO  Server started
2026-04-10 08:05:23 WARN  High memory usage
2026-04-10 08:10:45 ERROR Connection timeout
2026-04-10 08:12:00 INFO  Retry successful
"""

log_path = OUT / "server.log"
log_path.write_text(log_text)

with open(log_path) as f:
    for line in f:
        parts = line.split(maxsplit=3)
        if len(parts) == 4:
            date, time_, level, msg = parts
            print(f"  [{level:5s}] {date} {time_} — {msg.rstrip()}")
print()

# ---------------------------------------------------------------------------
# 9. CSV to JSON conversion
# ---------------------------------------------------------------------------
print("--- 9. CSV -> JSON ---")

json_path = OUT / "students.json"
with open(json_path, "w") as f:
    json.dump(students, f, indent=2)

print(f"  Converted {csv_path.name} -> {json_path.name}")
with open(json_path) as f:
    data = json.load(f)
    print(f"  First record: {data[0]}")
print()

# ---------------------------------------------------------------------------
# 10. Counting words in a text file
# ---------------------------------------------------------------------------
print("--- 10. Word count ---")

sample = OUT / "sample.txt"
sample.write_text(
    "Python is great. Python is simple.\n"
    "Learning Python is fun and Python is powerful.\n"
)

text = sample.read_text()
words = text.lower().split()
word_count: dict[str, int] = {}
for w in words:
    clean = w.strip(".,!?;:")
    word_count[clean] = word_count.get(clean, 0) + 1

for word, count in sorted(word_count.items(), key=lambda x: -x[1])[:5]:
    print(f"  {word:10s} {count}")
print()

print("=" * 50)
print("Key ideas:  csv.reader, csv.writer, DictReader,")
print("            DictWriter, delimiter, json.dump/load,")
print("            text parsing, word counting")
print("=" * 50)
