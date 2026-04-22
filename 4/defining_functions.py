"""
Defining Functions
==================

A function is a reusable block of code with a name.
You define it once, then call it as many times as you need.

Run:
    python defining_functions.py
"""

# ---------------------------------------------------------------------------
# 1. The simplest function
# ---------------------------------------------------------------------------
print("--- 1. A function with no parameters ---")


def say_hello():
    print("  Hello from a function!")


say_hello()
say_hello()
print()

# ---------------------------------------------------------------------------
# 2. A function with a parameter
# ---------------------------------------------------------------------------
print("--- 2. One parameter ---")


def greet(name):
    print(f"  Hello, {name}!")


greet("Alice")
greet("Bob")
print()

# ---------------------------------------------------------------------------
# 3. Returning a value
# ---------------------------------------------------------------------------
print("--- 3. Return values ---")


def square(n):
    return n * n


result = square(5)
print(f"  square(5) = {result}")
print(f"  square(9) = {square(9)}")
print()

# ---------------------------------------------------------------------------
# 4. Multiple parameters
# ---------------------------------------------------------------------------
print("--- 4. Multiple parameters ---")


def add(a, b):
    return a + b


print(f"  add(3, 7)       = {add(3, 7)}")
print(f"  add('Hi ', 'there') = {add('Hi ', 'there')!r}")
print()

# ---------------------------------------------------------------------------
# 5. Returning multiple values (tuple)
# ---------------------------------------------------------------------------
print("--- 5. Returning multiple values ---")


def min_max(numbers):
    return min(numbers), max(numbers)


lo, hi = min_max([4, 1, 9, 2, 7])
print(f"  min_max([4,1,9,2,7]) -> min={lo}, max={hi}")
print()

# ---------------------------------------------------------------------------
# 6. Docstrings — documenting your functions
# ---------------------------------------------------------------------------
print("--- 6. Docstrings ---")


def celsius_to_fahrenheit(c):
    """Convert Celsius to Fahrenheit.

    Parameters
    ----------
    c : float
        Temperature in Celsius.

    Returns
    -------
    float
        Temperature in Fahrenheit.
    """
    return c * 9 / 5 + 32


print(f"  celsius_to_fahrenheit(100) = {celsius_to_fahrenheit(100)}")
print(f"  Docstring: {celsius_to_fahrenheit.__doc__.strip().splitlines()[0]}")
print()

# ---------------------------------------------------------------------------
# 7. Functions are objects — you can store them in variables
# ---------------------------------------------------------------------------
print("--- 7. Functions are objects ---")

operation = square
print(f"  operation(6) = {operation(6)}")

funcs = [square, celsius_to_fahrenheit]
for fn in funcs:
    print(f"  {fn.__name__}(10) = {fn(10)}")
print()

# ---------------------------------------------------------------------------
# 8. Calling a function from another function
# ---------------------------------------------------------------------------
print("--- 8. Functions calling functions ---")


def rectangle_area(width, height):
    return width * height


def describe_rectangle(width, height):
    area = rectangle_area(width, height)
    perimeter = 2 * (width + height)
    print(f"  {width}x{height} rectangle: area={area}, perimeter={perimeter}")


describe_rectangle(5, 3)
describe_rectangle(10, 2)
print()

print("=" * 50)
print("Key ideas:  def, parameters, return,")
print("            docstrings, functions as objects")
print("=" * 50)
