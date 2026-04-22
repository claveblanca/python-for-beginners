"""
Tuples and Sets
===============

Tuples are ordered and immutable (cannot change after creation).
Sets are unordered collections of unique values.

Run:
    python tuples_and_sets.py
"""

# ===================================================================
# PART A — TUPLES
# ===================================================================
print("=" * 50)
print("TUPLES")
print("=" * 50)
print()

# ---------------------------------------------------------------------------
# 1. Creating tuples
# ---------------------------------------------------------------------------
print("--- 1. Creating tuples ---")
empty = ()
single = (42,)
point = (3, 7)
person = ("Alice", 30, "Rome")
from_list = tuple([1, 2, 3])

print(f"  empty     = {empty}")
print(f"  single    = {single}   (trailing comma needed)")
print(f"  point     = {point}")
print(f"  person    = {person}")
print(f"  from_list = {from_list}")
print()

# ---------------------------------------------------------------------------
# 2. Accessing elements
# ---------------------------------------------------------------------------
print("--- 2. Indexing & slicing (same as lists) ---")
print(f"  person[0]   = {person[0]!r}")
print(f"  person[-1]  = {person[-1]!r}")
print(f"  person[1:]  = {person[1:]}")
print()

# ---------------------------------------------------------------------------
# 3. Tuples are immutable
# ---------------------------------------------------------------------------
print("--- 3. Immutability ---")
try:
    person[0] = "Bob"
except TypeError as e:
    print(f"  person[0] = 'Bob' -> TypeError: {e}")
print("  You cannot change a tuple after creation.")
print()

# ---------------------------------------------------------------------------
# 4. Unpacking
# ---------------------------------------------------------------------------
print("--- 4. Unpacking ---")
name, age, city = person
print(f"  name={name!r}, age={age}, city={city!r}")

x, *rest = (10, 20, 30, 40)
print(f"  x={x}, rest={rest}")
print()

# ---------------------------------------------------------------------------
# 5. Tuple as dictionary key / return value
# ---------------------------------------------------------------------------
print("--- 5. Tuples as keys & return values ---")
grid = {(0, 0): "origin", (1, 0): "east", (0, 1): "north"}
print(f"  grid[(0,0)] = {grid[(0, 0)]!r}")


def divide(a, b):
    return a // b, a % b


quotient, remainder = divide(17, 5)
print(f"  17 ÷ 5 -> quotient={quotient}, remainder={remainder}")
print()

# ---------------------------------------------------------------------------
# 6. Named tuples (preview)
# ---------------------------------------------------------------------------
print("--- 6. Named tuples ---")
from collections import namedtuple

Color = namedtuple("Color", ["name", "hex", "r", "g", "b"])
red = Color("red", "#FF0000", 255, 0, 0)
print(f"  {red}")
print(f"  red.name = {red.name!r}, red.hex = {red.hex}")
print()


# ===================================================================
# PART B — SETS
# ===================================================================
print("=" * 50)
print("SETS")
print("=" * 50)
print()

# ---------------------------------------------------------------------------
# 7. Creating sets
# ---------------------------------------------------------------------------
print("--- 7. Creating sets ---")
empty_set = set()
fruits = {"apple", "banana", "cherry"}
from_list = set([1, 2, 2, 3, 3, 3])

print(f"  empty_set = {empty_set}")
print(f"  fruits    = {fruits}")
print(f"  from_list = {from_list}  (duplicates removed)")
print()

# ---------------------------------------------------------------------------
# 8. Adding and removing
# ---------------------------------------------------------------------------
print("--- 8. Adding & removing ---")
s = {1, 2, 3}
print(f"  start: {s}")

s.add(4)
print(f"  .add(4)     -> {s}")

s.add(2)
print(f"  .add(2)     -> {s}  (no duplicate)")

s.discard(1)
print(f"  .discard(1) -> {s}")

s.discard(99)
print(f"  .discard(99)-> {s}  (no error if missing)")
print()

# ---------------------------------------------------------------------------
# 9. Set operations
# ---------------------------------------------------------------------------
print("--- 9. Set operations ---")
a = {1, 2, 3, 4, 5}
b = {3, 4, 5, 6, 7}

print(f"  a = {a}")
print(f"  b = {b}")
print(f"  a | b  (union)        = {a | b}")
print(f"  a & b  (intersection) = {a & b}")
print(f"  a - b  (difference)   = {a - b}")
print(f"  b - a  (difference)   = {b - a}")
print(f"  a ^ b  (symmetric)    = {a ^ b}")
print()

# ---------------------------------------------------------------------------
# 10. Membership testing (very fast for sets)
# ---------------------------------------------------------------------------
print("--- 10. Membership ---")
big = set(range(1_000_000))
print(f"  999_999 in big -> {999_999 in big}")
print(f"  -1 in big      -> {-1 in big}")
print()

# ---------------------------------------------------------------------------
# 11. Set comprehension
# ---------------------------------------------------------------------------
print("--- 11. Set comprehension ---")
lengths = {len(w) for w in ["hello", "hi", "hey", "howdy"]}
print(f"  Word lengths: {lengths}")
print()

# ---------------------------------------------------------------------------
# 12. Frozenset (immutable set)
# ---------------------------------------------------------------------------
print("--- 12. Frozenset ---")
fs = frozenset([1, 2, 3])
print(f"  frozenset = {fs}")
try:
    fs.add(4)
except AttributeError as e:
    print(f"  fs.add(4) -> AttributeError: {e}")
print()

# ---------------------------------------------------------------------------
# 13. Practical example: remove duplicates while keeping order
# ---------------------------------------------------------------------------
print("--- 13. Remove duplicates (keep order) ---")
items = ["b", "a", "c", "a", "b", "d"]
seen = set()
unique = []
for item in items:
    if item not in seen:
        seen.add(item)
        unique.append(item)
print(f"  {items} -> {unique}")
print()

print("=" * 50)
print("Tuples:  (), immutable, unpacking, namedtuple")
print("Sets:    {{}}, unique, |  &  -  ^, fast 'in'")
print("=" * 50)
