"""
Making Requests in Python
==========================

The ``requests`` library is the standard way to call web APIs.
If not installed, the script falls back to ``urllib`` (built-in).

Install requests (recommended):
    pip install requests

Run:
    python making_requests.py

All examples use free, public APIs — no key required.
"""

from __future__ import annotations

import json
import sys

# ---------------------------------------------------------------------------
# Pick an HTTP backend
# ---------------------------------------------------------------------------
try:
    import requests as _req

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error

    print("  (requests not installed — using urllib fallback)\n")


def http_get(url: str, params: dict | None = None) -> tuple[int, str]:
    """Simple GET that works with or without the requests library."""
    if HAS_REQUESTS:
        r = _req.get(url, params=params, timeout=10)
        return r.status_code, r.text
    if params:
        from urllib.parse import urlencode
        url = f"{url}?{urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "python-beginner-book"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


# ---------------------------------------------------------------------------
# 1. Simple GET — IP address
# ---------------------------------------------------------------------------
print("--- 1. Simple GET ---")

status, body = http_get("https://httpbin.org/ip")
print(f"  GET https://httpbin.org/ip -> {status}")
print(f"  Body: {body.strip()}")
print()

# ---------------------------------------------------------------------------
# 2. GET with query parameters
# ---------------------------------------------------------------------------
print("--- 2. Query parameters ---")

status, body = http_get("https://httpbin.org/get", params={"name": "Alice", "lang": "Python"})
data = json.loads(body)
print(f"  Status: {status}")
print(f"  Server saw args: {data.get('args', {})}")
print()

# ---------------------------------------------------------------------------
# 3. Response headers
# ---------------------------------------------------------------------------
print("--- 3. Response headers ---")

if HAS_REQUESTS:
    r = _req.get("https://httpbin.org/headers", timeout=10)
    print(f"  Content-Type : {r.headers.get('Content-Type')}")
    print(f"  Server       : {r.headers.get('Server')}")
else:
    req = urllib.request.Request("https://httpbin.org/headers",
                                 headers={"User-Agent": "python-beginner-book"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"  Content-Type : {resp.headers.get('Content-Type')}")
        print(f"  Server       : {resp.headers.get('Server')}")
print()

# ---------------------------------------------------------------------------
# 4. Status code handling
# ---------------------------------------------------------------------------
print("--- 4. Status codes ---")

for url in [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
]:
    status, _ = http_get(url)
    print(f"  {url.split('/')[-1]} -> {status}")
print()

# ---------------------------------------------------------------------------
# 5. Real API — random user
# ---------------------------------------------------------------------------
print("--- 5. Real API: randomuser.me ---")

status, body = http_get("https://randomuser.me/api/")
if status == 200:
    user = json.loads(body)["results"][0]
    name = f"{user['name']['first']} {user['name']['last']}"
    country = user["location"]["country"]
    email = user["login"]["username"]
    print(f"  Random user : {name}")
    print(f"  Country     : {country}")
    print(f"  Username    : {email}")
else:
    print(f"  Could not reach randomuser.me (status {status})")
print()

# ---------------------------------------------------------------------------
# 6. Real API — GitHub user info
# ---------------------------------------------------------------------------
print("--- 6. Real API: GitHub ---")

status, body = http_get("https://api.github.com/users/octocat")
if status == 200:
    gh = json.loads(body)
    print(f"  Login      : {gh['login']}")
    print(f"  Name       : {gh.get('name', 'N/A')}")
    print(f"  Public repos: {gh['public_repos']}")
    print(f"  Followers  : {gh['followers']}")
else:
    print(f"  GitHub API returned {status}")
print()

# ---------------------------------------------------------------------------
# 7. POST with requests (if available)
# ---------------------------------------------------------------------------
print("--- 7. POST request ---")

if HAS_REQUESTS:
    payload = {"title": "Buy milk", "completed": False}
    r = _req.post("https://httpbin.org/post", json=payload, timeout=10)
    resp_data = r.json()
    print(f"  POST -> {r.status_code}")
    print(f"  Server received: {resp_data.get('json', {})}")
else:
    print("  (Skipped — install requests to try POST examples)")
print()

# ---------------------------------------------------------------------------
# 8. Error handling
# ---------------------------------------------------------------------------
print("--- 8. Error handling ---")

try:
    status, body = http_get("https://httpbin.org/status/418")
    print(f"  Status: {status}")
    if status >= 400:
        print("  Handling error: the server returned an error status.")
except Exception as e:
    print(f"  Network error: {e}")
print()

# ---------------------------------------------------------------------------
# 9. Timeout
# ---------------------------------------------------------------------------
print("--- 9. Timeout ---")

try:
    if HAS_REQUESTS:
        _req.get("https://httpbin.org/delay/10", timeout=2)
    else:
        req = urllib.request.Request("https://httpbin.org/delay/10")
        urllib.request.urlopen(req, timeout=2)
    print("  (no timeout)")
except Exception as e:
    print(f"  Caught timeout: {type(e).__name__}: {e}")
print()

print("=" * 50)
print("Key ideas:  requests.get(), .post(), .json(),")
print("            status_code, headers, params,")
print("            timeout, error handling")
print("=" * 50)
