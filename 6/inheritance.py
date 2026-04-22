"""
Inheritance
===========

Inheritance lets a new class (child) reuse and extend the behaviour
of an existing class (parent).

Run:
    python inheritance.py
"""

# ---------------------------------------------------------------------------
# 1. Basic inheritance
# ---------------------------------------------------------------------------
print("--- 1. Basic inheritance ---")


class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound"

    def __str__(self):
        return f"Animal({self.name!r})"


class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"


class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"


dog = Dog("Rex")
cat = Cat("Whiskers")
generic = Animal("Mystery")

for a in [dog, cat, generic]:
    print(f"  {a!s:24s} -> {a.speak()}")
print()

# ---------------------------------------------------------------------------
# 2. super() — calling the parent
# ---------------------------------------------------------------------------
print("--- 2. super() ---")


class Vehicle:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

    def info(self):
        return f"{self.year} {self.make} {self.model}"


class ElectricCar(Vehicle):
    def __init__(self, make, model, year, battery_kwh):
        super().__init__(make, model, year)
        self.battery_kwh = battery_kwh

    def info(self):
        base = super().info()
        return f"{base} ({self.battery_kwh} kWh battery)"


car = ElectricCar("Tesla", "Model 3", 2024, 75)
print(f"  {car.info()}")
print()

# ---------------------------------------------------------------------------
# 3. isinstance and issubclass
# ---------------------------------------------------------------------------
print("--- 3. isinstance / issubclass ---")
print(f"  isinstance(dog, Dog)    = {isinstance(dog, Dog)}")
print(f"  isinstance(dog, Animal) = {isinstance(dog, Animal)}")
print(f"  isinstance(dog, Cat)    = {isinstance(dog, Cat)}")
print(f"  issubclass(Dog, Animal) = {issubclass(Dog, Animal)}")
print(f"  issubclass(Animal, Dog) = {issubclass(Animal, Dog)}")
print()

# ---------------------------------------------------------------------------
# 4. Adding new methods in the child
# ---------------------------------------------------------------------------
print("--- 4. Extending a child class ---")


class Bird(Animal):
    def __init__(self, name, can_fly=True):
        super().__init__(name)
        self.can_fly = can_fly

    def speak(self):
        return f"{self.name} says Tweet!"

    def flight_status(self):
        return "can fly" if self.can_fly else "cannot fly"


sparrow = Bird("Sparrow")
penguin = Bird("Penguin", can_fly=False)
print(f"  {sparrow.name}: {sparrow.speak()}, {sparrow.flight_status()}")
print(f"  {penguin.name}: {penguin.speak()}, {penguin.flight_status()}")
print()

# ---------------------------------------------------------------------------
# 5. Multiple inheritance (brief intro)
# ---------------------------------------------------------------------------
print("--- 5. Multiple inheritance ---")


class Swimmer:
    def swim(self):
        return f"{self.name} is swimming"


class Flyer:
    def fly(self):
        return f"{self.name} is flying"


class Duck(Animal, Swimmer, Flyer):
    def speak(self):
        return f"{self.name} says Quack!"


donald = Duck("Donald")
print(f"  {donald.speak()}")
print(f"  {donald.swim()}")
print(f"  {donald.fly()}")
print(f"  MRO: {[c.__name__ for c in Duck.__mro__]}")
print()

# ---------------------------------------------------------------------------
# 6. Abstract base class (preview)
# ---------------------------------------------------------------------------
print("--- 6. Abstract base class ---")

from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        ...

    @abstractmethod
    def perimeter(self):
        ...

    def describe(self):
        print(f"  {self.__class__.__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}")


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class CircleShape(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        import math
        return math.pi * self.radius ** 2

    def perimeter(self):
        import math
        return 2 * math.pi * self.radius


try:
    s = Shape()
except TypeError as e:
    print(f"  Shape() -> TypeError: {e}")

rect = Rectangle(5, 3)
circ = CircleShape(7)
rect.describe()
circ.describe()
print()

print("=" * 50)
print("Key ideas:  class Child(Parent), super(),")
print("            method overriding, isinstance,")
print("            multiple inheritance, ABC")
print("=" * 50)
