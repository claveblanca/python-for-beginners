"""
Packaging and Distribution
===========================

This file shows two approaches to packaging a Python project:

  1. The classic setup.py (setuptools)
  2. The modern pyproject.toml (PEP 621)

It also demonstrates how to build distribution artifacts (.whl, .tar.gz)
and what ``pip install -e .`` actually does.

IMPORTANT — setup.py is still valid, but the community is moving to
pyproject.toml.  Both approaches are shown below.

Quick start:

    # Editable install (for development):
    pip install -e .

    # Build distribution artifacts:
    pip install build
    python -m build

    # This creates:
    #   dist/
    #     chapter09-0.1.0-py3-none-any.whl     (wheel — fast install)
    #     chapter09-0.1.0.tar.gz                (source distribution)
"""

from setuptools import setup, find_packages

setup(
    # ── identity ──────────────────────────────────────────────────────
    name="chapter09",
    version="0.1.0",
    description="Chapter 9 — Introduction to Libraries (Python Beginner Book)",
    author="Python Beginner Book",
    url="https://github.com/example/python-beginner-book",

    # ── what to include ───────────────────────────────────────────────
    py_modules=[
        "main",
        "settings",
        "installing_packages",
        "using_libraries",
        "virtual_environments",
    ],

    # ── dependencies ──────────────────────────────────────────────────
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "full": [
            "requests",
            "rich",
            "python-dateutil",
        ],
        "dev": [
            "build",
            "twine",
            "pytest",
        ],
    },

    # ── console entry points ──────────────────────────────────────────
    entry_points={
        "console_scripts": [
            "chapter09=main:main",
        ],
    },

    # ── PyPI classifiers (metadata for the package index) ─────────────
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)


# ══════════════════════════════════════════════════════════════════════════
# Below is the equivalent pyproject.toml content (for reference).
# In a real project you would use ONE of these, not both.
# ══════════════════════════════════════════════════════════════════════════
PYPROJECT_TOML_EXAMPLE = """\
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "chapter09"
version = "0.1.0"
description = "Chapter 9 — Introduction to Libraries"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

dependencies = []

[project.optional-dependencies]
full = [
    "requests",
    "rich",
    "python-dateutil",
]
dev = [
    "build",
    "twine",
    "pytest",
]

[project.scripts]
chapter09 = "main:main"
"""


if __name__ == "__main__":
    from pathlib import Path
    import textwrap

    print("Packaging and Distribution")
    print("=" * 55)
    print()

    # ── 1. What setup.py does ─────────────────────────────────────────
    print("--- 1. What setup.py does ---")
    print()
    print("  setup.py tells pip/setuptools about your project:")
    print("    • name, version, description")
    print("    • which .py files to include")
    print("    • dependencies (install_requires)")
    print("    • console entry points (CLI commands)")
    print()

    # ── 2. Editable install ──────────────────────────────────────────
    print("--- 2. Editable install (pip install -e .) ---")
    print()
    print("  pip install -e .")
    print()
    print("  This installs your project in 'development mode':")
    print("    • No need to reinstall after every code change")
    print("    • Entry points (chapter09) become available")
    print("    • Great for development")
    print()

    # ── 3. Building artifacts ─────────────────────────────────────────
    print("--- 3. Building distribution artifacts ---")
    print()
    print("  pip install build")
    print("  python -m build")
    print()
    print("  Creates dist/ with:")
    print("    chapter09-0.1.0-py3-none-any.whl   # wheel (binary)")
    print("    chapter09-0.1.0.tar.gz              # sdist (source)")
    print()
    print("  Wheel (.whl) = fast install, no build step")
    print("  Sdist (.tar.gz) = source code, needs build step")
    print()

    # ── 4. Publishing to PyPI ─────────────────────────────────────────
    print("--- 4. Publishing to PyPI ---")
    print()
    print("  pip install twine")
    print("  twine upload dist/*                   # upload to PyPI")
    print("  twine upload --repository testpypi dist/*   # test PyPI first")
    print()
    print("  Before publishing:")
    print("    1. Create an account at https://pypi.org")
    print("    2. Generate an API token")
    print("    3. twine prompts for credentials (or use .pypirc)")
    print()

    # ── 5. pyproject.toml (modern approach) ───────────────────────────
    print("--- 5. pyproject.toml (modern alternative) ---")
    print()
    print("  The Python community is moving from setup.py to pyproject.toml.")
    print("  Here is the equivalent config:")
    print()

    out = Path(__file__).parent / "_output"
    out.mkdir(exist_ok=True)
    example_path = out / "pyproject.toml"
    example_path.write_text(PYPROJECT_TOML_EXAMPLE)
    print(textwrap.indent(PYPROJECT_TOML_EXAMPLE, "  "))
    print(f"  Saved example to {example_path}")
    print()

    # ── 6. Project structure ──────────────────────────────────────────
    print("--- 6. Typical project layout ---")
    print()
    layout = textwrap.dedent("""\
        myproject/
        ├── pyproject.toml      # or setup.py
        ├── README.md
        ├── LICENSE
        ├── requirements.txt    # pinned deps for reproducibility
        ├── src/
        │   └── mypackage/
        │       ├── __init__.py
        │       └── core.py
        ├── tests/
        │   └── test_core.py
        └── .gitignore
    """)
    print(textwrap.indent(layout, "  "))

    # ── 7. Key commands summary ───────────────────────────────────────
    print("--- 7. Commands cheat sheet ---")
    print()
    commands = [
        ("pip install .",          "Install from current directory"),
        ("pip install -e .",       "Editable / development install"),
        ("pip install -e '.[dev]'","Editable + dev extras"),
        ("python -m build",       "Build wheel + sdist into dist/"),
        ("twine check dist/*",    "Validate built artifacts"),
        ("twine upload dist/*",   "Upload to PyPI"),
    ]
    for cmd, desc in commands:
        print(f"  {cmd:<30s} {desc}")
    print()

    print("=" * 55)
    print("Key ideas:  setup.py, pyproject.toml, pip install -e .,")
    print("            python -m build, wheel, sdist, twine, PyPI,")
    print("            entry_points, extras_require")
    print("=" * 55)
