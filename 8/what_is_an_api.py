"""
What Is an API?
===============

API = Application Programming Interface.
It is a set of rules that lets programs talk to each other.

A Web API works over HTTP:
  - Your program sends a REQUEST to a URL (the "endpoint").
  - The server sends back a RESPONSE, usually in JSON format.

This script does NOT call the internet.  It demonstrates the concept
with a local "fake" API so you can understand the flow first.

Run:
    python what_is_an_api.py
"""

from __future__ import annotations

import json

# ---------------------------------------------------------------------------
# 1. The request / response model
# ---------------------------------------------------------------------------
print("--- 1. How an API works ---")
print()
print("  You (client)              Server (API)")
print("  ─────────────             ────────────")
print("  GET /users/42   ──────>   Look up user 42")
print("                  <──────   { id: 42, name: 'Alice' }")
print()
print("  Key parts of a request:")
print("    • Method  : GET, POST, PUT, DELETE")
print("    • URL     : https://api.example.com/users/42")
print("    • Headers : metadata (content type, auth token)")
print("    • Body    : data you send (for POST/PUT)")
print()
print("  Key parts of a response:")
print("    • Status  : 200 OK, 404 Not Found, 500 Server Error")
print("    • Headers : metadata")
print("    • Body    : the data (usually JSON)")
print()

# ---------------------------------------------------------------------------
# 2. Common HTTP status codes
# ---------------------------------------------------------------------------
print("--- 2. Common status codes ---")
codes = {
    200: "OK — request succeeded",
    201: "Created — new resource was created",
    400: "Bad Request — something wrong with your request",
    401: "Unauthorized — need authentication",
    403: "Forbidden — not allowed",
    404: "Not Found — resource does not exist",
    429: "Too Many Requests — rate limited",
    500: "Internal Server Error — server problem",
}
for code, desc in codes.items():
    print(f"  {code}  {desc}")
print()

# ---------------------------------------------------------------------------
# 3. Simulated API (no internet needed)
# ---------------------------------------------------------------------------
print("--- 3. Simulated API ---")

FAKE_DB = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com", "role": "user"},
}


def fake_api_get_user(user_id: int) -> tuple[int, dict]:
    """Simulate GET /users/{id}.  Returns (status_code, body)."""
    if user_id in FAKE_DB:
        return 200, FAKE_DB[user_id]
    return 404, {"error": "User not found"}


def fake_api_list_users() -> tuple[int, list[dict]]:
    """Simulate GET /users.  Returns (status_code, body)."""
    return 200, list(FAKE_DB.values())


status, body = fake_api_get_user(1)
print(f"  GET /users/1 -> {status}")
print(f"  Body: {json.dumps(body, indent=4)}")
print()

status, body = fake_api_get_user(99)
print(f"  GET /users/99 -> {status}")
print(f"  Body: {json.dumps(body, indent=4)}")
print()

status, users = fake_api_list_users()
print(f"  GET /users -> {status}  ({len(users)} users)")
for u in users:
    print(f"    {u['name']:10s} {u['email']}")
print()

# ---------------------------------------------------------------------------
# 4. REST conventions
# ---------------------------------------------------------------------------
print("--- 4. REST API conventions ---")
print()
print("  Method   URL              Action")
print("  ──────   ───              ──────")
print("  GET      /users           List all users")
print("  GET      /users/42        Get one user")
print("  POST     /users           Create a new user")
print("  PUT      /users/42        Update user 42 (full)")
print("  PATCH    /users/42        Update user 42 (partial)")
print("  DELETE   /users/42        Delete user 42")
print()

# ---------------------------------------------------------------------------
# 5. What you need to call a real API
# ---------------------------------------------------------------------------
print("--- 5. What you need ---")
print()
print("  1. The base URL        (e.g. https://api.github.com)")
print("  2. The endpoint path   (e.g. /users/octocat)")
print("  3. An HTTP library     (requests — see next script)")
print("  4. Sometimes an API key or token")
print()
print("  Next file: making_requests.py  (calls real APIs)")
print()

print("=" * 50)
print("Key ideas:  client/server, HTTP methods,")
print("            status codes, endpoints, REST, JSON")
print("=" * 50)
