"""
Loops (for, while)
==================

Loops repeat a block of code.
- ``for`` iterates over a sequence (list, range, string, …).
- ``while`` repeats as long as a condition is True.

Run:
    python loops.py
"""

# ---------------------------------------------------------------------------
# 1. for loop with a list
# ---------------------------------------------------------------------------
print("--- 1. for loop (list) ---")
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(f"  I like {fruit}.")

print()

# ---------------------------------------------------------------------------
# 2. for loop with range()
# ---------------------------------------------------------------------------
print("--- 2. for loop (range) ---")
print("  range(5)         ->", list(range(5)))
print("  range(2, 8)      ->", list(range(2, 8)))
print("  range(0, 10, 2)  ->", list(range(0, 10, 2)))

print()
print("  Counting 1 to 5:")
for i in range(1, 6):
    print(f"    {i}")

print()

# ---------------------------------------------------------------------------
# 3. for loop with a string
# ---------------------------------------------------------------------------
print("--- 3. for loop (string) ---")
word = "Python"
for i, ch in enumerate(word):
    print(f"  index {i} -> {ch!r}")

print()

# ---------------------------------------------------------------------------
# 4. while loop
# ---------------------------------------------------------------------------
print("--- 4. while loop ---")
count = 1
while count <= 5:
    print(f"  count = {count}")
    count += 1

print()

# ---------------------------------------------------------------------------
# 5. break — exit a loop early
# ---------------------------------------------------------------------------
print("--- 5. break ---")
for n in range(1, 100):
    if n * n > 50:
        print(f"  First n where n² > 50: {n} (n² = {n * n})")
        break

print()

# ---------------------------------------------------------------------------
# 6. continue — skip to the next iteration
# ---------------------------------------------------------------------------
print("--- 6. continue (skip odd numbers) ---")
for n in range(1, 11):
    if n % 2 != 0:
        continue
    print(f"  {n}", end="")
print()
print()

# ---------------------------------------------------------------------------
# 7. else on a loop (runs when loop ends normally, not via break)
# ---------------------------------------------------------------------------
print("--- 7. for … else ---")
target = 7
for n in range(1, 11):
    if n == target:
        print(f"  Found {target}!")
        break
else:
    print(f"  {target} was not in the range.")

print()

# ---------------------------------------------------------------------------
# 8. Nested loops
# ---------------------------------------------------------------------------
print("--- 8. Nested loops (multiplication table 1–4) ---")
for row in range(1, 5):
    line = ""
    for col in range(1, 5):
        line += f"{row * col:4d}"
    print(f"  {line}")

print()

# ---------------------------------------------------------------------------
# 9. List comprehension (compact for loop)
# ---------------------------------------------------------------------------
print("--- 9. List comprehension ---")
squares = [x ** 2 for x in range(1, 8)]
print(f"  Squares: {squares}")

evens = [x for x in range(20) if x % 2 == 0]
print(f"  Evens < 20: {evens}")

print()

# ---------------------------------------------------------------------------
# 10. while True + break (common pattern)
# ---------------------------------------------------------------------------
print("--- 10. while True + break ---")
print("  (Simulating a menu loop)")
choices = ["play", "settings", "quit"]
for choice in choices:
    print(f"  > {choice}")
    if choice == "quit":
        print("  Goodbye!")
        break

print()
print("=" * 50)
print("Key ideas:  for, while, range(), enumerate(),")
print("            break, continue, else on loop,")
print("            nested loops, list comprehension")
print("=" * 50)
