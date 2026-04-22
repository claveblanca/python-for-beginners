"""
Writing Simple Programs
=======================

Five small programs that combine conditionals and loops.
Each one is a standalone function you can study and modify.

Run:
    python simple_programs.py
"""


# ---------------------------------------------------------------------------
# Program 1: Guess the number
# ---------------------------------------------------------------------------
def guess_the_number() -> None:
    """The computer picks a number; the user guesses."""
    import random

    secret = random.randint(1, 20)
    attempts = 0
    max_attempts = 5

    print(f"I picked a number between 1 and 20. You have {max_attempts} tries.")

    while attempts < max_attempts:
        attempts += 1
        try:
            raw = input(f"  Guess #{attempts}: ").strip()
        except EOFError:
            raw = str(secret)

        if not raw.isdigit():
            print("  Please enter a whole number.")
            continue

        guess = int(raw)
        if guess == secret:
            print(f"  Correct! You got it in {attempts} {'try' if attempts == 1 else 'tries'}.")
            return
        elif guess < secret:
            print("  Too low.")
        else:
            print("  Too high.")

    print(f"  Out of tries! The number was {secret}.")


# ---------------------------------------------------------------------------
# Program 2: FizzBuzz (classic interview question)
# ---------------------------------------------------------------------------
def fizzbuzz(n: int = 30) -> None:
    """Print 1..n, but multiples of 3 -> Fizz, 5 -> Buzz, both -> FizzBuzz."""
    for i in range(1, n + 1):
        if i % 15 == 0:
            print("  FizzBuzz")
        elif i % 3 == 0:
            print("  Fizz")
        elif i % 5 == 0:
            print("  Buzz")
        else:
            print(f"  {i}")


# ---------------------------------------------------------------------------
# Program 3: Sum calculator (while loop + sentinel)
# ---------------------------------------------------------------------------
def sum_calculator() -> None:
    """Keep adding numbers until the user types 'done'."""
    total = 0.0
    count = 0
    inputs = ["10", "25.5", "3", "done"]

    print("Enter numbers one at a time. Type 'done' to finish.")
    print("(Auto-running with sample inputs:", inputs, ")")

    for raw in inputs:
        print(f"  > {raw}")
        if raw.lower() == "done":
            break
        try:
            total += float(raw)
            count += 1
        except ValueError:
            print(f"  '{raw}' is not a number — skipped.")

    if count:
        print(f"  Sum: {total}  |  Count: {count}  |  Average: {total / count:.2f}")
    else:
        print("  No numbers entered.")


# ---------------------------------------------------------------------------
# Program 4: Simple password validator
# ---------------------------------------------------------------------------
def password_validator() -> None:
    """Check a password against basic rules."""
    passwords = ["hi", "hello123", "Hello123", "H3llo!world"]

    for pw in passwords:
        errors: list[str] = []
        if len(pw) < 8:
            errors.append("too short (need 8+ characters)")
        if not any(c.isupper() for c in pw):
            errors.append("needs an uppercase letter")
        if not any(c.islower() for c in pw):
            errors.append("needs a lowercase letter")
        if not any(c.isdigit() for c in pw):
            errors.append("needs a digit")

        if errors:
            print(f"  {pw!r:16s} WEAK  — {', '.join(errors)}")
        else:
            print(f"  {pw!r:16s} OK")


# ---------------------------------------------------------------------------
# Program 5: Pattern printer (nested loops)
# ---------------------------------------------------------------------------
def pattern_printer() -> None:
    """Print a right-aligned triangle of stars."""
    rows = 6
    for i in range(1, rows + 1):
        spaces = " " * (rows - i)
        stars = "*" * (2 * i - 1)
        print(f"  {spaces}{stars}")


# ---------------------------------------------------------------------------
# Run all programs
# ---------------------------------------------------------------------------
def main() -> None:
    programs = [
        ("Program 1: Guess the Number", guess_the_number),
        ("Program 2: FizzBuzz (1–30)", lambda: fizzbuzz(30)),
        ("Program 3: Sum Calculator", sum_calculator),
        ("Program 4: Password Validator", password_validator),
        ("Program 5: Pattern Printer", pattern_printer),
    ]

    for title, fn in programs:
        print()
        print("=" * 50)
        print(title)
        print("=" * 50)
        fn()

    print()
    print("-" * 50)
    print("All five programs use only: if/elif/else,")
    print("for, while, break, continue, and functions.")
    print("-" * 50)


if __name__ == "__main__":
    main()
