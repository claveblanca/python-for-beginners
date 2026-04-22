"""
Real-World Example — Library Management System
================================================

A mini program that uses classes, __init__, encapsulation, inheritance,
and interaction between objects.

Run:
    python real_world_example.py
"""

from __future__ import annotations

from datetime import date


# ---------------------------------------------------------------------------
# Base: a single item that the library can hold
# ---------------------------------------------------------------------------
class LibraryItem:
    _next_id = 1

    def __init__(self, title: str, year: int):
        self.id = LibraryItem._next_id
        LibraryItem._next_id += 1
        self.title = title
        self.year = year
        self._checked_out_to: Member | None = None

    @property
    def is_available(self) -> bool:
        return self._checked_out_to is None

    def check_out(self, member: Member) -> None:
        if not self.is_available:
            raise ValueError(f"'{self.title}' is already checked out")
        self._checked_out_to = member

    def return_item(self) -> None:
        self._checked_out_to = None

    def __str__(self) -> str:
        status = "available" if self.is_available else f"-> {self._checked_out_to.name}"
        return f"[{self.id}] {self.title} ({self.year}) [{status}]"


# ---------------------------------------------------------------------------
# Subclasses: Book and DVD
# ---------------------------------------------------------------------------
class Book(LibraryItem):
    def __init__(self, title: str, author: str, year: int, pages: int):
        super().__init__(title, year)
        self.author = author
        self.pages = pages

    def __str__(self) -> str:
        base = super().__str__()
        return f"📖 {base}  — {self.author}, {self.pages}p"


class DVD(LibraryItem):
    def __init__(self, title: str, director: str, year: int, minutes: int):
        super().__init__(title, year)
        self.director = director
        self.minutes = minutes

    def __str__(self) -> str:
        base = super().__str__()
        return f"📀 {base}  — dir. {self.director}, {self.minutes}min"


# ---------------------------------------------------------------------------
# A library member who can borrow items
# ---------------------------------------------------------------------------
class Member:
    def __init__(self, name: str, max_items: int = 3):
        self.name = name
        self._max_items = max_items
        self._borrowed: list[LibraryItem] = []

    @property
    def borrowed_count(self) -> int:
        return len(self._borrowed)

    def borrow(self, item: LibraryItem) -> None:
        if self.borrowed_count >= self._max_items:
            raise ValueError(f"{self.name} has reached the limit of {self._max_items} items")
        item.check_out(self)
        self._borrowed.append(item)

    def return_item(self, item: LibraryItem) -> None:
        if item not in self._borrowed:
            raise ValueError(f"{self.name} did not borrow '{item.title}'")
        item.return_item()
        self._borrowed.remove(item)

    def list_borrowed(self) -> list[str]:
        return [f"  {item}" for item in self._borrowed]

    def __str__(self) -> str:
        return f"Member({self.name!r}, borrowed={self.borrowed_count})"


# ---------------------------------------------------------------------------
# The library itself — holds items and members
# ---------------------------------------------------------------------------
class Library:
    def __init__(self, name: str):
        self.name = name
        self._catalog: list[LibraryItem] = []
        self._members: list[Member] = []

    def add_item(self, item: LibraryItem) -> None:
        self._catalog.append(item)

    def register_member(self, member: Member) -> None:
        self._members.append(member)

    def search(self, query: str) -> list[LibraryItem]:
        q = query.lower()
        return [item for item in self._catalog if q in item.title.lower()]

    def available_items(self) -> list[LibraryItem]:
        return [item for item in self._catalog if item.is_available]

    def print_catalog(self) -> None:
        print(f"\n  === {self.name} catalog ({len(self._catalog)} items) ===")
        for item in self._catalog:
            print(f"  {item}")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def main() -> None:
    lib = Library("City Library")

    b1 = Book("1984", "George Orwell", 1949, 328)
    b2 = Book("To Kill a Mockingbird", "Harper Lee", 1960, 281)
    b3 = Book("The Pragmatic Programmer", "Hunt & Thomas", 1999, 352)
    d1 = DVD("Inception", "Christopher Nolan", 2010, 148)
    d2 = DVD("The Matrix", "Wachowskis", 1999, 136)

    for item in [b1, b2, b3, d1, d2]:
        lib.add_item(item)

    alice = Member("Alice")
    bob = Member("Bob", max_items=2)
    lib.register_member(alice)
    lib.register_member(bob)

    lib.print_catalog()

    # Alice borrows two items
    print("\n  --- Alice borrows ---")
    alice.borrow(b1)
    print(f"  {alice}")
    alice.borrow(d1)
    print(f"  {alice}")
    for line in alice.list_borrowed():
        print(line)

    # Bob tries to borrow
    print("\n  --- Bob borrows ---")
    bob.borrow(b3)
    print(f"  {bob}")

    try:
        bob.borrow(b1)
    except ValueError as e:
        print(f"  Error: {e}")

    # Show catalog status
    lib.print_catalog()

    # Search
    print("\n  --- Search 'the' ---")
    for item in lib.search("the"):
        print(f"  {item}")

    # Alice returns a book
    print("\n  --- Alice returns 1984 ---")
    alice.return_item(b1)
    print(f"  {alice}")

    # Available items
    print("\n  --- Available items ---")
    for item in lib.available_items():
        print(f"  {item}")

    print()
    print("=" * 60)
    print("This example used: classes, __init__, @property,")
    print("encapsulation (_private), inheritance (Book/DVD),")
    print("__str__, interaction between objects (Library/Member/Item)")
    print("=" * 60)


if __name__ == "__main__":
    main()
