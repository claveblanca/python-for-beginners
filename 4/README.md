# Chapter 4 — Functions and Reusable Code

How to define functions, pass data in and get results back, and organise growing programs.

## Prerequisites

- Python 3.10+ installed
- Completed [Chapter 3](../3/) (control flow, loops)

## The files

| # | File | Topic |
|---|------|-------|
| 1 | `defining_functions.py` | `def`, parameters, `return`, docstrings, functions as objects |
| 2 | `arguments_and_returns.py` | Positional, keyword, defaults, `*args`, `**kwargs`, type hints, unpacking |
| 3 | `helpers.py` | A utility module (imported by `code_organization.py`) |
| 4 | `code_organization.py` | `import`, `from … import`, `__name__`, scope, lambdas, structuring a program |

## How to run

```bash
cd 4
python defining_functions.py
python arguments_and_returns.py
python code_organization.py
```

(`helpers.py` is imported, not run directly.)

## Concepts introduced

### Defining Functions
- `def name():` — the simplest function
- Parameters and arguments
- `return` — send a value back to the caller
- Returning multiple values (tuples)
- Docstrings — `"""triple-quoted"""` documentation
- Functions are objects — store them in variables or lists

### Arguments and Return Values
- Positional arguments — order matters
- Keyword arguments — `name=value`
- Default parameter values — `def f(x, y=10):`
- `*args` — accept any number of positional arguments
- `**kwargs` — accept any number of keyword arguments
- Keyword-only arguments — after `*`
- Type hints / annotations — `def f(x: int) -> str:`
- Implicit `None` return
- Unpacking with `*list` and `**dict`

### Code Organization
- `import module` / `from module import name`
- `if __name__ == "__main__":` — entry-point guard
- Variable scope — local, `global`, `nonlocal`
- Splitting code into separate `.py` files (modules)
- `lambda` — small anonymous functions
- Practical example: student grade report
