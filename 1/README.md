# Chapter 1 — Running Python & Hello World

Five ways to run Python, from simplest to most professional.

## Prerequisites

- Python 3.10+ installed ([python.org/downloads](https://www.python.org/downloads/))
- On Windows: check **Add python.exe to PATH** during install

## The files

| # | File | What it teaches | How to run |
|---|------|-----------------|------------|
| 1 | `hello_repl.py` | Interactive mode (REPL) | `python` then type lines, or `python hello_repl.py` |
| 2 | `hello_script.py` | Running a `.py` file | `python hello_script.py` |
| 3 | `hello_executable.py` | Shebang, `chmod +x` (Linux/Mac) | `chmod +x hello_executable.py && ./hello_executable.py` |
| 4 | `hello_input.py` | `input()`, variables, `if/else` | `python hello_input.py` |
| 5 | `hello_ide.py` | Running from VS Code / PyCharm | Open file, click **Run** |

## Quick summary

| Method | Best for | Command |
|--------|----------|---------|
| Interactive (REPL) | Quick testing | `python` |
| Script file | Real programs | `python hello_script.py` |
| Executable | Advanced usage (Linux/Mac) | `./hello_executable.py` |
| Double-click | Beginners (limited, window may close) | Open the `.py` file |
| IDE | Development | Click **Run** in editor |

## Suggested order

1. Start the REPL (`python`) and type `print("Hello, world!")`.
2. Run `python hello_script.py` — see how a file executes top-to-bottom.
3. Run `python hello_input.py` — have a conversation with your program.
4. Open `hello_ide.py` in your editor and click Run.
5. (Linux/Mac) Try `chmod +x hello_executable.py && ./hello_executable.py`.

## Concepts introduced

- `print()` — display text
- Variables — `name = "Python"`
- f-strings — `f"Hello, {name}!"`
- `input()` — read user input
- `if / else` — make decisions
- `type()` — check what kind of value something is
- Shebang (`#!/usr/bin/env python3`) — let the OS find the interpreter
