"""
What Are Classes and Objects? / Defining Classes and Creating Objects
=====================================================================

A class is a blueprint.  An object (instance) is a concrete thing
built from that blueprint.  Think of a class as a cookie cutter and
each cookie as an object.

Run:
    python classes_and_objects.py
"""

# ---------------------------------------------------------------------------
# 1. The simplest class
# ---------------------------------------------------------------------------
print("--- 1. The simplest class ---")


class Dog:
    pass


fido = Dog()
rex = Dog()

print(f"  fido = {fido}")
print(f"  rex  = {rex}")
print(f"  Are they the same object? {fido is rex}")
print(f"  Both are Dogs? {isinstance(fido, Dog)} / {isinstance(rex, Dog)}")
print()

# ---------------------------------------------------------------------------
# 2. Adding attributes on the fly
# ---------------------------------------------------------------------------
print("--- 2. Attributes on the fly ---")

fido.name = "Fido"
fido.breed = "Labrador"
rex.name = "Rex"
rex.breed = "German Shepherd"

print(f"  {fido.name} is a {fido.breed}")
print(f"  {rex.name} is a {rex.breed}")
print()

# ---------------------------------------------------------------------------
# 3. A class with __init__ (constructor)
# ---------------------------------------------------------------------------
print("--- 3. __init__ constructor ---")


class Cat:
    def __init__(self, name, color):
        self.name = name
        self.color = color


whiskers = Cat("Whiskers", "orange")
shadow = Cat("Shadow", "black")

print(f"  {whiskers.name} is {whiskers.color}")
print(f"  {shadow.name} is {shadow.color}")
print()

# ---------------------------------------------------------------------------
# 4. Methods — functions that belong to a class
# ---------------------------------------------------------------------------
print("--- 4. Methods ---")


class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        import math
        return math.pi * self.radius ** 2

    def circumference(self):
        import math
        return 2 * math.pi * self.radius

    def describe(self):
        print(f"  Circle(r={self.radius}): area={self.area():.2f}, circ={self.circumference():.2f}")


small = Circle(3)
big = Circle(10)
small.describe()
big.describe()
print()

# ---------------------------------------------------------------------------
# 5. Class vs. instance attributes
# ---------------------------------------------------------------------------
print("--- 5. Class vs. instance attributes ---")


class Counter:
    total_created = 0

    def __init__(self, name):
        self.name = name
        Counter.total_created += 1


c1 = Counter("A")
c2 = Counter("B")
c3 = Counter("C")
print(f"  Created {Counter.total_created} Counter objects")
print(f"  c1.name = {c1.name!r}, c2.name = {c2.name!r}")
print()

# ---------------------------------------------------------------------------
# 6. __str__ and __repr__
# ---------------------------------------------------------------------------
print("--- 6. __str__ and __repr__ ---")


class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def __str__(self):
        return f"{self.title} by {self.author}"

    def __repr__(self):
        return f"Book({self.title!r}, {self.author!r})"


b = Book("1984", "George Orwell")
print(f"  str(b)  -> {b}")
print(f"  repr(b) -> {b!r}")
print()

# ---------------------------------------------------------------------------
# 7. Multiple objects interacting
# ---------------------------------------------------------------------------
print("--- 7. Objects interacting ---")


class Player:
    def __init__(self, name, health=100):
        self.name = name
        self.health = health

    def attack(self, other, damage):
        other.health = max(0, other.health - damage)
        print(f"  {self.name} attacks {other.name} for {damage} dmg -> {other.name} HP: {other.health}")

    def is_alive(self):
        return self.health > 0


hero = Player("Hero")
goblin = Player("Goblin", health=40)

hero.attack(goblin, 25)
goblin.attack(hero, 10)
hero.attack(goblin, 20)
print(f"  Goblin alive? {goblin.is_alive()}")
print()

print("=" * 50)
print("Key ideas:  class, object, __init__, self,")
print("            methods, class attrs, __str__/__repr__")
print("=" * 50)
