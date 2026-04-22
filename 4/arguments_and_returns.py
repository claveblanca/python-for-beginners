"""
Arguments and Return Values
============================

Python functions support many argument styles:
positional, keyword, defaults, *args, **kwargs, and type hints.

Run:
    python arguments_and_returns.py
"""

# ---------------------------------------------------------------------------
# 1. Positional arguments
# ---------------------------------------------------------------------------
print("--- 1. Positional arguments ---")


def power(base, exponent):
    return base ** exponent


print(f"  power(2, 10) = {power(2, 10)}")
print()

# ---------------------------------------------------------------------------
# 2. Keyword arguments (named)
# ---------------------------------------------------------------------------
print("--- 2. Keyword arguments ---")

print(f"  power(exponent=3, base=5) = {power(exponent=3, base=5)}")
print()

# ---------------------------------------------------------------------------
# 3. Default values
# ---------------------------------------------------------------------------
print("--- 3. Default parameter values ---")


def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"


print(f"  greet('Alice')              = {greet('Alice')!r}")
print(f"  greet('Bob', 'Good morning') = {greet('Bob', 'Good morning')!r}")
print()

# ---------------------------------------------------------------------------
# 4. *args — variable number of positional arguments
# ---------------------------------------------------------------------------
print("--- 4. *args ---")


def total(*numbers):
    """Sum any number of arguments."""
    return sum(numbers)


print(f"  total(1, 2, 3)       = {total(1, 2, 3)}")
print(f"  total(10, 20, 30, 40) = {total(10, 20, 30, 40)}")
print()

# ---------------------------------------------------------------------------
# 5. **kwargs — variable number of keyword arguments
# ---------------------------------------------------------------------------
print("--- 5. **kwargs ---")


def build_profile(name, **info):
    """Build a dictionary from keyword arguments."""
    profile = {"name": name}
    profile.update(info)
    return profile


print(f"  {build_profile('Alice', age=30, city='Rome')}")
print(f"  {build_profile('Bob', role='developer')}")
print()

# ---------------------------------------------------------------------------
# 6. Mixing all argument types (order matters)
# ---------------------------------------------------------------------------
print("--- 6. Mixing argument styles ---")


def example(a, b, c=10, *extra, verbose=False, **opts):
    print(f"  a={a}, b={b}, c={c}, extra={extra}, verbose={verbose}, opts={opts}")


example(1, 2)
example(1, 2, 3, 4, 5, verbose=True, mode="fast")
print()

# ---------------------------------------------------------------------------
# 7. Keyword-only arguments (after *)
# ---------------------------------------------------------------------------
print("--- 7. Keyword-only arguments ---")


def connect(host, port, *, timeout=30, retries=3):
    print(f"  host={host}, port={port}, timeout={timeout}, retries={retries}")


connect("localhost", 5432)
connect("db.example.com", 3306, timeout=5, retries=1)
print()

# ---------------------------------------------------------------------------
# 8. Type hints (annotations)
# ---------------------------------------------------------------------------
print("--- 8. Type hints ---")


def bmi(weight_kg: float, height_m: float) -> float:
    """Body Mass Index = weight / height²."""
    return weight_kg / (height_m ** 2)


value = bmi(70, 1.75)
print(f"  bmi(70, 1.75) = {value:.1f}")
print(f"  Annotations: {bmi.__annotations__}")
print()

# ---------------------------------------------------------------------------
# 9. Returning None implicitly
# ---------------------------------------------------------------------------
print("--- 9. Returning None ---")


def log(message):
    print(f"  LOG: {message}")


result = log("system started")
print(f"  Return value of log(): {result!r}")
print()

# ---------------------------------------------------------------------------
# 10. Unpacking arguments with * and **
# ---------------------------------------------------------------------------
print("--- 10. Unpacking with * and ** ---")


def point_info(x, y, z):
    print(f"  x={x}, y={y}, z={z}")


coords = [1, 2, 3]
point_info(*coords)

settings = {"x": 10, "y": 20, "z": 30}
point_info(**settings)
print()

print("=" * 50)
print("Key ideas:  positional, keyword, defaults,")
print("            *args, **kwargs, keyword-only,")
print("            type hints, unpacking * / **")
print("=" * 50)
