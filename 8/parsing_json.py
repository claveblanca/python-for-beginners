"""
Parsing JSON Data
=================

JSON (JavaScript Object Notation) is the standard data format for APIs.
Python's built-in ``json`` module converts between JSON strings and
Python dicts/lists.

Run:
    python parsing_json.py
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).parent / "_output"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. JSON ↔ Python type mapping
# ---------------------------------------------------------------------------
print("--- 1. JSON ↔ Python ---")
print()
print("  JSON            Python")
print("  ────            ──────")
print('  { "key": val }  dict')
print("  [ 1, 2, 3 ]    list")
print('  "hello"         str')
print("  42              int")
print("  3.14            float")
print("  true / false    True / False")
print("  null            None")
print()

# ---------------------------------------------------------------------------
# 2. json.loads — parse a JSON string
# ---------------------------------------------------------------------------
print("--- 2. json.loads (string -> Python) ---")

json_str = '{"name": "Alice", "age": 30, "scores": [92, 88, 95]}'
data = json.loads(json_str)
print(f"  Input:  {json_str}")
print(f"  Output: {data}")
print(f"  type:   {type(data).__name__}")
print(f"  data['name']   = {data['name']!r}")
print(f"  data['scores'] = {data['scores']}")
print()

# ---------------------------------------------------------------------------
# 3. json.dumps — Python to JSON string
# ---------------------------------------------------------------------------
print("--- 3. json.dumps (Python -> string) ---")

python_obj = {
    "city": "Rome",
    "population": 2_873_000,
    "landmarks": ["Colosseum", "Vatican", "Pantheon"],
    "is_capital": True,
}

compact = json.dumps(python_obj)
print(f"  Compact: {compact}")

pretty = json.dumps(python_obj, indent=2)
print(f"  Pretty:\n{pretty}")
print()

# ---------------------------------------------------------------------------
# 4. Reading JSON from a file
# ---------------------------------------------------------------------------
print("--- 4. json.load (file -> Python) ---")

sample_path = OUT / "config.json"
sample_path.write_text(json.dumps({
    "app_name": "MyApp",
    "debug": True,
    "max_retries": 3,
    "allowed_hosts": ["localhost", "example.com"],
}, indent=2))

with open(sample_path) as f:
    config = json.load(f)

print(f"  Loaded from {sample_path.name}:")
for k, v in config.items():
    print(f"    {k}: {v}")
print()

# ---------------------------------------------------------------------------
# 5. Writing JSON to a file
# ---------------------------------------------------------------------------
print("--- 5. json.dump (Python -> file) ---")

users = [
    {"id": 1, "name": "Alice", "active": True},
    {"id": 2, "name": "Bob", "active": False},
    {"id": 3, "name": "Charlie", "active": True},
]

users_path = OUT / "users.json"
with open(users_path, "w") as f:
    json.dump(users, f, indent=2)

print(f"  Wrote {len(users)} users to {users_path.name}")
print()

# ---------------------------------------------------------------------------
# 6. Navigating nested JSON
# ---------------------------------------------------------------------------
print("--- 6. Nested JSON ---")

api_response = json.loads("""
{
    "status": "ok",
    "data": {
        "user": {
            "name": "Alice",
            "address": {
                "city": "Rome",
                "zip": "00100"
            }
        },
        "posts": [
            {"id": 1, "title": "Hello World"},
            {"id": 2, "title": "Python Tips"}
        ]
    }
}
""")

print(f"  Status       : {api_response['status']}")
print(f"  User city    : {api_response['data']['user']['address']['city']}")
print(f"  First post   : {api_response['data']['posts'][0]['title']}")
print()

# ---------------------------------------------------------------------------
# 7. Safe access with .get()
# ---------------------------------------------------------------------------
print("--- 7. Safe access with .get() ---")

incomplete = {"name": "Bob"}
email = incomplete.get("email", "not provided")
print(f"  name  = {incomplete.get('name')!r}")
print(f"  email = {email!r}")
print()

# ---------------------------------------------------------------------------
# 8. Processing a list of JSON records
# ---------------------------------------------------------------------------
print("--- 8. Processing records ---")

records_str = """
[
    {"product": "Widget",    "price": 9.99,  "qty": 150},
    {"product": "Gadget",    "price": 24.50, "qty": 80},
    {"product": "Doohickey", "price": 4.75,  "qty": 300}
]
"""
products = json.loads(records_str)

total_value = sum(p["price"] * p["qty"] for p in products)
most_expensive = max(products, key=lambda p: p["price"])
most_stock = max(products, key=lambda p: p["qty"])

print(f"  Total inventory value : ${total_value:,.2f}")
print(f"  Most expensive        : {most_expensive['product']} (${most_expensive['price']})")
print(f"  Largest stock         : {most_stock['product']} ({most_stock['qty']} units)")
print()

# ---------------------------------------------------------------------------
# 9. Modifying and saving back
# ---------------------------------------------------------------------------
print("--- 9. Modify and save ---")

with open(users_path) as f:
    loaded = json.load(f)

for u in loaded:
    u["email"] = f"{u['name'].lower()}@example.com"

with open(users_path, "w") as f:
    json.dump(loaded, f, indent=2)

print(f"  Added email field to every user in {users_path.name}:")
for u in loaded:
    print(f"    {u['name']}: {u['email']}")
print()

# ---------------------------------------------------------------------------
# 10. Handling invalid JSON
# ---------------------------------------------------------------------------
print("--- 10. Handling invalid JSON ---")

bad_json = '{"name": "Alice", "age": }'
try:
    json.loads(bad_json)
except json.JSONDecodeError as e:
    print(f"  json.loads() raised JSONDecodeError:")
    print(f"    {e}")
print()

print("=" * 50)
print("Key ideas:  json.loads / json.dumps (strings),")
print("            json.load  / json.dump  (files),")
print("            nested access, .get(), indent,")
print("            JSONDecodeError")
print("=" * 50)
