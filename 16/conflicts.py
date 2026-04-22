"""
UCDP GED Event Browser
-----------------------
Fetches georeferenced conflict events from the UCDP GED API and prints
a summary table. Supports filtering by country (ISO2 or GW code),
date range, and type of violence. Optionally exports results as GeoJSON.

API docs : https://ucdp.uu.se/apidocs/
GW codes : gw_codes.json

Usage:
    export UCDP_TOKEN="your-token-here"

    python conflicts.py
    python conflicts.py --countries PG
    python conflicts.py --countries PG ID --start 2010-01-01 --end 2020-12-31
    python conflicts.py --countries SD ET --violence 1 2
    python conflicts.py --countries PG --geojson png_conflicts.geojson
    python conflicts.py --pagesize 200 --page 1
"""

import json
import os
import sys
import argparse
import requests
from pathlib import Path

# ── Token ──────────────────────────────────────────────────────────────────────

TOKEN = os.environ.get("UCDP_TOKEN", "").strip()
if not TOKEN:
    print("[ERROR] UCDP_TOKEN environment variable is not set.")
    sys.exit(1)

# ── GW code lookup ─────────────────────────────────────────────────────────────

GW_CODES_PATH = Path(__file__).parent / "gw_codes.json"

def load_gw_codes() -> dict[str, int]:
    if not GW_CODES_PATH.exists():
        return {}
    with GW_CODES_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)

def resolve_country_filter(values: list[str], iso2_to_gw: dict[str, int]) -> str:
    """
    Accept a mix of ISO2 codes (e.g. 'PG') and raw GW integers (e.g. '910').
    Returns a comma-separated GW code string ready for the API Country param.
    """
    gw_ids: list[str] = []
    unknown: list[str] = []

    for v in values:
        upper = v.upper()
        if upper in iso2_to_gw:
            gw_ids.append(str(iso2_to_gw[upper]))
        elif v.isdigit():
            gw_ids.append(v)
        else:
            unknown.append(v)

    if unknown:
        print(f"[ERROR] Unrecognised country code(s): {', '.join(unknown)}")
        print("        Use ISO2 codes (e.g. PG, SD) or raw GW integers.")
        sys.exit(1)

    return ",".join(gw_ids)

# ── Violence type labels ───────────────────────────────────────────────────────

VIOLENCE_LABELS = {
    1: "State-based",
    2: "Non-state",
    3: "One-sided",
}

# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Browse UCDP GED conflict events with optional filters.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python conflicts.py\n"
            "  python conflicts.py --countries PG\n"
            "  python conflicts.py --countries PG ID --start 2010-01-01\n"
            "  python conflicts.py --countries SD ET --end 2020-12-31\n"
            "  python conflicts.py --violence 2            # non-state only\n"
            "  python conflicts.py --countries NG --violence 1 3 --pagesize 200\n"
        ),
    )
    parser.add_argument(
        "--countries", "-c",
        nargs="+", metavar="ISO2_OR_GW",
        help="Filter by ISO2 country code(s) or GW integer(s) (e.g. PG SD 910).",
    )
    parser.add_argument(
        "--start", "-s",
        metavar="YYYY-MM-DD",
        help="Only include events with date_end >= this date.",
    )
    parser.add_argument(
        "--end", "-e",
        metavar="YYYY-MM-DD",
        help="Only include events with date_end <= this date.",
    )
    parser.add_argument(
        "--violence", "-v",
        nargs="+", type=int, choices=[1, 2, 3], metavar="TYPE",
        help="Filter by type of violence: 1=state-based 2=non-state 3=one-sided.",
    )
    parser.add_argument(
        "--pagesize", "-ps",
        type=int, default=100, metavar="N",
        help="Number of results per page (default: 100).",
    )
    parser.add_argument(
        "--page", "-p",
        type=int, default=1, metavar="N",
        help="Page number to fetch (default: 1).",
    )
    parser.add_argument(
        "--geojson", "-g",
        metavar="FILE",
        help="Export results as a GeoJSON FeatureCollection to this file.",
    )
    return parser.parse_args()

# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    iso2_to_gw = load_gw_codes()

    params: dict = {
        "pagesize": args.pagesize,
        "page":     args.page,
    }

    if args.countries:
        gw_filter = resolve_country_filter(args.countries, iso2_to_gw)
        params["Country"] = gw_filter
        print(f"Country filter : {', '.join(args.countries)}  (GW: {gw_filter})")

    if args.start:
        params["StartDate"] = args.start
        print(f"Start date     : {args.start}")

    if args.end:
        params["EndDate"] = args.end
        print(f"End date       : {args.end}")

    if args.violence:
        params["TypeOfViolence"] = ",".join(str(v) for v in args.violence)
        labels = ", ".join(VIOLENCE_LABELS[v] for v in args.violence)
        print(f"Violence type  : {labels}")

    print()

    headers = {"x-ucdp-access-token": TOKEN}
    url     = "https://ucdpapi.pcr.uu.se/api/gedevents/25.1"

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    total   = data.get("TotalCount", "?")
    pages   = data.get("TotalPages", "?")
    results = data.get("Result", [])

    print(f"Total events : {total}  |  Page {args.page}/{pages}  |  Showing {len(results)}")
    print()

    # ── header ────────────────────────────────────────────────────────────────
    col = "{:<8} {:<28} {:<12} {:<9} {:<9} {:<12} {:<12} {:>7} {:>7} {:>7} {:>7} {:>7} {:>7}"
    print(col.format(
        "ID", "Country", "Type", "Lat", "Lon",
        "Start", "End",
        "Best", "Low", "High",
        "Side A", "Side B", "Civilian",
    ))
    print("─" * 128)

    # ── totals ────────────────────────────────────────────────────────────────
    sum_best = sum_low = sum_high = 0
    sum_a    = sum_b   = sum_civ  = 0

    for ev in results:
        vtype = VIOLENCE_LABELS.get(ev.get("type_of_violence"), "?")

        best = ev.get("best")      or 0
        low  = ev.get("low")       or 0
        high = ev.get("high")      or 0
        d_a  = ev.get("deaths_a")  or 0
        d_b  = ev.get("deaths_b")  or 0
        d_civ= ev.get("deaths_civilians") or 0

        sum_best += best;  sum_low += low;  sum_high += high
        sum_a    += d_a;   sum_b   += d_b;  sum_civ  += d_civ

        print(col.format(
            ev.get("id", ""),
            str(ev.get("country", ""))[:28],
            vtype,
            f"{ev['latitude']:.4f}"  if ev.get("latitude")  is not None else "",
            f"{ev['longitude']:.4f}" if ev.get("longitude") is not None else "",
            str(ev.get("date_start", ""))[:12],
            str(ev.get("date_end",   ""))[:12],
            best, low, high, d_a, d_b, d_civ,
        ))

    # ── page totals ───────────────────────────────────────────────────────────
    print("─" * 128)
    print(col.format(
        "TOTAL", f"({len(results)} events)", "", "", "", "", "",
        sum_best, sum_low, sum_high, sum_a, sum_b, sum_civ,
    ))

    if args.geojson:
        export_geojson(results, args.geojson)


def export_geojson(events: list[dict], path: str) -> None:
    """Write events as a GeoJSON FeatureCollection."""
    features = []
    for ev in events:
        lat = ev.get("latitude")
        lon = ev.get("longitude")
        if lat is None or lon is None:
            continue

        properties = {
            "id":               ev.get("id"),
            "conflict_name":    ev.get("conflict_name"),
            "country":          ev.get("country"),
            "country_id":       ev.get("country_id"),
            "region":           ev.get("region"),
            "type_of_violence": ev.get("type_of_violence"),
            "violence_label":   VIOLENCE_LABELS.get(ev.get("type_of_violence"), "?"),
            "date_start":       ev.get("date_start"),
            "date_end":         ev.get("date_end"),
            "deaths_best":      ev.get("best"),
            "deaths_low":       ev.get("low"),
            "deaths_high":      ev.get("high"),
            "deaths_a":         ev.get("deaths_a"),
            "deaths_b":         ev.get("deaths_b"),
            "deaths_civilians": ev.get("deaths_civilians"),
            "deaths_unknown":   ev.get("deaths_unknown"),
            "side_a":           ev.get("side_a"),
            "side_b":           ev.get("side_b"),
            "adm_1":            ev.get("adm_1"),
            "adm_2":            ev.get("adm_2"),
            "where_description":ev.get("where_description"),
            "source_article":   ev.get("source_article"),
        }

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": properties,
        })

    collection = {"type": "FeatureCollection", "features": features}

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(collection, fh, ensure_ascii=False, indent=2)

    print(f"\nGeoJSON saved to: {path}  ({len(features)} features)")


if __name__ == "__main__":
    main()
