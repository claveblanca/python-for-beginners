# Chapter 9 — Introduction to Libraries

Installing packages with pip, using popular third-party libraries, creating virtual environments, and packaging your own project for distribution.

## Prerequisites

- Python 3.10+ installed
- Completed [Chapter 8](../8/) (APIs and JSON)

## The files

| # | File | Topic |
|---|------|-------|
| 1 | `installing_packages.py` | pip install/uninstall, `pip freeze`, requirements.txt, version pinning, `importlib.metadata`, PyPI JSON API |
| 2 | `using_libraries.py` | Importing stdlib & third-party modules; demos of `requests`, `rich`, `python-dateutil`; finding new libraries |
| 3 | `virtual_environments.py` | Why venvs exist, creating/activating/deactivating, `sys.prefix`, workflow, `.gitignore`, alternatives |
| 4 | `main.py` | Argparse sub-commands: `greet`, `pip-info`, `pip-list`, `pip-freeze`, `venv-check` |
| 5 | `settings.py` | Shared configuration (app name, sample packages, PyPI URL) |
| 6 | `setup.py` | Packaging with setuptools, `pip install -e .`, building wheels/sdists, pyproject.toml reference, publishing to PyPI |

## How to run

```bash
cd 9

# Informational scripts
python installing_packages.py
python using_libraries.py
python virtual_environments.py

# CLI tool (argparse sub-commands)
python main.py greet --name Alice --verbose
python main.py pip-info pip
python main.py pip-list
python main.py pip-freeze --output _output/frozen.txt
python main.py venv-check

# Packaging demo
python setup.py            # explains packaging concepts
pip install -e .           # editable install (creates 'chapter09' command)
chapter09 greet --name You
```

## Optional dependencies

The scripts gracefully skip libraries that are not installed, but for full output:

```bash
pip install requests rich python-dateutil
```

## Concepts introduced

### Installing Packages with pip
- `pip install`, `pip uninstall`, `pip show`, `pip list`
- `pip freeze > requirements.txt` and `pip install -r requirements.txt`
- Version specifiers: `==`, `>=`, `~=`, ranges
- `importlib.metadata` — inspecting packages from Python
- PyPI JSON API

### Using Popular Libraries
- `import`, `from … import`, `import … as`
- `requests` — HTTP for humans
- `rich` — beautiful terminal output (tables, colors)
- `python-dateutil` — flexible date parsing
- stdlib gems: `json`, `pathlib`, `collections.Counter`
- Where packages live on disk (`__file__`)
- Finding new libraries (PyPI, Awesome Python, GitHub)

### Virtual Environments
- `python -m venv .venv`
- `source .venv/bin/activate` / `deactivate`
- `sys.prefix` vs `sys.base_prefix`
- Typical project workflow (create → activate → install → freeze → deactivate)
- `.gitignore` for venvs
- Alternatives: `virtualenv`, `conda`, `poetry`, `pipenv`, `uv`, `pyenv`

### Packaging and Distribution
- `setup.py` with `setuptools` — metadata, modules, dependencies, entry points
- `extras_require` (`[full]`, `[dev]`)
- `pip install -e .` — editable / development install
- `python -m build` — create `.whl` and `.tar.gz` in `dist/`
- `twine upload` — publish to PyPI
- `pyproject.toml` — the modern alternative (PEP 621)
- Typical project layout

## Technologies Used

- **pip** — Python package installer
- **venv** — built-in virtual environment manager
- **setuptools** — packaging and distribution
- **PyPI** — Python Package Index (queried via its JSON API)
- **`importlib`** / **`importlib.metadata`** — dynamic imports and package introspection
- Demo libraries: **`requests`**, **`rich`**, **`python-dateutil`**
