#!/usr/bin/env python3
"""
Chapter 15 — Automated Trading App with Python
===============================================
kraken_backtest.py  — VWAP deviation backtest on stored ticker data

Reads the SQLite database written by kraken_ticker_web.py (ticker_data.db)
and replays the VWAP deviation signal over every stored snapshot, producing
a detailed report: signal counts, price extremes, and a per-row signal log.

Usage
-----
    # First collect some data:
    python kraken_ticker_web.py --interval 10

    # Then run the backtest against the stored database:
    python kraken_backtest.py
    python kraken_backtest.py --db ticker_data.db --pair XXBTZUSD --threshold 0.3
    python kraken_backtest.py --threshold 0.5 --log    # show per-row signal log
"""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

DEFAULT_DB        = "ticker_data.db"
DEFAULT_PAIR      = "XXBTZUSD"
DEFAULT_THRESHOLD = 0.3   # percent


# ── Database ──────────────────────────────────────────────────────────────────

def open_db(db_path: str) -> sqlite3.Connection:
    """Open the existing SQLite database in read-only mode."""
    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Database not found: {db_path}\n"
            "Run kraken_ticker_web.py first to collect data."
        )
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ── Backtest engine ───────────────────────────────────────────────────────────

def backtest_vwap_signal(conn: sqlite3.Connection, pair: str,
                         threshold_pct: float = DEFAULT_THRESHOLD) -> dict:
    """
    Replay the VWAP deviation signal over every stored snapshot for pair.

    Signal logic:
        deviation = (last_price - vwap_24h) / vwap_24h * 100

        deviation < -threshold_pct  →  BUY   (price below VWAP)
        deviation >  threshold_pct  →  SELL  (price above VWAP)
        otherwise                   →  HOLD

    Returns a result dict with counts, percentages, and the full row list.
    """
    rows = conn.execute(
        dedent("""\
            SELECT id, last_price, vwap_24h, ask_price, bid_price,
                   high_24h, low_24h, fetched_at
              FROM ticker
             WHERE pair = ?
             ORDER BY id"""),
        (pair,),
    ).fetchall()

    if not rows:
        return {
            "pair": pair, "threshold_pct": threshold_pct,
            "total": 0, "BUY": 0, "SELL": 0, "HOLD": 0,
            "pct_buy": 0.0, "pct_sell": 0.0, "pct_hold": 0.0,
            "signals": [],
        }

    counts  = {"BUY": 0, "SELL": 0, "HOLD": 0}
    signals = []

    for row in rows:
        last = row["last_price"]
        vwap = row["vwap_24h"]
        dev  = ((last - vwap) / vwap) * 100

        if   dev < -threshold_pct: sig = "BUY"
        elif dev >  threshold_pct: sig = "SELL"
        else:                      sig = "HOLD"

        counts[sig] += 1
        signals.append({
            "id":            row["id"],
            "signal":        sig,
            "last_price":    last,
            "vwap_24h":      vwap,
            "deviation_pct": round(dev, 4),
            "ask_price":     row["ask_price"],
            "bid_price":     row["bid_price"],
            "fetched_at":    row["fetched_at"],
        })

    n = len(rows)
    return {
        "pair":           pair,
        "threshold_pct":  threshold_pct,
        "total":          n,
        "BUY":            counts["BUY"],
        "SELL":           counts["SELL"],
        "HOLD":           counts["HOLD"],
        "pct_buy":        round(counts["BUY"]  / n * 100, 1),
        "pct_sell":       round(counts["SELL"] / n * 100, 1),
        "pct_hold":       round(counts["HOLD"] / n * 100, 1),
        "signals":        signals,
    }


def db_summary(conn: sqlite3.Connection, pair: str) -> dict:
    """Return price extremes and time range for the stored data."""
    row = conn.execute(
        dedent("""\
            SELECT COUNT(*) as n,
                   MIN(last_price) as lo, MAX(last_price) as hi,
                   AVG(last_price) as avg,
                   MIN(fetched_at) as first_ts, MAX(fetched_at) as last_ts
              FROM ticker WHERE pair = ?"""),
        (pair,),
    ).fetchone()
    return dict(row) if row else {}


# ── Display ───────────────────────────────────────────────────────────────────

