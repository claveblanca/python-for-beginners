#!/usr/bin/env python3
"""
Kraken Bitcoin Ticker → In-Memory SQLite Database
==================================================

A self-contained job that:
  1. Fetches the BTC/USD ticker from the Kraken public REST API
  2. Stores every snapshot in an in-memory SQLite database
  3. Queries the database to show stats

The Kraken Ticker endpoint is public — no API key required.
  https://docs.kraken.com/api/docs/rest-api/get-ticker-information

Uses only the standard library (urllib + sqlite3 + json).

Run:
    python kraken_ticker.py                    # fetch once
    python kraken_ticker.py --interval 10 --count 6   # fetch 6 times, 10s apart
    python kraken_ticker.py --pair XETHZUSD    # ETH/USD instead
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from textwrap import dedent

KRAKEN_TICKER_URL = "https://api.kraken.com/0/public/Ticker"
DEFAULT_PAIR = "XXBTZUSD"  # BTC/USD on Kraken


# ─── database layer ──────────────────────────────────────────────────────

def create_db() -> sqlite3.Connection:
    """Create an in-memory SQLite database with the ticker table."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA journal_mode=WAL")
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


def insert_tick(conn: sqlite3.Connection, pair: str, tick: dict) -> int:
    """Insert one parsed ticker row.  Returns the new row id."""
    cur = conn.execute(
        dedent("""\
            INSERT INTO ticker
                (pair, ask_price, bid_price, last_price, volume_24h,
                 vwap_24h, high_24h, low_24h, open_price, trades_24h, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """),
        (
            pair,
            float(tick["a"][0]),   # ask price
            float(tick["b"][0]),   # bid price
            float(tick["c"][0]),   # last trade price
            float(tick["v"][1]),   # volume (24 h)
            float(tick["p"][1]),   # VWAP   (24 h)
            float(tick["h"][1]),   # high   (24 h)
            float(tick["l"][1]),   # low    (24 h)
            float(tick["o"]),      # opening price
            int(tick["t"][1]),     # trades (24 h)
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    return cur.lastrowid


# ─── API layer ────────────────────────────────────────────────────────────

def fetch_ticker(pair: str = DEFAULT_PAIR) -> dict:
    """
    Call the Kraken public Ticker endpoint and return the raw result dict
    for the requested pair.

    Kraken response shape (simplified):
        { "error": [], "result": { "XXBTZUSD": { "a": [...], "b": [...], ... } } }

    Docs: https://docs.kraken.com/api/docs/rest-api/get-ticker-information
    """
    url = f"{KRAKEN_TICKER_URL}?pair={pair}"
    req = urllib.request.Request(url, headers={"User-Agent": "python-beginner-book/1.0"})

    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())

    if data.get("error"):
        raise RuntimeError(f"Kraken API error: {data['error']}")

    result = data["result"]
    key = next(iter(result))
    return result[key]


# ─── display helpers ──────────────────────────────────────────────────────

def print_tick_row(row_id: int, pair: str, tick: dict) -> None:
    """Pretty-print one fetched tick to the console."""
    now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    print(f"\n  [{row_id}] {pair}  @  {now}")
    print(f"    Last     : ${float(tick['c'][0]):>12,.2f}")
    print(f"    Ask      : ${float(tick['a'][0]):>12,.2f}")
    print(f"    Bid      : ${float(tick['b'][0]):>12,.2f}")
    print(f"    High 24h : ${float(tick['h'][1]):>12,.2f}")
    print(f"    Low  24h : ${float(tick['l'][1]):>12,.2f}")
    print(f"    VWAP 24h : ${float(tick['p'][1]):>12,.2f}")
    print(f"    Vol  24h : {float(tick['v'][1]):>12,.4f}")
    print(f"    Trades   : {int(tick['t'][1]):>12,}")


def print_db_summary(conn: sqlite3.Connection, pair: str) -> None:
    """Query the in-memory database and print aggregate stats."""
    row = conn.execute(
        dedent("""\
            SELECT COUNT(*),
                   MIN(last_price), MAX(last_price),
                   AVG(last_price),
                   MIN(fetched_at), MAX(fetched_at)
              FROM ticker
             WHERE pair = ?
        """),
        (pair,),
    ).fetchone()

    count, lo, hi, avg, first_ts, last_ts = row

    print("\n" + "=" * 55)
    print(f"  Database summary  ({pair})")
    print("=" * 55)
    print(f"    Snapshots stored : {count}")
    print(f"    Lowest  price    : ${lo:>12,.2f}")
    print(f"    Highest price    : ${hi:>12,.2f}")
    print(f"    Average price    : ${avg:>12,.2f}")
    print(f"    First fetch      : {first_ts}")
    print(f"    Last  fetch      : {last_ts}")

    if count > 1:
        spread = hi - lo
        pct = (spread / lo) * 100 if lo else 0
        print(f"    Spread (hi-lo)   : ${spread:>12,.2f}  ({pct:.4f}%)")

    print()
    print("  All rows:")
    print(f"    {'id':>4s}  {'last_price':>12s}  {'fetched_at'}")
    print(f"    {'--':>4s}  {'----------':>12s}  {'----------'}")
    for r in conn.execute(
        "SELECT id, last_price, fetched_at FROM ticker WHERE pair = ? ORDER BY id",
        (pair,),
    ):
        print(f"    {r[0]:>4d}  ${r[1]:>11,.2f}  {r[2]}")
    print()


# ─── CLI ──────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Fetch the Kraken BTC ticker and store it in an in-memory SQLite DB.",
    )
    p.add_argument(
        "--pair", default=DEFAULT_PAIR,
        help=f"Kraken pair symbol (default: {DEFAULT_PAIR}).  "
             "Examples: XXBTZUSD, XETHZUSD, XXBTZEUR",
    )
    p.add_argument(
        "--interval", type=int, default=0,
        help="Seconds between fetches (0 = fetch once and exit)",
    )
    p.add_argument(
        "--count", type=int, default=5,
        help="How many times to fetch when --interval > 0 (default: 5)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pair = args.pair.upper()

    print("Kraken Ticker Collector")
    print("=" * 55)
    print(f"  Pair     : {pair}")
    print(f"  Endpoint : {KRAKEN_TICKER_URL}?pair={pair}")
    print(f"  Database : sqlite3 :memory:")

    conn = create_db()

    iterations = args.count if args.interval > 0 else 1
    if args.interval > 0:
        print(f"  Schedule : every {args.interval}s × {iterations} fetches")

    for i in range(iterations):
        if i > 0:
            print(f"\n  Sleeping {args.interval}s ...")
            time.sleep(args.interval)

        try:
            tick = fetch_ticker(pair)
        except Exception as e:
            print(f"\n  [!] Fetch failed: {e}")
            continue

        row_id = insert_tick(conn, pair, tick)
        print_tick_row(row_id, pair, tick)

    print_db_summary(conn, pair)
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
