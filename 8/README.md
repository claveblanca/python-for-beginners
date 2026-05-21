# Chapter 8 — Working with APIs and JSON

What an API is, how to call one from Python, and how to parse the data that comes back.

## Prerequisites

- Python 3.10+ installed
- Completed [Chapter 7](../7/) (file handling)
- `requests` library recommended: `pip install requests` (scripts fall back to `urllib` if missing)

## The files

| # | File | Topic |
|---|------|-------|
| 1 | `what_is_an_api.py` | HTTP request/response model, status codes, REST conventions, simulated API (no internet) |
| 2 | `making_requests.py` | `requests.get()` / `.post()`, query params, headers, status handling, timeout, real public APIs |
| 3 | `parsing_json.py` | `json.loads`/`dumps`, `json.load`/`dump`, nested access, `.get()`, modifying & saving, error handling |

## How to run

```bash
cd 8
python what_is_an_api.py          # no internet needed
python making_requests.py         # calls free public APIs
python parsing_json.py            # no internet needed
```

## Concepts introduced

### What Is an API?
- Client / server model
- HTTP methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- URL = base + endpoint
- Request: method, URL, headers, body
- Response: status code, headers, body (JSON)
- Common status codes: 200, 201, 400, 401, 403, 404, 429, 500
- REST conventions (resource-based URLs)

### Making Requests in Python
- `requests.get(url, params=…, timeout=…)` — the standard library
- `response.status_code`, `.text`, `.json()`, `.headers`
- Query parameters (passed as a dict)
- `requests.post(url, json=…)` — send data
- Error handling and timeouts
- Fallback with `urllib.request` (built-in, no install needed)
- Real APIs used: httpbin.org, randomuser.me, api.github.com

### Parsing JSON Data
- JSON ↔ Python type mapping (dict, list, str, int, float, bool, None)
- `json.loads(string)` → Python object
- `json.dumps(obj, indent=2)` → formatted string
- `json.load(file)` / `json.dump(obj, file)` — read/write files
- Navigating nested structures: `data['a']['b'][0]`
- Safe access with `.get(key, default)`
- Processing lists of records (sum, max, filter)
- Modifying JSON and saving back
- `json.JSONDecodeError` — handling broken JSON

## Technologies Used

- **`requests`** — HTTP client for calling REST APIs
- **`json`** — parsing and building JSON payloads
- **httpbin.org** — public HTTP testing service
- **randomuser.me** — public random-user data API
- **GitHub REST API** — real-world API example
