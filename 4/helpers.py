"""
helpers.py — a utility module imported by code_organization.py
==============================================================

This file is NOT run on its own.  It demonstrates how to put reusable
functions in a separate file and import them elsewhere.
"""

from __future__ import annotations


def is_even(n: int) -> bool:
    return n % 2 == 0


def clamp(value: float, lo: float, hi: float) -> float:
    """Restrict *value* to the range [lo, hi]."""
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value


def title_case(text: str) -> str:
    """Capitalize the first letter of every word."""
    return " ".join(word.capitalize() for word in text.split())


def fahrenheit_to_celsius(f: float) -> float:
    return (f - 32) * 5 / 9
