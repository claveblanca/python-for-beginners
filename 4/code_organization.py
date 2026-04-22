"""
Code Organization
=================

As programs grow, you split code into functions and modules.
This file shows how to import from another file, use ``if __name__``,
and structure a small program cleanly.

Run:
    python code_organization.py
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 1. Importing from another file in the same folder
# ---------------------------------------------------------------------------
print("--- 1. Importing from helpers.py ---")

import helpers

print(f"  helpers.is_even(4)        = {helpers.is_even(4)}")
print(f"  helpers.clamp(15, 0, 10)  = {helpers.clamp(15, 0, 10)}")
print(f"  helpers.title_case('hello world') = {helpers.title_case('hello world')!r}")
print()

# ---------------------------------------------------------------------------
# 2. Importing specific names
# ---------------------------------------------------------------------------
print("--- 2. Importing specific names ---")

from helpers import fahrenheit_to_celsius, clamp

print(f"  fahrenheit_to_celsius(212) = {fahrenheit_to_celsius(212)}")
print(f"  clamp(-5, 0, 100)         = {clamp(-5, 0, 100)}")
print()

# ---------------------------------------------------------------------------
# 3. The if __name__ == "__main__" pattern
# ---------------------------------------------------------------------------
print("--- 3. if __name__ == '__main__' ---")
print(f"  This file's __name__ = {__name__!r}")
print("  helpers' __name__    =", helpers.__name__)
print()
print('  When you run a file directly, __name__ is "__main__".')
print("  When it is imported, __name__ is the module name.")
print()

# ---------------------------------------------------------------------------
# 4. Organizing with functions — before vs. after
# ---------------------------------------------------------------------------
print("--- 4. Before vs. after: organizing with functions ---")

print()
print("  BAD (everything at the top level):")
print("  ┌──────────────────────────────────────┐")
print("  │  data = [3, 1, 4, 1, 5, 9]          │")
print("  │  total = 0                            │")
print("  │  for n in data:                       │")
print("  │      total += n                       │")
print("  │  avg = total / len(data)              │")
print("  │  print(avg)                           │")
print("  └──────────────────────────────────────┘")

print()
print("  GOOD (logic inside functions, called from main):")
print("  ┌──────────────────────────────────────┐")
print("  │  def average(numbers):               │")
print("  │      return sum(numbers) / len(...)   │")
print("  │                                       │")
print("  │  def main():                          │")
print("  │      data = [3, 1, 4, 1, 5, 9]      │")
print("  │      print(average(data))             │")
print("  │                                       │")
print("  │  if __name__ == '__main__':           │")
print("  │      main()                           │")
print("  └──────────────────────────────────────┘")
print()

# ---------------------------------------------------------------------------
# 5. A real example — student grade report
# ---------------------------------------------------------------------------
print("--- 5. Practical example: student grade report ---")


def letter_grade(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def average(numbers: list[float]) -> float:
    return sum(numbers) / len(numbers) if numbers else 0.0


def print_report(name: str, scores: list[float]) -> None:
    avg = average(scores)
    grade = letter_grade(avg)
    formatted = ", ".join(str(s) for s in scores)
    print(f"  {name:10s}  scores: [{formatted}]  avg: {avg:.1f}  grade: {grade}")


students = {
    "Alice": [92, 88, 95],
    "Bob": [70, 65, 72],
    "Charlie": [55, 48, 60],
    "Diana": [100, 97, 99],
}

for name, scores in students.items():
    print_report(name, scores)

print()

# ---------------------------------------------------------------------------
# 6. Scope — local vs. global
# ---------------------------------------------------------------------------
print("--- 6. Variable scope ---")

counter = 0


def increment():
    global counter
    counter += 1


increment()
increment()
print(f"  counter after two increment() calls: {counter}")
print()


def outer():
    message = "hello"

    def inner():
        nonlocal message
        message = "changed"

    inner()
    print(f"  After inner(): message = {message!r}")


outer()
print()

# ---------------------------------------------------------------------------
# 7. Lambda — small anonymous functions
# ---------------------------------------------------------------------------
print("--- 7. Lambda ---")

double = lambda x: x * 2
print(f"  double(7) = {double(7)}")

names = ["Charlie", "alice", "Bob"]
sorted_names = sorted(names, key=lambda n: n.lower())
print(f"  sorted (case-insensitive): {sorted_names}")
print()

print("=" * 50)
print("Key ideas:  import, from … import, __name__,")
print("            scope (local/global/nonlocal),")
print("            organizing code into functions,")
print("            lambda, splitting into modules")
print("=" * 50)
