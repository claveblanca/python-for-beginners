"""
Installing Packages with pip
=============================

pip is the standard package installer for Python.
This script walks through all the things you can do with it, showing the
commands to run and — where possible — doing the equivalent from Python code.

Run:
    python installing_packages.py

No packages are actually installed by this script (it is safe to run).
"""

from __future__ import annotations

import importlib.metadata
import json
import subprocess
import sys
import textwrap
from pathlib import Path

OUT = Path(__file__).parent / "_output"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. What is pip?
# ---------------------------------------------------------------------------
print("--- 1. What is pip? ---")
print()
print("  pip = 'pip installs packages'")
print("  It downloads libraries from PyPI (https://pypi.org) and installs them.")
print()
print("  Verify it exists:")
print(f"    python -m pip --version")

result = subprocess.run(
    [sys.executable, "-m", "pip", "--version"],
    capture_output=True, text=True,
)
print(f"    {result.stdout.strip()}")
print()

# ---------------------------------------------------------------------------
# 2. Installing a package
# ---------------------------------------------------------------------------
print("--- 2. Installing a package ---")
print()
print("  Basic install (latest):")
print("    pip install requests")
print()
print("  Specific version:")
print("    pip install requests==2.31.0")
print()
print("  Minimum version:")
print("    pip install requests>=2.28")
print()
print("  From a Git repository:")
print("    pip install git+https://github.com/user/repo.git")
print()
print("  In editable / development mode (your own project):")
print("    pip install -e .")
print()

# ---------------------------------------------------------------------------
# 3. Uninstalling
# ---------------------------------------------------------------------------
print("--- 3. Uninstalling ---")
print()
print("    pip uninstall requests")
print("    pip uninstall -y requests   # skip confirmation")
print()

# ---------------------------------------------------------------------------
# 4. Listing installed packages
# ---------------------------------------------------------------------------
print("--- 4. Listing installed packages ---")
print()
print("  Command line:  pip list")
print("  From Python :  importlib.metadata.distributions()")
print()

dists = sorted(importlib.metadata.distributions(),
               key=lambda d: (d.metadata["Name"] or "").lower())
print(f"  You have {len(dists)} packages installed.  First 10:")
for d in dists[:10]:
    print(f"    {d.metadata['Name']:<30s} {d.metadata['Version']}")
print("    ...")
print()

# ---------------------------------------------------------------------------
# 5. pip freeze and requirements.txt
# ---------------------------------------------------------------------------
print("--- 5. pip freeze & requirements.txt ---")
print()
print("  Capture what is installed:")
print("    pip freeze > requirements.txt")
print()
print("  Install everything from that file:")
print("    pip install -r requirements.txt")
print()

lines = []
for d in dists:
    name = d.metadata["Name"]
    ver = d.metadata["Version"]
    if name:
        lines.append(f"{name}=={ver}")
lines.sort(key=str.lower)

req_path = OUT / "requirements.txt"
req_path.write_text("\n".join(lines) + "\n")
print(f"  Generated {req_path} with {len(lines)} entries.")
print(f"  First 5 lines:")
for line in lines[:5]:
    print(f"    {line}")
print("    ...")
print()

# ---------------------------------------------------------------------------
# 6. requirements.txt best practices
# ---------------------------------------------------------------------------
print("--- 6. requirements.txt best practices ---")
print()
example = textwrap.dedent("""\
    # requirements.txt — pin versions for reproducibility
    requests==2.31.0
    rich>=13.0,<14.0
    python-dateutil~=2.9

    # Version specifiers:
    #   ==2.31.0    exact version
    #   >=2.28      minimum version
    #   <3.0        maximum version
    #   ~=2.9       compatible release (>=2.9, <3.0)
    #   >=1.0,<2.0  range
""")
print(textwrap.indent(example, "  "))

example_path = OUT / "requirements_example.txt"
example_path.write_text(example)
print(f"  Saved example to {example_path.name}")
print()

# ---------------------------------------------------------------------------
# 7. pip show — inspect a single package
# ---------------------------------------------------------------------------
print("--- 7. pip show ---")
print()
print("  Command: pip show pip")

result = subprocess.run(
    [sys.executable, "-m", "pip", "show", "pip"],
    capture_output=True, text=True,
)
for line in result.stdout.strip().splitlines()[:6]:
    print(f"    {line}")
print()

# ---------------------------------------------------------------------------
# 8. Upgrading packages
# ---------------------------------------------------------------------------
print("--- 8. Upgrading ---")
print()
print("  Upgrade one package:")
print("    pip install --upgrade requests")
print()
print("  Upgrade pip itself:")
print("    python -m pip install --upgrade pip")
print()
print("  Check what is outdated:")
print("    pip list --outdated")
print()

# ---------------------------------------------------------------------------
# 9. Installing from different sources
# ---------------------------------------------------------------------------
print("--- 9. Installing from different sources ---")
print()
print("  Default (PyPI):")
print("    pip install requests")
print()
print("  Local wheel/tarball:")
print("    pip install ./dist/mypackage-1.0.0-py3-none-any.whl")
print("    pip install ./dist/mypackage-1.0.0.tar.gz")
print()
print("  Extra index:")
print("    pip install --extra-index-url https://test.pypi.org/simple/ mypackage")
print()
print("  From a requirements file:")
print("    pip install -r requirements.txt")
print()

# ---------------------------------------------------------------------------
# 10. Checking a package from PyPI (without installing)
# ---------------------------------------------------------------------------
print("--- 10. Querying PyPI ---")
print()
print("  PyPI has a JSON API.  Example for 'requests':")
print("    https://pypi.org/pypi/requests/json")
print()

try:
    from urllib.request import urlopen, Request
    url = "https://pypi.org/pypi/requests/json"
    req = Request(url, headers={"User-Agent": "python-beginner-book"})
    with urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode())
    info = data["info"]
    print(f"  Name    : {info['name']}")
    print(f"  Version : {info['version']}")
    print(f"  Summary : {info['summary']}")
    print(f"  License : {info.get('license', 'N/A')}")
except Exception as e:
    print(f"  (Could not reach PyPI: {e})")
print()

print("=" * 55)
print("Key ideas:  pip install/uninstall, pip freeze,")
print("            requirements.txt, version pinning,")
print("            pip show, pip list --outdated,")
print("            importlib.metadata, PyPI JSON API")
print("=" * 55)
