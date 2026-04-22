"""
Encapsulation
=============

Encapsulation means bundling data with the methods that operate on it,
and controlling access to that data so it cannot be changed in unexpected ways.

Python uses naming conventions (not strict enforcement):
- public:     name
- protected:  _name   (hint: internal use)
- private:    __name  (name-mangled to prevent accidental access)

Run:
    python encapsulation.py
"""

# ---------------------------------------------------------------------------
# 1. Public, protected, and private attributes
# ---------------------------------------------------------------------------
print("--- 1. Naming conventions ---")


class Account:
    def __init__(self, owner, balance):
        self.owner = owner          # public
        self._currency = "USD"      # protected (convention)
        self.__balance = balance    # private (name-mangled)

    def __str__(self):
        return f"Account({self.owner!r}, {self.__balance} {self._currency})"


acc = Account("Alice", 1000)
print(f"  acc.owner     = {acc.owner!r}        (public)")
print(f"  acc._currency = {acc._currency!r}      (protected — accessible but 'private by convention')")

try:
    print(acc.__balance)
except AttributeError as e:
    print(f"  acc.__balance -> AttributeError: {e}")

print(f"  acc._Account__balance = {acc._Account__balance}  (name-mangled — don't do this!)")
print()

# ---------------------------------------------------------------------------
# 2. Getters and setters (manual)
# ---------------------------------------------------------------------------
print("--- 2. Getters / setters ---")


class Temperature:
    def __init__(self, celsius):
        self.__celsius = celsius

    def get_celsius(self):
        return self.__celsius

    def set_celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self.__celsius = value

    def get_fahrenheit(self):
        return self.__celsius * 9 / 5 + 32


t = Temperature(25)
print(f"  {t.get_celsius()}°C = {t.get_fahrenheit():.1f}°F")

t.set_celsius(100)
print(f"  {t.get_celsius()}°C = {t.get_fahrenheit():.1f}°F")

try:
    t.set_celsius(-300)
except ValueError as e:
    print(f"  set_celsius(-300) -> ValueError: {e}")
print()

# ---------------------------------------------------------------------------
# 3. @property — the Pythonic way
# ---------------------------------------------------------------------------
print("--- 3. @property (Pythonic getters/setters) ---")


class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, amount):
        if amount < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = amount

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self._balance += amount

    def withdraw(self, amount):
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount

    def __str__(self):
        return f"{self.owner}: ${self._balance:,.2f}"


ba = BankAccount("Bob", 500)
print(f"  {ba}")
print(f"  ba.balance = {ba.balance}  (looks like an attribute, actually calls @property)")

ba.deposit(200)
print(f"  deposit(200) -> {ba}")

ba.withdraw(150)
print(f"  withdraw(150) -> {ba}")

try:
    ba.balance = -100
except ValueError as e:
    print(f"  ba.balance = -100 -> ValueError: {e}")

try:
    ba.withdraw(9999)
except ValueError as e:
    print(f"  withdraw(9999) -> ValueError: {e}")
print()

# ---------------------------------------------------------------------------
# 4. Read-only property
# ---------------------------------------------------------------------------
print("--- 4. Read-only property ---")


class Square:
    def __init__(self, side):
        self._side = side

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, value):
        if value <= 0:
            raise ValueError("Side must be positive")
        self._side = value

    @property
    def area(self):
        return self._side ** 2


sq = Square(5)
print(f"  side={sq.side}, area={sq.area}")
sq.side = 10
print(f"  side={sq.side}, area={sq.area}")

try:
    sq.area = 99
except AttributeError as e:
    print(f"  sq.area = 99 -> AttributeError: {e}")
print()

print("=" * 50)
print("Key ideas:  _protected, __private (mangled),")
print("            @property, @x.setter, validation,")
print("            read-only properties")
print("=" * 50)
