"""
Variables and Data Types
========================

A variable is a name that refers to a value stored in memory.
Python figures out the type automatically — you do not declare it.

Run:
    python variables_and_types.py
"""

# ---------------------------------------------------------------------------
# 1. Creating variables
# ---------------------------------------------------------------------------
name = "Alice"          # str  — a piece of text (a "string")
age = 30                # int  — a whole number
height = 1.72           # float — a decimal number
is_student = True       # bool — True or False

print("--- 1. Creating variables ---")
print(f"name       = {name}")
print(f"age        = {age}")
print(f"height     = {height}")
print(f"is_student = {is_student}")
print()

# ---------------------------------------------------------------------------
# 2. Checking types with type()
# ---------------------------------------------------------------------------
print("--- 2. Checking types ---")
print(f"type(name)       -> {type(name)}")
print(f"type(age)        -> {type(age)}")
print(f"type(height)     -> {type(height)}")
print(f"type(is_student) -> {type(is_student)}")
print()

# ---------------------------------------------------------------------------
# 3. Changing a variable's value (and even its type)
# ---------------------------------------------------------------------------
print("--- 3. Re-assigning variables ---")
x = 10
print(f"x = {x}  (type: {type(x).__name__})")
x = "ten"
print(f"x = {x}  (type: {type(x).__name__})")
print("Python lets you change a variable to a different type — but be careful!")
print()

# ---------------------------------------------------------------------------
# 4. Converting between types (casting)
# ---------------------------------------------------------------------------
print("--- 4. Type conversion (casting) ---")
num_str = "42"
num_int = int(num_str)          # str -> int
num_float = float(num_str)      # str -> float
back_to_str = str(num_int)      # int -> str

print(f'int("42")   -> {num_int}   (type: {type(num_int).__name__})')
print(f'float("42") -> {num_float} (type: {type(num_float).__name__})')
print(f"str(42)     -> {back_to_str!r}  (type: {type(back_to_str).__name__})")
print()

# ---------------------------------------------------------------------------
# 5. None — the "nothing" value
# ---------------------------------------------------------------------------
print("--- 5. None ---")
result = None
print(f"result = {result}  (type: {type(result).__name__})")
print("None means 'no value yet'. It is not the same as 0 or an empty string.")
print()

# ---------------------------------------------------------------------------
# 6. Multiple assignment
# ---------------------------------------------------------------------------
print("--- 6. Multiple assignment ---")
a, b, c = 1, 2, 3
print(f"a, b, c = {a}, {b}, {c}")
x = y = z = 0
print(f"x = y = z = {x}")
print()

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("=" * 50)
print("Core types:  str, int, float, bool, None")
print("Check type:  type(value)")
print("Convert:     int(), float(), str(), bool()")
print("=" * 50)
