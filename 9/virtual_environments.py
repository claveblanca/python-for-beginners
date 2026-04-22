"""
Virtual Environments
====================

A virtual environment (venv) is an isolated Python installation.
Each project gets its own set of packages so they never conflict.

This script explains the concept, shows the commands, and probes
the current environment to illustrate the difference.

Run:
    python virtual_environments.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Why virtual environments?
# ---------------------------------------------------------------------------
print("--- 1. Why virtual environments? ---")
print()
print("  Problem:")
print("    Project A needs requests==2.28")
print("    Project B needs requests==2.31")
print("    If both share the system Python, one of them breaks.")
print()
print("  Solution:")
print("    Give each project its own isolated Python (a 'venv').")
print("    Each venv has its own pip and its own site-packages.")
print()

# ---------------------------------------------------------------------------
# 2. Creating a venv
# ---------------------------------------------------------------------------
print("--- 2. Creating a venv ---")
print()
print("  python -m venv .venv          # creates a folder called .venv")
print()
print("  What happens:")
print("    .venv/")
print("    ├── bin/           (Linux/Mac)  or  Scripts/  (Windows)")
print("    │   ├── python     (copy or symlink to the interpreter)")
print("    │   ├── pip")
print("    │   └── activate   (shell script to activate)")
print("    ├── lib/")
print("    │   └── pythonX.Y/")
print("    │       └── site-packages/   (empty at first)")
print("    └── pyvenv.cfg     (config: base Python, include-system-site)")
print()

# ---------------------------------------------------------------------------
# 3. Activating and deactivating
# ---------------------------------------------------------------------------
print("--- 3. Activating / deactivating ---")
print()
cmds = textwrap.dedent("""\
    Linux / macOS:
      source .venv/bin/activate
      deactivate

    Windows (cmd):
      .venv\\Scripts\\activate.bat
      deactivate

    Windows (PowerShell):
      .venv\\Scripts\\Activate.ps1
      deactivate

    Fish shell:
      source .venv/bin/activate.fish
      deactivate
""")
print(textwrap.indent(cmds, "  "))

print("  After activating, 'python' and 'pip' point to the venv copy.")
print()

# ---------------------------------------------------------------------------
# 4. Current environment info
# ---------------------------------------------------------------------------
print("--- 4. Your current environment ---")
print()

in_venv = sys.prefix != sys.base_prefix
venv_name = Path(sys.prefix).name if in_venv else "(system)"

print(f"  Python executable : {sys.executable}")
print(f"  sys.prefix        : {sys.prefix}")
print(f"  sys.base_prefix   : {sys.base_prefix}")
print(f"  VIRTUAL_ENV env   : {os.environ.get('VIRTUAL_ENV', '(not set)')}")
print(f"  In a venv?        : {'Yes — ' + venv_name if in_venv else 'No'}")
print()

# ---------------------------------------------------------------------------
# 5. Typical project workflow
# ---------------------------------------------------------------------------
print("--- 5. Typical workflow ---")
print()
workflow = textwrap.dedent("""\
    # 1. Create the project folder
    mkdir myproject && cd myproject

    # 2. Create a venv
    python -m venv .venv

    # 3. Activate it
    source .venv/bin/activate        # Linux/Mac
    .venv\\Scripts\\activate           # Windows

    # 4. Install what you need
    pip install requests rich

    # 5. Freeze for reproducibility
    pip freeze > requirements.txt

    # 6. Work on your code ...
    python main.py

    # 7. Deactivate when done
    deactivate

    # 8. Later (or on another machine):
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
""")
print(textwrap.indent(workflow, "  "))

# ---------------------------------------------------------------------------
# 6. .gitignore and venvs
# ---------------------------------------------------------------------------
print("--- 6. .gitignore ---")
print()
print("  NEVER commit the venv folder to Git.  Add to .gitignore:")
print()
print("    .venv/")
print("    venv/")
print("    __pycache__/")
print()
print("  Commit requirements.txt instead — that is the portable record")
print("  of what the project needs.")
print()

# ---------------------------------------------------------------------------
# 7. Alternatives to venv
# ---------------------------------------------------------------------------
print("--- 7. Alternatives ---")
print()
alternatives = [
    ("venv",       "Built-in (Python 3.3+), standard, always available"),
    ("virtualenv", "Third-party, faster venv creation, more features"),
    ("conda",      "Package + environment manager (popular in data science)"),
    ("poetry",     "Dependency manager + venv in one tool"),
    ("pipenv",     "pip + venv combined, uses Pipfile"),
    ("uv",         "Very fast Rust-based pip + venv replacement"),
    ("pyenv",      "Manages multiple Python versions (not a venv tool)"),
]
for name, desc in alternatives:
    print(f"  {name:<14s} {desc}")
print()

# ---------------------------------------------------------------------------
# 8. Quick demo: create a venv from Python
# ---------------------------------------------------------------------------
print("--- 8. Creating a venv from Python (demo) ---")
print()

demo_dir = Path(__file__).parent / "_output" / "demo_venv"
if demo_dir.exists():
    import shutil
    shutil.rmtree(demo_dir)

print(f"  Creating venv at {demo_dir} ...")

import venv
venv.create(str(demo_dir), with_pip=False)

cfg = demo_dir / "pyvenv.cfg"
if cfg.exists():
    print(f"  pyvenv.cfg contents:")
    for line in cfg.read_text().splitlines():
        print(f"    {line}")
else:
    print("  (pyvenv.cfg not found — venv module may be limited)")

pip_path = demo_dir / "bin" / "python"
if not pip_path.exists():
    pip_path = demo_dir / "Scripts" / "python.exe"

if pip_path.exists():
    print(f"\n  Python in demo venv: {pip_path}")

print()
print("  (This was just a demo — feel free to delete _output/demo_venv/)")
print()

# ---------------------------------------------------------------------------
# 9. Troubleshooting
# ---------------------------------------------------------------------------
print("--- 9. Common issues ---")
print()
issues = [
    ("'python -m venv' fails",
     "Ensure python3-venv is installed: sudo apt install python3-venv"),
    ("pip not found after activation",
     "Recreate: python -m venv --clear .venv"),
    ("Wrong Python version",
     "Specify: python3.12 -m venv .venv"),
    ("Permission denied on activate",
     "PowerShell: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned"),
    ("Packages still from system",
     "Make sure you activated: which python should show .venv path"),
]
for problem, fix in issues:
    print(f"  Problem : {problem}")
    print(f"  Fix     : {fix}")
    print()

print("=" * 55)
print("Key ideas:  python -m venv .venv, activate / deactivate,")
print("            sys.prefix vs sys.base_prefix,")
print("            requirements.txt, .gitignore, alternatives")
print("=" * 55)