_SIG_LABEL = {"BUY": "BUY ", "SELL": "SELL", "HOLD": "HOLD"}
_SIG_ARROW = {"BUY": "▼", "SELL": "▲", "HOLD": "─"}


def print_report(result: dict, summary: dict, show_log: bool) -> None:
    pair      = result["pair"]
    threshold = result["threshold_pct"]
    n         = result["total"]

    print()
    print("=" * 60)
    print(f"  VWAP Deviation Backtest  —  {pair}")
    print("=" * 60)

    if n == 0:
        print("  No data found for this pair. Collect data first.")
        print()
        return

    # ── data window ──
    print(f"\n  Data Window")
    print(f"    Snapshots : {n}")
    print(f"    First     : {summary.get('first_ts', 'n/a')}")
    print(f"    Last      : {summary.get('last_ts',  'n/a')}")
    print(f"    Low       : ${summary.get('lo',  0):>12,.2f}")
    print(f"    High      : ${summary.get('hi',  0):>12,.2f}")
    print(f"    Average   : ${summary.get('avg', 0):>12,.2f}")

    # ── signal counts ──
    print(f"\n  Signal Counts  (threshold ±{threshold}%)")
    print(f"    BUY  : {result['BUY']:>5}  ({result['pct_buy']:>5.1f}%)"
          f"  — last_price more than {threshold}% below VWAP")
    print(f"    SELL : {result['SELL']:>5}  ({result['pct_sell']:>5.1f}%)"
          f"  — last_price more than {threshold}% above VWAP")
    print(f"    HOLD : {result['HOLD']:>5}  ({result['pct_hold']:>5.1f}%)"
          f"  — within ±{threshold}% of VWAP")

    # ── signal quality note ──
    high_signal = result["pct_buy"] + result["pct_sell"]
    print()
    if high_signal > 40:
        print(f"  ⚠  {high_signal:.1f}% of snapshots triggered a directional signal.")
        print(f"     Threshold may be too tight — consider raising it.")
    elif high_signal < 5:
        print(f"  ⚠  Only {high_signal:.1f}% of snapshots triggered a signal.")
        print(f"     Threshold may be too wide — consider lowering it.")
    else:
        print(f"  ✓  {high_signal:.1f}% directional signal rate looks reasonable.")

    # ── per-row log ──
    if show_log and result["signals"]:
        print(f"\n  Per-Row Signal Log")
        print(f"    {'id':>5}  {'sig':4}  {'last':>12}  {'vwap':>12}  {'dev%':>8}  fetched_at")
        print(f"    {'--':>5}  {'---':4}  {'----':>12}  {'----':>12}  {'----':>8}  ----------")
        for s in result["signals"]:
            arr = _SIG_ARROW[s["signal"]]
            ts  = s["fetched_at"].split("T")[1][:8] if "T" in s["fetched_at"] else s["fetched_at"]
            print(
                f"    {s['id']:>5}  "
                f"{arr} {_SIG_LABEL[s['signal']]}  "
                f"${s['last_price']:>11,.2f}  "
                f"${s['vwap_24h']:>11,.2f}  "
                f"{s['deviation_pct']:>+8.4f}%  "
                f"{ts}"
            )

    print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Chapter 15 — VWAP deviation backtest on stored Kraken ticker data.",
    )
    p.add_argument(
        "--db", default=DEFAULT_DB, metavar="FILE",
        help=f"SQLite database file written by kraken_ticker_web.py (default: {DEFAULT_DB})",
    )
    p.add_argument(
        "--pair", default=DEFAULT_PAIR,
        help=f"Kraken pair to analyse (default: {DEFAULT_PAIR})",
    )
    p.add_argument(
        "--threshold", type=float, default=DEFAULT_THRESHOLD, metavar="PCT",
        help=f"VWAP deviation threshold in percent (default: {DEFAULT_THRESHOLD})",
    )
    p.add_argument(
        "--log", action="store_true",
        help="Print the full per-row signal log",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        conn = open_db(args.db)
    except FileNotFoundError as e:
        print(f"\n  [!] {e}\n")
        return 1

    pair = args.pair.upper()

    try:
        result  = backtest_vwap_signal(conn, pair, threshold_pct=args.threshold)
        summary = db_summary(conn, pair)
    finally:
        conn.close()

    print_report(result, summary, show_log=args.log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
