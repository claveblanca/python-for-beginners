#!/usr/bin/env python3
"""
Kraken Bitcoin Ticker Web UI
=============================

An enhanced version of kraken_ticker.py that runs a Flask web server
with a live-updating dashboard to visualize ticker data.

The app:
  - Fetches tickers from Kraken API in a background thread
  - Stores every snapshot in SQLite (file-based for persistence)
  - Serves a web UI at http://localhost:5000
  - Auto-refreshes every 5 seconds

Install dependencies:
    pip install flask

Run:
    python kraken_ticker_web.py
    # Then visit http://localhost:5000 in your browser
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

from flask import Flask, render_template_string, jsonify

KRAKEN_TICKER_URL = "https://api.kraken.com/0/public/Ticker"
DEFAULT_PAIR = "XXBTZUSD"
DB_FILE = "ticker_data.db"

app = Flask(__name__)
db_lock = threading.Lock()


# ─── database layer ──────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    """Get or create the SQLite database."""
    db_path = Path(DB_FILE)
    exists = db_path.exists()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    if not exists:
        conn.execute(dedent("""\
            CREATE TABLE ticker (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                pair        TEXT    NOT NULL,
                ask_price   REAL    NOT NULL,
                bid_price   REAL    NOT NULL,
                last_price  REAL    NOT NULL,
                volume_24h  REAL    NOT NULL,
                vwap_24h    REAL    NOT NULL,
                high_24h    REAL    NOT NULL,
                low_24h     REAL    NOT NULL,
                open_price  REAL    NOT NULL,
                trades_24h  INTEGER NOT NULL,
                fetched_at  TEXT    NOT NULL
            )
        """))
        conn.commit()

    return conn


def insert_tick(pair: str, tick: dict) -> int:
    """Insert one ticker row and return the id."""
    with db_lock:
        conn = get_db()
        try:
            cur = conn.execute(
                dedent("""\
                    INSERT INTO ticker
                        (pair, ask_price, bid_price, last_price, volume_24h,
                         vwap_24h, high_24h, low_24h, open_price, trades_24h, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """),
                (
                    pair,
                    float(tick["a"][0]),
                    float(tick["b"][0]),
                    float(tick["c"][0]),
                    float(tick["v"][1]),
                    float(tick["p"][1]),
                    float(tick["h"][1]),
                    float(tick["l"][1]),
                    float(tick["o"]),
                    int(tick["t"][1]),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
            row_id = cur.lastrowid
        finally:
            conn.close()
    return row_id


# ─── API layer ────────────────────────────────────────────────────────────

def fetch_ticker(pair: str = DEFAULT_PAIR) -> dict:
    """Fetch from Kraken API."""
    url = f"{KRAKEN_TICKER_URL}?pair={pair}"
    req = urllib.request.Request(url, headers={"User-Agent": "python-beginner-book/2.0"})

    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())

    if data.get("error"):
        raise RuntimeError(f"Kraken API error: {data['error']}")

    result = data["result"]
    key = next(iter(result))
    return result[key]


# ─── background fetcher ──────────────────────────────────────────────────

def background_fetcher(pair: str, interval: int) -> None:
    """Run in a thread: fetch tickers at regular intervals."""
    print(f"[Fetcher] Starting for {pair}, interval={interval}s")

    while True:
        try:
            tick = fetch_ticker(pair)
            row_id = insert_tick(pair, tick)
            print(f"[Fetcher] Row {row_id}: {pair} @ ${float(tick['c'][0]):.2f}")
        except Exception as e:
            print(f"[Fetcher] Error: {e}")

        time.sleep(interval)


# ─── Flask routes ────────────────────────────────────────────────────────

HTML_TEMPLATE = dedent("""\
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kraken Ticker Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            header p {
                font-size: 0.95em;
                opacity: 0.9;
            }
            .content {
                padding: 30px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 20px;
                border-radius: 8px;
            }
            .stat-card .label {
                font-size: 0.9em;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 8px;
            }
            .stat-card .value {
                font-size: 1.8em;
                font-weight: bold;
                color: #667eea;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th {
                background: #f8f9fa;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                color: #666;
                border-bottom: 2px solid #e9ecef;
            }
            td {
                padding: 12px;
                border-bottom: 1px solid #e9ecef;
            }
            tr:hover {
                background: #f8f9fa;
            }
            .price { font-weight: 600; color: #667eea; font-family: monospace; }
            .time { color: #999; font-size: 0.9em; }
            .refresh-info {
                text-align: center;
                margin-top: 20px;
                padding: 15px;
                background: #e7f3ff;
                border-radius: 8px;
                color: #0066cc;
                font-size: 0.95em;
            }
            .pair-selector {
                margin-bottom: 20px;
                display: flex;
                gap: 10px;
                align-items: center;
            }
            .pair-selector input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 1em;
            }
            .pair-selector button {
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 1em;
                font-weight: 600;
            }
            .pair-selector button:hover {
                background: #764ba2;
            }
            .no-data {
                text-align: center;
                padding: 40px;
                color: #999;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🚀 Kraken Ticker Dashboard</h1>
                <p id="pair-display">Pair: {{ pair }}</p>
            </header>

            <div class="content">
                <div class="pair-selector">
                    <input type="text" id="pairInput" placeholder="Enter pair (e.g., XXBTZUSD, XETHZUSD)"
                           value="{{ pair }}" />
                    <button onclick="changePair()">Change Pair</button>
                </div>

                <div id="stats" class="stats"></div>

                <h2 style="margin-top: 30px; margin-bottom: 15px;">Recent Snapshots</h2>
                <table id="ticker-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Last Price</th>
                            <th>Bid</th>
                            <th>Ask</th>
                            <th>Volume 24h</th>
                            <th>VWAP 24h</th>
                            <th>Fetched At</th>
                        </tr>
                    </thead>
                    <tbody id="table-body">
                        <tr class="no-data"><td colspan="7">Loading...</td></tr>
                    </tbody>
                </table>

                <div class="refresh-info">
                    🔄 This page auto-refreshes every 5 seconds
                </div>
            </div>
        </div>

        <script>
            let currentPair = "{{ pair }}";

            function changePair() {
                const newPair = document.getElementById('pairInput').value.trim().toUpperCase();
                if (newPair) {
                    currentPair = newPair;
                    window.location.search = '?pair=' + encodeURIComponent(newPair);
                }
            }

            async function fetchData() {
                try {
                    const response = await fetch('/api/ticker?pair=' + encodeURIComponent(currentPair));
                    const data = await response.json();

                    if (data.error) {
                        console.error('Error:', data.error);
                        return;
                    }

                    updateStats(data.stats);
                    updateTable(data.rows);
                } catch (error) {
                    console.error('Fetch error:', error);
                }
            }

            function updateStats(stats) {
                const statsDiv = document.getElementById('stats');
                if (!stats || Object.keys(stats).length === 0) {
                    statsDiv.innerHTML = '<div class="no-data">No data available</div>';
                    return;
                }

                statsDiv.innerHTML = `
                    <div class="stat-card">
                        <div class="label">Snapshots</div>
                        <div class="value">${stats.count}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Current Price</div>
                        <div class="value">$${parseFloat(stats.current).toFixed(2)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">24h High</div>
                        <div class="value">$${parseFloat(stats.high_24h).toFixed(2)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">24h Low</div>
                        <div class="value">$${parseFloat(stats.low_24h).toFixed(2)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Average</div>
                        <div class="value">$${parseFloat(stats.avg).toFixed(2)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Spread</div>
                        <div class="value">$${parseFloat(stats.spread).toFixed(2)}</div>
                    </div>
                `;
            }

            function updateTable(rows) {
                const tbody = document.getElementById('table-body');
                if (!rows || rows.length === 0) {
                    tbody.innerHTML = '<tr class="no-data"><td colspan="7">No data yet. Fetching...</td></tr>';
                    return;
                }

                tbody.innerHTML = rows.map(row => `
                    <tr>
                        <td>${row.id}</td>
                        <td class="price">$${parseFloat(row.last_price).toFixed(2)}</td>
                        <td class="price">$${parseFloat(row.bid_price).toFixed(2)}</td>
                        <td class="price">$${parseFloat(row.ask_price).toFixed(2)}</td>
                        <td>${parseFloat(row.volume_24h).toFixed(2)}</td>
                        <td class="price">$${parseFloat(row.vwap_24h).toFixed(2)}</td>
                        <td class="time">${row.fetched_at.split('T')[1].split('.')[0]}</td>
                    </tr>
                `).join('');
            }

            // Fetch immediately and then every 5 seconds
            fetchData();
            setInterval(fetchData, 5000);

            // Allow Enter key in input
            document.getElementById('pairInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') changePair();
            });
        </script>
    </body>
    </html>
""")


@app.route("/")
def index():
    """Render the main dashboard."""
    pair = DEFAULT_PAIR
    return render_template_string(HTML_TEMPLATE, pair=pair)


@app.route("/api/ticker")
def api_ticker():
    """API endpoint: return JSON with current data."""
    from flask import request
    
    pair = request.args.get("pair", DEFAULT_PAIR).upper()

    with db_lock:
        conn = get_db()
        try:
            rows = conn.execute(
                "SELECT id, last_price, bid_price, ask_price, volume_24h, vwap_24h, fetched_at "
                "FROM ticker WHERE pair = ? ORDER BY id DESC LIMIT 50",
                (pair,),
            ).fetchall()

            row_dicts = [dict(row) for row in rows]

            stats = conn.execute(
                "SELECT COUNT(*) as count, MAX(last_price) as max_price, "
                "MIN(last_price) as min_price, AVG(last_price) as avg_price, "
                "MAX(high_24h) as high_24h, MIN(low_24h) as low_24h "
                "FROM ticker WHERE pair = ?",
                (pair,),
            ).fetchone()

            if stats and stats["count"] > 0:
                stats_dict = {
                    "count": stats["count"],
                    "current": row_dicts[0]["last_price"] if row_dicts else 0,
                    "high_24h": stats["high_24h"],
                    "low_24h": stats["low_24h"],
                    "avg": stats["avg_price"],
                    "spread": stats["max_price"] - stats["min_price"],
                }
            else:
                stats_dict = {}

        finally:
            conn.close()

    return jsonify({
        "pair": pair,
        "rows": row_dicts[::-1],  # reverse to show newest at bottom
        "stats": stats_dict,
    })


# ─── CLI ──────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kraken Ticker Web UI with live dashboard"
    )
    parser.add_argument(
        "--pair", default=DEFAULT_PAIR,
        help=f"Kraken pair symbol (default: {DEFAULT_PAIR})"
    )
    parser.add_argument(
        "--interval", type=int, default=10,
        help="Seconds between API fetches (default: 10)"
    )
    parser.add_argument(
        "--port", type=int, default=5000,
        help="Flask port (default: 5000)"
    )
    parser.add_argument(
        "--host", default="127.0.0.1",
        help="Flask host (default: 127.0.0.1)"
    )

    args = parser.parse_args()
    pair = args.pair.upper()

    print()
    print("=" * 60)
    print("  Kraken Ticker Web Dashboard")
    print("=" * 60)
    print(f"  Pair       : {pair}")
    print(f"  Interval   : {args.interval}s")
    print(f"  Database   : {DB_FILE}")
    print(f"  Web URL    : http://{args.host}:{args.port}")
    print()
    print("  Tip: Open http://localhost:5000 in your browser")
    print("=" * 60)
    print()

    # Start background fetcher thread
    fetcher_thread = threading.Thread(
        target=background_fetcher,
        args=(pair, args.interval),
        daemon=True,
    )
    fetcher_thread.start()

    # Run Flask app
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    import sys
    raise SystemExit(main())
