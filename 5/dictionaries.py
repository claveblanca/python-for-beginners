"""
Dictionaries
============

A dictionary maps keys to values.  Keys must be unique and hashable
(strings, numbers, tuples).  Lookup by key is very fast.

Run:
    python dictionaries.py
"""

# ---------------------------------------------------------------------------
# 1. Creating dictionaries
# ---------------------------------------------------------------------------
print("--- 1. Creating dictionaries ---")
empty = {}
person = {"name": "Alice", "age": 30, "city": "Rome"}
from_pairs = dict([("a", 1), ("b", 2)])
from_kwargs = dict(x=10, y=20)

print(f"  empty      = {empty}")
print(f"  person     = {person}")
print(f"  from_pairs = {from_pairs}")
print(f"  from_kwargs= {from_kwargs}")
print()

# ---------------------------------------------------------------------------
# 2. Accessing values
# ---------------------------------------------------------------------------
print("--- 2. Accessing values ---")
print(f"  person['name']        = {person['name']!r}")
print(f"  person.get('age')     = {person.get('age')}")
print(f"  person.get('email','N/A') = {person.get('email', 'N/A')!r}")

try:
    _ = person["email"]
except KeyError as e:
    print(f"  person['email']       -> KeyError: {e}")
print()

# ---------------------------------------------------------------------------
# 3. Adding and updating
# ---------------------------------------------------------------------------
print("--- 3. Adding & updating ---")
d = {"a": 1, "b": 2}
print(f"  start: {d}")

d["c"] = 3
print(f"  d['c'] = 3          -> {d}")

d["a"] = 100
print(f"  d['a'] = 100        -> {d}")

d.update({"b": 200, "d": 4})
print(f"  .update(b=200, d=4) -> {d}")
print()

# ---------------------------------------------------------------------------
# 4. Removing items
# ---------------------------------------------------------------------------
print("--- 4. Removing items ---")
d = {"a": 1, "b": 2, "c": 3, "d": 4}
print(f"  start: {d}")

del d["a"]
print(f"  del d['a']  -> {d}")

val = d.pop("b")
print(f"  d.pop('b')  -> {d}  (returned {val})")

val = d.pop("z", "missing")
print(f"  d.pop('z', 'missing') -> {val!r}  (safe default)")
print()

# ---------------------------------------------------------------------------
# 5. Iterating
# ---------------------------------------------------------------------------
print("--- 5. Iterating ---")
scores = {"Alice": 92, "Bob": 78, "Charlie": 85}

print("  keys:")
for k in scores:
    print(f"    {k}")

print("  values:")
for v in scores.values():
    print(f"    {v}")

print("  items (key, value):")
for name, score in scores.items():
    print(f"    {name}: {score}")
print()

# ---------------------------------------------------------------------------
# 6. Useful methods
# ---------------------------------------------------------------------------
print("--- 6. Useful methods ---")
d = {"a": 1, "b": 2}
print(f"  d.keys()   = {list(d.keys())}")
print(f"  d.values() = {list(d.values())}")
print(f"  d.items()  = {list(d.items())}")
print(f"  'a' in d   = {'a' in d}")
print(f"  len(d)     = {len(d)}")
print()

# ---------------------------------------------------------------------------
# 7. Dictionary comprehension
# ---------------------------------------------------------------------------
print("--- 7. Dictionary comprehension ---")
squares = {x: x ** 2 for x in range(1, 7)}
print(f"  {{x: x**2 for x in range(1,7)}} = {squares}")

words = ["hello", "world", "python"]
lengths = {w: len(w) for w in words}
print(f"  word lengths = {lengths}")
print()

# ---------------------------------------------------------------------------
# 8. Nested dictionaries
# ---------------------------------------------------------------------------
print("--- 8. Nested dictionaries ---")
school = {
    "Alice": {"math": 90, "science": 85},
    "Bob": {"math": 72, "science": 68},
}

for student, grades in school.items():
    avg = sum(grades.values()) / len(grades)
    print(f"  {student}: {grades} -> avg {avg:.0f}")
print()

# ---------------------------------------------------------------------------
# 9. setdefault and defaultdict
# ---------------------------------------------------------------------------
print("--- 9. setdefault & defaultdict ---")
word_count = {}
sentence = "the cat sat on the mat the cat"

for word in sentence.split():
    word_count.setdefault(word, 0)
    word_count[word] += 1
print(f"  setdefault: {word_count}")

from collections import defaultdict

grouped = defaultdict(list)
pairs = [("fruit", "apple"), ("veg", "carrot"), ("fruit", "banana"), ("veg", "pea")]
for category, item in pairs:
    grouped[category].append(item)
print(f"  defaultdict(list): {dict(grouped)}")
print()

# ---------------------------------------------------------------------------
# 10. Merging dictionaries (Python 3.9+)
# ---------------------------------------------------------------------------
print("--- 10. Merging ---")
defaults = {"color": "blue", "size": 10, "visible": True}
overrides = {"color": "red", "size": 20}

merged = {**defaults, **overrides}
print(f"  {{**defaults, **overrides}} = {merged}")

merged2 = defaults | overrides
print(f"  defaults | overrides      = {merged2}")
print()

# ---------------------------------------------------------------------------
# 11. Practical example: inventory tracker
# ---------------------------------------------------------------------------
print("--- 11. Inventory tracker ---")
inventory: dict[str, int] = {}
actions = [
    ("add", "apples", 10),
    ("add", "bananas", 6),
    ("add", "apples", 5),
    ("sell", "bananas", 2),
    ("sell", "apples", 3),
]

for action, item, qty in actions:
    if action == "add":
        inventory[item] = inventory.get(item, 0) + qty
    elif action == "sell":
        current = inventory.get(item, 0)
        inventory[item] = max(0, current - qty)
    print(f"  {action:4s} {qty} {item:8s} -> stock: {inventory}")
print()

print("=" * 50)
print("Key ideas:  {key: value}, .get(), .items(),")
print("            del, .pop(), comprehensions,")
print("            nesting, defaultdict, | merge")
print("=" * 50)
