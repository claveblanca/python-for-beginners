"""
analysis/geo.py
Geocode place names extracted by NER and render them as an
interactive Leaflet map using folium.

Dependencies:
    pip install geopy folium
"""

import time
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Single geocoder instance — Nominatim requires a descriptive user_agent
_geocoder = Nominatim(user_agent='socmint-book/1.0')

# Simple in-process cache — avoids repeat network calls for the same place
_cache: dict[str, tuple[float, float] | None] = {}


def geocode(location_name: str) -> tuple[float, float] | None:
    """
    Return (latitude, longitude) for a place name string.

    Uses the Nominatim geocoder (OpenStreetMap data, free, no API key).
    Results are cached in memory; a 1-second sleep is inserted between
    uncached requests to respect Nominatim's rate limit.

    Args:
        location_name: Place name string, e.g. 'Kyiv' or 'Ukraine'.

    Returns:
        (lat, lon) tuple, or None if the place could not be geocoded.
    """
    if location_name in _cache:
        return _cache[location_name]
    try:
        loc    = _geocoder.geocode(location_name, timeout=5)
        result = (loc.latitude, loc.longitude) if loc else None
    except GeocoderTimedOut:
        result = None
    _cache[location_name] = result
    time.sleep(1)   # Nominatim rate limit: 1 request/second
    return result


def build_activity_map(
    posts_with_coords: list[dict],
    output_path: str = "socmint_map.html",
    center: tuple[float, float] = (48.5, 31.0),
    zoom_start: int = 6,
) -> folium.Map:
    """
    Render geolocated posts as an interactive Leaflet map.

    Each post becomes a CircleMarker whose radius scales with the post
    score and whose colour encodes the sentiment label. Clicking a
    marker opens a popup with the post title and score.

    Args:
        posts_with_coords: List of dicts, each containing:
                               title           str
                               lat             float
                               lon             float
                               score           int
                               sentiment_label 'positive'|'neutral'|'negative'
        output_path:       File path for the saved HTML map.
        center:            (lat, lon) for the initial map view.
        zoom_start:        Initial zoom level (1 = world, 18 = street).

    Returns:
        folium.Map object (also saved to output_path).
    """
    COLOURS = {
        "positive": "green",
        "negative": "red",
        "neutral":  "blue",
    }

    m = folium.Map(location=list(center), zoom_start=zoom_start)

    for p in posts_with_coords:
        colour = COLOURS.get(p.get('sentiment_label', 'neutral'), 'gray')
        radius = max(4, min(20, p['score'] / 500))   # scale score → 4–20 px
        folium.CircleMarker(
            location     = [p['lat'], p['lon']],
            radius       = radius,
            color        = colour,
            fill         = True,
            fill_opacity = 0.7,
            popup        = folium.Popup(
                f"<b>{p['title'][:80]}</b><br>"
                f"Score: {p['score']} | {p['sentiment_label']}",
                max_width=300,
            ),
        ).add_to(m)

    m.save(output_path)
    print(f"Map saved: {output_path}  ({len(posts_with_coords)} markers)")
    return m


if __name__ == "__main__":
    places = ['Kyiv', 'Kharkiv', 'Odesa', 'Lviv']
    print("--- Geocoding ---")
    for place in places:
        coords = geocode(place)
        if coords:
            print(f"  {place:<12s}: {coords[0]:.4f}, {coords[1]:.4f}")
