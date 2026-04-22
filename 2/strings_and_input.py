"""
Strings and User Input
======================

Strings are sequences of characters.  Python gives you many ways to
create, combine, search, and transform them.

Run:
    python strings_and_input.py
"""

# ---------------------------------------------------------------------------
# 1. Creating strings
# ---------------------------------------------------------------------------
print("--- 1. Creating strings ---")
single = 'Hello'
double = "World"
multi = """This string
spans multiple
lines."""

print(f"single quotes: {single}")
print(f"double quotes: {double}")
print(f"triple quotes:\n{multi}")
print()

# ---------------------------------------------------------------------------
# 2. Concatenation and repetition
# ---------------------------------------------------------------------------
print("--- 2. Concatenation & repetition ---")
full = single + ", " + double + "!"
print(f"single + ', ' + double + '!' -> {full}")
echo = "ha" * 3
print(f'"ha" * 3 -> {echo}')
print()

# ---------------------------------------------------------------------------
# 3. f-strings (formatted string literals)
# ---------------------------------------------------------------------------
print("--- 3. f-strings ---")
item = "coffee"
price = 3.5
print(f"One {item} costs ${price:.2f}.")
print(f"Upper: {item.upper()}, Length: {len(item)} characters.")
print()

# ---------------------------------------------------------------------------
# 4. Useful string methods
# ---------------------------------------------------------------------------
print("--- 4. Common string methods ---")
text = "  Hello, Python World!  "
print(f"original          : {text!r}")
print(f".strip()          : {text.strip()!r}")
print(f".lower()          : {text.lower()!r}")
print(f".upper()          : {text.upper()!r}")
print(f".replace('World', 'Earth') : {text.replace('World', 'Earth')!r}")
print(f".split(',')       : {text.split(',')}")
print(f".startswith('  H'): {text.startswith('  H')}")
print(f".find('Python')   : index {text.find('Python')}")
print()

# ---------------------------------------------------------------------------
# 5. Indexing and slicing
# ---------------------------------------------------------------------------
print("--- 5. Indexing & slicing ---")
word = "Python"
print(f"word          = {word!r}")
print(f"word[0]       = {word[0]!r}   (first character)")
print(f"word[-1]      = {word[-1]!r}   (last character)")
print(f"word[0:3]     = {word[0:3]!r}  (first three)")
print(f"word[2:]      = {word[2:]!r}")
print(f"word[::-1]    = {word[::-1]!r} (reversed)")
print()

# ---------------------------------------------------------------------------
# 6. Escape characters
# ---------------------------------------------------------------------------
print("--- 6. Escape characters ---")
print("Newline:    Hello\\nWorld  ->")
print("Hello\nWorld")
print(f"Tab:        Hello\\tWorld  -> Hello\tWorld")
print(f"Backslash:  C:\\\\Users     -> C:\\Users")
print(f"Quote:      She said \\\"hi\\\" -> She said \"hi\"")
print()

# ---------------------------------------------------------------------------
# 7. User input
# ---------------------------------------------------------------------------
print("--- 7. User input ---")
print("input() always returns a string — convert if you need a number.")
print()

try:
    first = input("Enter your first name: ").strip()
    last = input("Enter your last name:  ").strip()
    birth_year = input("Enter your birth year: ").strip()
except EOFError:
    first, last, birth_year = "Jane", "Doe", "2000"

if not first:
    first = "Jane"
if not last:
    last = "Doe"

full_name = f"{first.capitalize()} {last.capitalize()}"
print(f"\nFull name: {full_name}")
print(f"Initials:  {first[0].upper()}.{last[0].upper()}.")

if birth_year.isdigit():
    approx_age = 2026 - int(birth_year)
    print(f"You are approximately {approx_age} years old.")
else:
    print(f"{birth_year!r} is not a valid year.")

print()
print("=" * 50)
print("Key ideas:  f-strings, .strip(), .split(), .upper(),")
print("            indexing [0], slicing [a:b], input()")
print("=" * 50)
