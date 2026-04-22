"""
Lists
=====

A list is an ordered, mutable collection.  You can add, remove,
sort, and slice items freely.

Run:
    python lists.py
"""

# ---------------------------------------------------------------------------
# 1. Creating lists
# ---------------------------------------------------------------------------
print("--- 1. Creating lists ---")
empty = []
numbers = [10, 20, 30, 40, 50]
mixed = [1, "two", 3.0, True, None]
nested = [[1, 2], [3, 4], [5, 6]]

print(f"  empty   = {empty}")
print(f"  numbers = {numbers}")
print(f"  mixed   = {mixed}")
print(f"  nested  = {nested}")
print()

# ---------------------------------------------------------------------------
# 2. Indexing and slicing
# ---------------------------------------------------------------------------
print("--- 2. Indexing & slicing ---")
colors = ["red", "green", "blue", "yellow", "purple"]

print(f"  colors        = {colors}")
print(f"  colors[0]     = {colors[0]!r}   (first)")
print(f"  colors[-1]    = {colors[-1]!r} (last)")
print(f"  colors[1:3]   = {colors[1:3]}  (slice)")
print(f"  colors[::2]   = {colors[::2]}  (every 2nd)")
print(f"  colors[::-1]  = {colors[::-1]}  (reversed)")
print()

# ---------------------------------------------------------------------------
# 3. Modifying lists
# ---------------------------------------------------------------------------
print("--- 3. Modifying lists ---")
fruits = ["apple", "banana", "cherry"]
print(f"  start: {fruits}")

fruits.append("date")
print(f"  .append('date')     -> {fruits}")

fruits.insert(1, "apricot")
print(f"  .insert(1,'apricot')-> {fruits}")

fruits.remove("banana")
print(f"  .remove('banana')   -> {fruits}")

popped = fruits.pop()
print(f"  .pop()              -> {fruits}  (removed {popped!r})")

fruits[0] = "avocado"
print(f"  fruits[0] = 'avocado' -> {fruits}")

fruits.extend(["fig", "grape"])
print(f"  .extend([fig,grape])-> {fruits}")
print()

# ---------------------------------------------------------------------------
# 4. Common list operations
# ---------------------------------------------------------------------------
print("--- 4. Common operations ---")
nums = [5, 2, 8, 1, 9, 3]
print(f"  nums        = {nums}")
print(f"  len(nums)   = {len(nums)}")
print(f"  min(nums)   = {min(nums)}")
print(f"  max(nums)   = {max(nums)}")
print(f"  sum(nums)   = {sum(nums)}")
print(f"  sorted(nums)= {sorted(nums)}")
print(f"  3 in nums   = {3 in nums}")
print(f"  nums.count(5) = {nums.count(5)}")
print(f"  nums.index(8) = {nums.index(8)}  (position of 8)")

nums.sort()
print(f"  nums.sort()   -> {nums}  (in-place)")
nums.reverse()
print(f"  nums.reverse() -> {nums}")
print()

# ---------------------------------------------------------------------------
# 5. Iterating
# ---------------------------------------------------------------------------
print("--- 5. Iterating ---")
langs = ["Python", "JavaScript", "Go"]

print("  for item in list:")
for lang in langs:
    print(f"    {lang}")

print("  for i, item in enumerate(list):")
for i, lang in enumerate(langs, start=1):
    print(f"    {i}. {lang}")
print()

# ---------------------------------------------------------------------------
# 6. List comprehensions
# ---------------------------------------------------------------------------
print("--- 6. List comprehensions ---")
squares = [x ** 2 for x in range(1, 8)]
print(f"  [x**2 for x in range(1,8)]        = {squares}")

evens = [x for x in range(20) if x % 2 == 0]
print(f"  [x for x in range(20) if x%2==0]  = {evens}")

words = ["Hello", "World"]
upper = [w.upper() for w in words]
print(f"  [w.upper() for w in words]         = {upper}")
print()

# ---------------------------------------------------------------------------
# 7. Copying a list (shallow vs. reference)
# ---------------------------------------------------------------------------
print("--- 7. Copying ---")
original = [1, 2, 3]
ref = original
copy = original.copy()

original.append(4)
print(f"  original = {original}")
print(f"  ref      = {ref}      (same object — also changed!)")
print(f"  copy     = {copy}         (.copy() is independent)")
print()

# ---------------------------------------------------------------------------
# 8. Unpacking
# ---------------------------------------------------------------------------
print("--- 8. Unpacking ---")
first, second, *rest = [10, 20, 30, 40, 50]
print(f"  first={first}, second={second}, rest={rest}")
print()

print("=" * 50)
print("Key ideas:  [], append, insert, remove, pop,")
print("            slicing, sort, comprehensions, copy")
print("=" * 50)
