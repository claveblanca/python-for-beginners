"""
Using Popular Libraries
========================

Shows how to import and use some well-known third-party libraries.
Each section tries the import and gracefully skips if the library
is not installed, so the script always runs.

Install the optional libraries to see full output:
    pip install requests rich python-dateutil

Run:
    python using_libraries.py
"""

from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime

import settings


def _available(name: str) -> bool:
    """Check if a package can be imported."""
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# 1. How imports work
# ---------------------------------------------------------------------------
print("--- 1. How imports work ---")
print()
print("  import math              # import the whole module")
print("  from math import sqrt    # import one name")
print("  import math as m         # import with alias")
print()
print("  For third-party libs the process is the same,")
print("  but you must install them first with pip.")
print()

# Quick demo with stdlib
import math
print(f"  math.pi    = {math.pi}")
print(f"  math.sqrt  = {math.sqrt(144)}")
print()

from collections import Counter
words = "the cat sat on the mat the cat".split()
print(f"  Counter({words})")
print(f"  = {Counter(words)}")
print()

# ---------------------------------------------------------------------------
# 2. requests — HTTP for humans
# ---------------------------------------------------------------------------
print("--- 2. requests ---")

if _available("requests"):
    import requests

    print("  Installed! Making a test call...")
    try:
        r = requests.get("https://httpbin.org/get",
                         params={"chapter": "9"},
                         timeout=5)
        print(f"  Status : {r.status_code}")
        print(f"  Args   : {r.json().get('args', {})}")
    except Exception as e:
        print(f"  (network error: {e})")
else:
    print("  Not installed.  Run:  pip install requests")
print()

# ---------------------------------------------------------------------------
# 3. rich — beautiful terminal output
# ---------------------------------------------------------------------------
print("--- 3. rich ---")

if _available("rich"):
    from rich.console import Console
    from rich.table import Table
    from rich import print as rprint

    console = Console()
    console.print("[bold green]rich[/bold green] is installed!", style="italic")

    table = Table(title="Sample packages from settings")
    table.add_column("Package", style="cyan")
    table.add_column("Installed?", justify="center")
    for pkg in settings.SAMPLE_PACKAGES:
        ok = "Yes" if _available(pkg.replace("-", "_")) else "No"
        table.add_row(pkg, ok)
    console.print(table)
else:
    print("  Not installed.  Run:  pip install rich")
    print(f"  Packages in settings: {settings.SAMPLE_PACKAGES}")
print()

# ---------------------------------------------------------------------------
# 4. python-dateutil — powerful date parsing
# ---------------------------------------------------------------------------
print("--- 4. python-dateutil ---")

if _available("dateutil"):
    from dateutil import parser as dtparser
    from dateutil.relativedelta import relativedelta

    samples = [
        "2025-04-12T15:30:00Z",
        "April 12, 2025 3:30 PM",
        "12/04/2025",
        "next Friday",
    ]
    for s in samples:
        try:
            dt = dtparser.parse(s)
            print(f"  {s!r:35s} -> {dt}")
        except Exception:
            print(f"  {s!r:35s} -> (could not parse)")

    now = datetime.now()
    future = now + relativedelta(months=3, days=10)
    print(f"\n  3 months + 10 days from now: {future.strftime('%Y-%m-%d')}")
else:
    print("  Not installed.  Run:  pip install python-dateutil")
print()

# ---------------------------------------------------------------------------
# 5. json (stdlib) — always available
# ---------------------------------------------------------------------------
print("--- 5. json (standard library — always available) ---")

data = {"chapter": 9, "topic": "libraries", "tags": ["pip", "venv", "packages"]}
pretty = json.dumps(data, indent=2)
print(f"  {pretty}")
print()

# ---------------------------------------------------------------------------
# 6. pathlib (stdlib) — modern file paths
# ---------------------------------------------------------------------------
print("--- 6. pathlib (standard library) ---")

from pathlib import Path

here = Path(__file__).parent
print(f"  This file   : {Path(__file__).name}")
print(f"  Parent dir  : {here}")
print(f"  .py files   : {[f.name for f in here.glob('*.py')]}")
print()

# ---------------------------------------------------------------------------
# 7. Where packages live on disk
# ---------------------------------------------------------------------------
print("--- 7. Where packages live ---")
print()

for name in ["pip", "json", "pathlib"]:
    try:
        mod = importlib.import_module(name)
        loc = getattr(mod, "__file__", "built-in")
        print(f"  {name:12s} -> {loc}")
    except ImportError:
        print(f"  {name:12s} -> not found")
print()

# ---------------------------------------------------------------------------
# 8. Finding new libraries
# ---------------------------------------------------------------------------
print("--- 8. Finding new libraries ---")
print()
print("  PyPI (package index)      : https://pypi.org")
print("  Awesome Python list       : https://awesome-python.com")
print("  GitHub trending (Python)  : https://github.com/trending/python")
print()
print("  Useful starter libraries:")
starter = [
    ("requests",        "HTTP requests"),
    ("rich",            "Beautiful terminal output"),
    ("python-dateutil", "Flexible date parsing"),
    ("click",           "CLI framework (alternative to argparse)"),
    ("pydantic",        "Data validation with type hints"),
    ("pytest",          "Testing framework"),
    ("black",           "Code formatter"),
    ("ruff",            "Fast linter"),
]
for pkg, desc in starter:
    print(f"    {pkg:<20s} {desc}")
print()

print("=" * 55)
print("Key ideas:  import, from … import, pip install,")
print("            requests, rich, dateutil, stdlib gems,")
print("            importlib, __file__, PyPI")
print("=" * 55)
