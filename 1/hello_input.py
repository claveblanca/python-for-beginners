"""
4. Interactive Input
====================

input() pauses the program and waits for the user to type something.
This is the simplest form of a two-way conversation with your program.

HOW TO RUN
----------
    python hello_input.py

WHAT HAPPENS
------------
The program asks questions, you type answers, and it responds.
"""

print("--- Interactive Hello ---")
print()

name = input("What is your name? ").strip()
if not name:
    name = "friend"

color = input(f"Hi {name}! What is your favourite colour? ").strip()
if not color:
    color = "blue"

number = input("Pick a number between 1 and 10: ").strip()

print()
print(f"Nice to meet you, {name}!")
print(f"Your favourite colour is {color}.")

if number.isdigit():
    n = int(number)
    print(f"You picked {n}. Doubled it is {n * 2}.")
else:
    print(f"You typed {number!r} — that is not a number, but that is OK!")

print()
print("You just used: print(), input(), if/else, variables, and f-strings.")
