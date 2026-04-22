"""
Chapter 9 — Introduction to Libraries
======================================

A single entry-point that demonstrates ``argparse`` sub-commands related to
pip, virtual environments, and third-party libraries.

Usage
-----
::

    python main.py greet --name Alice --verbose
    python main.py pip-info requests
    python main.py pip-list
    python main.py pip-freeze
    python main.py venv-check

After ``pip install -e .`` you can also run::

    chapter09 greet --name Alice
    chapter09 pip-info requests
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
import textwrap

import settings


# ── greet ─────────────────────────────────────────────────────────────────

def cmd_greet(args: argparse.Namespace) -> int:
    """Classic hello-world, kept from the original version."""
    who = args.name or settings.DEFAULT_AUDIENCE
    line = f"{settings.GREETING_PREFIX}, {who}!"
    print(line)
    if args.verbose:
        print(f"[{settings.APP_NAME}] said that to {who!r}.")
    return 0


# ── pip-info ──────────────────────────────────────────────────────────────

def cmd_pip_info(args: argparse.Namespace) -> int:
    """Show metadata about an installed package (via importlib.metadata)."""
    name: str = args.package

    try:
        meta = importlib.metadata.metadata(name)
    except importlib.metadata.PackageNotFoundError:
        print(f"  Package {name!r} is not installed.")
        print(f"  Try:  pip install {name}")
        return 1

    print(f"  Name    : {meta['Name']}")
    print(f"  Version : {meta['Version']}")
    print(f"  Summary : {meta.get('Summary', 'N/A')}")
    print(f"  Home    : {meta.get('Home-page') or meta.get('Project-URL', 'N/A')}")
    print(f"  License : {meta.get('License', 'N/A')}")

    requires = importlib.metadata.requires(name)
    if requires:
        core = [r for r in requires if "extra ==" not in r]
        if core:
            print(f"  Depends : {', '.join(core[:8])}")
    return 0


# ── pip-list ──────────────────────────────────────────────────────────────

def cmd_pip_list(args: argparse.Namespace) -> int:
    """List installed packages (like ``pip list``, but from Python)."""
    packages = sorted(importlib.metadata.distributions(),
                      key=lambda d: (d.metadata["Name"] or "").lower())

    fmt = "  {:<30s} {}"
    print(fmt.format("Package", "Version"))
    print(fmt.format("-" * 30, "-" * 15))
    for dist in packages:
        name = dist.metadata["Name"]
        ver = dist.metadata["Version"]
        if name:
            print(fmt.format(name, ver))
    print(f"\n  Total: {len(packages)} packages")
    return 0


# ── pip-freeze ────────────────────────────────────────────────────────────

def cmd_pip_freeze(args: argparse.Namespace) -> int:
    """Produce ``pip freeze`` output from Python (no subprocess needed)."""
    lines = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata["Name"]
        ver = dist.metadata["Version"]
        if name:
            lines.append(f"{name}=={ver}")
    lines.sort(key=str.lower)

    if args.output:
        from pathlib import Path
        Path(args.output).write_text("\n".join(lines) + "\n")
        print(f"  Wrote {len(lines)} packages to {args.output}")
    else:
        print("\n".join(lines))
    return 0


# ── venv-check ────────────────────────────────────────────────────────────

def cmd_venv_check(args: argparse.Namespace) -> int:
    """Report whether we are running inside a virtual environment."""
    venv = sys.prefix != sys.base_prefix

    print(f"  Python       : {sys.executable}")
    print(f"  Version      : {sys.version.split()[0]}")
    print(f"  sys.prefix   : {sys.prefix}")
    print(f"  base_prefix  : {sys.base_prefix}")
    print(f"  In venv?     : {'Yes' if venv else 'No'}")

    if venv:
        print("\n  You are inside a virtual environment.")
    else:
        print("\n  You are using the system Python.")
        print("  To create a venv:  python -m venv .venv")
        print("  To activate it  :  source .venv/bin/activate   (Linux/Mac)")
        print("                     .venv\\Scripts\\activate      (Windows)")
    return 0


# ── CLI builder ───────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chapter09",
        description="Chapter 9 — libraries, pip, and virtual environments.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              %(prog)s greet --name Alice --verbose
              %(prog)s pip-info requests
              %(prog)s pip-list
              %(prog)s pip-freeze --output requirements.txt
              %(prog)s venv-check
        """),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # greet
    p = sub.add_parser("greet", help="Say hello (classic demo)")
    p.add_argument("--name", default=None, help="Who to greet")
    p.add_argument("--verbose", action="store_true", help="Extra output")
    p.set_defaults(func=cmd_greet)

    # pip-info
    p = sub.add_parser("pip-info", help="Show metadata for an installed package")
    p.add_argument("package", help="Package name (e.g. requests)")
    p.set_defaults(func=cmd_pip_info)

    # pip-list
    p = sub.add_parser("pip-list", help="List all installed packages")
    p.set_defaults(func=cmd_pip_list)

    # pip-freeze
    p = sub.add_parser("pip-freeze", help="Output pip freeze format")
    p.add_argument("-o", "--output", default=None,
                   help="Write to file instead of stdout")
    p.set_defaults(func=cmd_pip_freeze)

    # venv-check
    p = sub.add_parser("venv-check", help="Am I in a virtual environment?")
    p.set_defaults(func=cmd_venv_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
