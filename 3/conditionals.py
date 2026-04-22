"""
Conditional Statements (if, elif, else)
=======================================

Conditionals let your program make decisions.
The code under a condition only runs when that condition is True.

Run:
    python conditionals.py
"""

# ---------------------------------------------------------------------------
# 1. Basic if
# ---------------------------------------------------------------------------
print("--- 1. Basic if ---")
temperature = 35

if temperature > 30:
    print(f"{temperature}°C — It is hot outside!")

print()

# ---------------------------------------------------------------------------
# 2. if / else
# ---------------------------------------------------------------------------
print("--- 2. if / else ---")
age = 16

if age >= 18:
    print("You can vote.")
else:
    print(f"You are {age}. You must be 18 to vote.")

print()

# ---------------------------------------------------------------------------
# 3. if / elif / else (multiple branches)
# ---------------------------------------------------------------------------
print("--- 3. if / elif / else ---")
score = 73

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Score {score} -> Grade {grade}")
print()

# ---------------------------------------------------------------------------
# 4. Nested if
# ---------------------------------------------------------------------------
print("--- 4. Nested if ---")
has_ticket = True
age = 12

if has_ticket:
    if age >= 13:
        print("Welcome to the movie!")
    else:
        print("You need a parent — you are under 13.")
else:
    print("You need a ticket first.")

print()

# ---------------------------------------------------------------------------
# 5. Combining conditions with and / or / not
# ---------------------------------------------------------------------------
print("--- 5. Combining conditions ---")
username = "admin"
password = "secret123"

if username == "admin" and password == "secret123":
    print("Login successful!")

temp = 22
if temp < 0 or temp > 40:
    print("Extreme temperature!")
else:
    print(f"{temp}°C is within normal range.")

logged_in = False
if not logged_in:
    print("Please log in.")

print()

# ---------------------------------------------------------------------------
# 6. Truthy and falsy values
# ---------------------------------------------------------------------------
print("--- 6. Truthy / falsy ---")
values = [0, 1, "", "hello", None, [], [1, 2], 0.0, 3.14]

for v in values:
    label = "truthy" if v else "falsy"
    print(f"  {str(v):10s} ({type(v).__name__:5s}) -> {label}")

print()

# ---------------------------------------------------------------------------
# 7. Ternary (inline if)
# ---------------------------------------------------------------------------
print("--- 7. Ternary expression ---")
n = 7
parity = "even" if n % 2 == 0 else "odd"
print(f"{n} is {parity}.")
print()

# ---------------------------------------------------------------------------
# 8. Interactive mini-exercise
# ---------------------------------------------------------------------------
print("--- 8. Try it: number classifier ---")
try:
    raw = input("Enter a number: ").strip()
except EOFError:
    raw = "0"

if raw.lstrip("-").replace(".", "", 1).isdigit():
    num = float(raw)
    if num > 0:
        sign = "positive"
    elif num < 0:
        sign = "negative"
    else:
        sign = "zero"
    print(f"{num} is {sign}.")
else:
    print(f"{raw!r} is not a valid number.")

print()
print("=" * 50)
print("Key ideas:  if / elif / else, and, or, not,")
print("            nested if, truthy/falsy, ternary")
print("=" * 50)
