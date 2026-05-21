# Chapter 14 — Kraken Bitcoin Ticker (API + Database)

Two versions:
1. **CLI version** — Fetch tickers and display stats in the terminal
2. **Web UI version** — Live-updating dashboard in your browser

Both fetch live cryptocurrency prices from the Kraken exchange and store every snapshot in SQLite.

## Prerequisites

- Python 3.10+
- Internet connection (calls the Kraken public API — no key needed)

### CLI version (stdlib only)
No additional packages needed (`urllib`, `json`, `sqlite3` are built-in)

### Web UI version
```bash
pip install flask
```

## The files

| File | What it does |
|------|-------------|
| `kraken_ticker.py` | CLI tool: Fetches BTC/USD ticker, stores in `:memory:` SQLite, prints terminal stats |
| `kraken_ticker_web.py` | Web UI: Flask dashboard with auto-refreshing live ticker data |

## How to run

### CLI version

```bash
cd 14

# Fetch once and show the result
python kraken_ticker.py

# Fetch 6 times, 10 seconds apart
python kraken_ticker.py --interval 10 --count 6

# Use a different pair (ETH/USD)
python kraken_ticker.py --pair XETHZUSD
```

### Web UI version

```bash
cd 14

# Start the web server (fetches every 10 seconds by default)
python kraken_ticker_web.py

# Then visit: http://localhost:5000 in your browser
```

**Options:**
```bash
python kraken_ticker_web.py --pair XETHZUSD --interval 5 --port 8000 --host 0.0.0.0
```

## What it demonstrates

| Concept | Where |
|---------|-------|
| Calling a REST API with `urllib.request` | `fetch_ticker()` |
| Parsing JSON responses | `json.loads()` on the Kraken response |
| In-memory SQLite (`sqlite3.connect(":memory:")`) | CLI version: `create_db()` |
| File-based SQLite persistence | Web version: `get_db()` with `ticker_data.db` |
| `CREATE TABLE`, `INSERT`, `SELECT` with aggregates | All queries |
| Parameterized queries (SQL injection safe) | All `conn.execute(…, (params,))` calls |
| `argparse` with `--pair`, `--interval`, `--count` | CLI `build_parser()` |
| `datetime` with UTC timezone | `fetched_at` timestamps |
| Scheduled polling with `time.sleep()` | CLI main loop, web `background_fetcher()` |
| Flask web framework | Web version: `@app.route()`, `render_template_string()` |
| RESTful API endpoints | Web `/api/ticker` returning JSON |
| Threading for background tasks | Web: `background_fetcher()` in daemon thread |
| JavaScript fetch + DOM updates | Web: client-side auto-refresh |
| Responsive CSS styling | Web: gradient, grid layout, mobile-friendly |
| Error handling for network failures | Both versions: `try/except` around `fetch_ticker()` |

## Kraken Ticker API

Endpoint: `https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD`

The response fields used:

| Key | Meaning |
|-----|---------|
| `a[0]` | Ask price |
| `b[0]` | Bid price |
| `c[0]` | Last trade price |
| `v[1]` | Volume (24h) |
| `p[1]` | VWAP (24h) |
| `h[1]` | High (24h) |
| `l[1]` | Low (24h) |
| `o` | Opening price |
| `t[1]` | Number of trades (24h) |

Docs: https://docs.kraken.com/api/docs/rest-api/get-ticker-information

## File comparison

| Feature | CLI (`kraken_ticker.py`) | Web (`kraken_ticker_web.py`) |
|---------|--------------------------|------------------------------|
| Storage | `:memory:` (temp) | `ticker_data.db` (persistent) |
| UI | Terminal tables | Browser dashboard |
| Refresh | One-shot or polling | Continuous background thread |
| Threading | Single-threaded | Background fetcher + Flask |
| Dependencies | Stdlib only | Flask required |
| Best for | Quick checks, scripting | Live monitoring, real-time display |

## Technologies Used

- **Flask** — live web dashboard for real-time ticker display
- **sqlite3** — local time-series storage for price history
- **Kraken public REST API** — cryptocurrency ticker data source (`api.kraken.com`)
