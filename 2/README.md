# Chapter 2 — Python Basics

Variables, strings, user input, and operators — the building blocks of every program.

## Prerequisites

- Python 3.10+ installed
- Completed [Chapter 1](../1/) (or at least know how to run a `.py` file)

## The files

| # | File | Topic |
|---|------|-------|
| 1 | `variables_and_types.py` | Variables, `int`, `float`, `str`, `bool`, `None`, casting, `type()` |
| 2 | `strings_and_input.py` | String creation, f-strings, methods, indexing, slicing, `input()` |
| 3 | `operators.py` | Arithmetic, comparison, logical, assignment, precedence |

## How to run

```bash
cd 2
python variables_and_types.py
python strings_and_input.py
python operators.py
```

## Concepts introduced

### Variables and Data Types
- `str`, `int`, `float`, `bool`, `None`
- `type()` to inspect, `int()` / `float()` / `str()` to convert
- Multiple assignment: `a, b, c = 1, 2, 3`

### Strings and User Input
- Single, double, and triple quotes
- Concatenation (`+`), repetition (`*`)
- f-strings: `f"Hello, {name}!"`
- Methods: `.strip()`, `.upper()`, `.lower()`, `.replace()`, `.split()`, `.find()`
- Indexing `[0]`, slicing `[a:b]`, reverse `[::-1]`
- Escape characters: `\n`, `\t`, `\\`, `\"`
- `input()` — always returns `str`

### Basic Operators
- Arithmetic: `+  -  *  /  //  %  **`
- Comparison: `==  !=  >  <  >=  <=`
- Logical: `and  or  not`
- Assignment shortcuts: `+=  -=  *=  //=  **=  %=`
- String operators: `+` (concat), `*` (repeat), `in` / `not in`
- Precedence: parentheses override default order
