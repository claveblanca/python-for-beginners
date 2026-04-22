# Chapter 6 — Object-Oriented Programming in Python

Classes, objects, encapsulation, inheritance, and a full real-world example.

## Prerequisites

- Python 3.10+ installed
- Completed [Chapter 5](../5/) (data structures)

## The files

| # | File | Topic |
|---|------|-------|
| 1 | `classes_and_objects.py` | Classes, objects, `__init__`, methods, class attrs, `__str__`/`__repr__` |
| 2 | `encapsulation.py` | Public / `_protected` / `__private`, `@property`, validation, read-only |
| 3 | `inheritance.py` | Parent/child, `super()`, overriding, `isinstance`, multiple inheritance, ABC |
| 4 | `real_world_example.py` | Library management system combining all OOP concepts |

## How to run

```bash
cd 6
python classes_and_objects.py
python encapsulation.py
python inheritance.py
python real_world_example.py
```

## Concepts introduced

### What Are Classes and Objects?
- A class is a blueprint; an object is an instance of that class
- `class Dog: pass` — the simplest class
- Creating objects: `fido = Dog()`
- `isinstance()` — check an object's type

### Defining Classes and Creating Objects
- Attaching attributes on the fly vs. using `__init__`
- Multiple objects from the same class

### Attributes and Methods
- Instance attributes (`self.x`) vs. class attributes
- Methods — functions defined inside a class
- `__str__` and `__repr__` for string representation

### The `__init__` Method (Constructors)
- Automatically called when creating an object
- `self` — reference to the current instance
- Initializing attributes with parameters

### Encapsulation
- `_protected` — convention for internal use
- `__private` — name-mangled to discourage direct access
- Manual getters/setters
- `@property` / `@x.setter` — the Pythonic way
- Validation inside setters
- Read-only properties (no setter)

### Inheritance
- `class Child(Parent)` — reuse parent behaviour
- `super().__init__()` — call the parent constructor
- Method overriding — replace parent behaviour in the child
- `isinstance()` / `issubclass()`
- Multiple inheritance and MRO
- Abstract Base Class (`ABC`, `@abstractmethod`)

### Real-World Example
- **Library management system** with:
  - `LibraryItem` (base) -> `Book`, `DVD` (children)
  - `Member` — borrows/returns items with a limit
  - `Library` — catalog, search, availability
  - Encapsulation, properties, inheritance, object interaction
