"""
Basic Operators
===============

Operators are symbols that perform actions on values (operands).
Python has arithmetic, comparison, logical, and assignment operators.

Run:
    python operators.py
"""

# ---------------------------------------------------------------------------
# 1. Arithmetic operators
# ---------------------------------------------------------------------------
print("--- 1. Arithmetic operators ---")
a, b = 17, 5

print(f"a = {a}, b = {b}")
print(f"a + b  = {a + b}      (addition)")
print(f"a - b  = {a - b}      (subtraction)")
print(f"a * b  = {a * b}      (multiplication)")
print(f"a / b  = {a / b}    (division — always a float)")
print(f"a // b = {a // b}       (floor division — whole part)")
print(f"a % b  = {a % b}       (modulo — remainder)")
print(f"a ** b = {a ** b}  (exponent — a to the power of b)")
print()

# ---------------------------------------------------------------------------
# 2. Comparison operators (return True or False)
# ---------------------------------------------------------------------------
print("--- 2. Comparison operators ---")
x, y = 10, 20

print(f"x = {x}, y = {y}")
print(f"x == y  -> {x == y}   (equal)")
print(f"x != y  -> {x != y}    (not equal)")
print(f"x > y   -> {x > y}  (greater than)")
print(f"x < y   -> {x < y}   (less than)")
print(f"x >= y  -> {x >= y}  (greater or equal)")
print(f"x <= y  -> {x <= y}   (less or equal)")
print()

# ---------------------------------------------------------------------------
# 3. Logical operators
# ---------------------------------------------------------------------------
print("--- 3. Logical operators ---")
sunny = True
warm = False

print(f"sunny = {sunny}, warm = {warm}")
print(f"sunny and warm  -> {sunny and warm}   (both must be True)")
print(f"sunny or warm   -> {sunny or warm}    (at least one True)")
print(f"not sunny       -> {not sunny}  (flip True/False)")
print()

# ---------------------------------------------------------------------------
# 4. Assignment operators (shortcuts)
# ---------------------------------------------------------------------------
print("--- 4. Assignment operators ---")
n = 10
print(f"n = {n}")
n += 3
print(f"n += 3   -> {n}")
n -= 1
print(f"n -= 1   -> {n}")
n *= 2
print(f"n *= 2   -> {n}")
n //= 5
print(f"n //= 5  -> {n}")
n **= 3
print(f"n **= 3  -> {n}")
n %= 7
print(f"n %= 7   -> {n}")
print()

# ---------------------------------------------------------------------------
# 5. String operators
# ---------------------------------------------------------------------------
print("--- 5. Operators on strings ---")
greeting = "Hello" + " " + "World"
print(f'"Hello" + " " + "World"  -> {greeting}')
repeat = "ab" * 4
print(f'"ab" * 4                 -> {repeat}')
print(f'"lo" in "Hello"          -> {"lo" in "Hello"}')
print(f'"xyz" not in "Hello"     -> {"xyz" not in "Hello"}')
print()

# ---------------------------------------------------------------------------
# 6. Operator precedence (mini example)
# ---------------------------------------------------------------------------
print("--- 6. Precedence ---")
result = 2 + 3 * 4
print(f"2 + 3 * 4   = {result}   (* before +)")
result = (2 + 3) * 4
print(f"(2 + 3) * 4 = {result}   (parentheses first)")
print()

# ---------------------------------------------------------------------------
# 7. Practical mini-exercise
# ---------------------------------------------------------------------------
print("--- 7. Try it yourself ---")
try:
    celsius = input("Enter a temperature in Celsius: ").strip()
except EOFError:
    celsius = "25"

if celsius.replace("-", "", 1).replace(".", "", 1).isdigit():
    c = float(celsius)
    f = c * 9 / 5 + 32
    print(f"{c}°C = {f:.1f}°F")
    if c > 30:
        print("That is hot!")
    elif c < 0:
        print("Below freezing!")
    else:
        print("Comfortable range.")
else:
    print(f"{celsius!r} does not look like a number.")

print()
print("=" * 50)
print("Key ideas:  +  -  *  /  //  %  **")
print("            ==  !=  >  <  >=  <=")
print("            and  or  not")
print("            +=  -=  *=  //=  **=  %=")
print("=" * 50)
