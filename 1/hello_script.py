"""
2. Running a Python Script File
================================

This is the most common way to run Python: write code in a .py file,
then execute it from the terminal.

HOW TO RUN
----------
    python hello_script.py

or:

    python3 hello_script.py

WHAT HAPPENS
------------
Python reads the file top-to-bottom and runs every line.
Output appears in the terminal.
"""

# --- Variables ---
message = "Hello, world!"
author = "a Python script file"

# --- Print ---
print(message)
print(f"This was printed by {author}.")

# --- Simple math ---
width = 10
height = 5
area = width * height
print(f"A {width}x{height} rectangle has area {area}.")

# --- A list ---
fruits = ["apple", "banana", "cherry"]
print(f"Fruits: {fruits}")
print(f"First fruit: {fruits[0]}")
print(f"Number of fruits: {len(fruits)}")
