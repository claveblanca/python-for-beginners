# Chapter 3 — Python Control Flow

Conditional statements, loops, and putting them together in small programs.

## Prerequisites

- Python 3.10+ installed
- Completed [Chapter 2](../2/) (variables, strings, operators)

## The files

| # | File | Topic |
|---|------|-------|
| 1 | `conditionals.py` | `if`, `elif`, `else`, nested if, `and`/`or`/`not`, truthy/falsy, ternary |
| 2 | `loops.py` | `for`, `while`, `range()`, `enumerate()`, `break`, `continue`, list comprehension |
| 3 | `simple_programs.py` | Five mini-programs that combine everything |

## How to run

```bash
cd 3
python conditionals.py
python loops.py
python simple_programs.py
```

## Concepts introduced

### Conditional Statements
- `if` / `elif` / `else` — choose which code block runs
- Nested conditions — `if` inside another `if`
- `and`, `or`, `not` — combine multiple conditions
- Truthy / falsy — `0`, `""`, `None`, `[]` are falsy; most other values are truthy
- Ternary expression — `value_if_true if condition else value_if_false`

### Loops
- `for item in sequence` — iterate over lists, strings, ranges
- `range(start, stop, step)` — generate number sequences
- `enumerate()` — get both index and value
- `while condition` — repeat until condition becomes False
- `break` — exit the loop immediately
- `continue` — skip to the next iteration
- `else` on a loop — runs only if the loop completed without `break`
- Nested loops — a loop inside a loop
- List comprehension — `[expr for x in seq if cond]`

### Simple Programs
1. **Guess the Number** — `while` loop, `random`, `if/elif/else`, `break`
2. **FizzBuzz** — `for` + `range()`, `%` modulo, `if/elif/else`
3. **Sum Calculator** — `while` with sentinel value, `float()`, `try/except`
4. **Password Validator** — `for` loop, `any()`, string methods, list of errors
5. **Pattern Printer** — nested `for` loops, string repetition
