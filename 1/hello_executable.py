#!/usr/bin/env python3
"""
3. Running as an Executable Script (Linux / macOS)
===================================================

The first line (#!/usr/bin/env python3) is called a "shebang".
It tells the operating system which program should interpret this file.

HOW TO USE
----------
Step 1 — make the file executable (one time only):

    chmod +x hello_executable.py

Step 2 — run it directly:

    ./hello_executable.py

On Windows this is not needed; just use  python hello_executable.py .

WHAT HAPPENS
------------
The OS reads the shebang, finds python3, and hands it the file.
You do not need to type "python" in front.
"""

import platform
import sys

print("Hello from an executable script!")
print(f"Python version : {platform.python_version()}")
print(f"Interpreter    : {sys.executable}")
print(f"Operating system: {platform.system()} {platform.release()}")
