"""
1. Running Python in Interactive Mode (REPL)
=============================================

The REPL (Read-Eval-Print Loop) lets you type Python one line at a time
and see results instantly.  It is the fastest way to experiment.

HOW TO START
------------
Open a terminal and type:

    python

or (on Mac / Linux):

    python3

You will see the >>> prompt.  Try typing each line below, one at a time,
and press Enter after each one.

EXAMPLE SESSION
---------------
>>> print("Hello, world!")
Hello, world!

>>> 2 + 3
5

>>> name = "Python"
>>> print(f"I am learning {name}!")
I am learning Python!

>>> type(42)
<class 'int'>

>>> type("hello")
<class 'str'>

>>> exit()           # leave the REPL

TIP
---
You can also run this file as a normal script to see the same outputs:

    python hello_repl.py
"""

print("--- REPL demo (running as a script) ---")
print()

print('>>> print("Hello, world!")')
print("Hello, world!")
print()

print(">>> 2 + 3")
print(2 + 3)
print()

name = "Python"
print('>>> name = "Python"')
print(f'>>> print(f"I am learning {{name}}!")')
print(f"I am learning {name}!")
print()

print(">>> type(42)")
print(type(42))
print()

print(">>> type('hello')")
print(type("hello"))
print()

print("Type  python  or  python3  in your terminal to try it yourself!")
