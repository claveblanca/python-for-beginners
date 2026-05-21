import base64
import json
import streamlit as st
import pydeck as pdk
import geopandas as gpd

st.set_page_config(page_title="Enga Mines WebGIS", layout="wide")
st.title("⛏️ Enga Mines WebGIS")

# ── Road color palette ────────────────────────────────────────────────────────
ROAD_COLORS = {
    "primary":       [255,  90,   0],   # vivid orange
    "secondary":     [255, 210,   0],   # yellow
    "tertiary":      [ 60, 180, 255],   # sky blue
    "tertiary_link": [ 60, 180, 255],
    "residential":   [210, 210, 210],   # light grey
    "unclassified":  [150, 150, 150],   # mid grey
    "service":       [ 90,  90,  90],   # dark grey
    "living_street": [180,  80, 255],   # purple
    "road":          [170, 170, 170],
    "escape":        [255,  40,  40],   # red
    "track":         [100, 200,  80],   # green
    "busway":        [  0, 210, 180],   # teal
}
DEFAULT_COLOR = [120, 120, 120]

# ── Load & prepare roads ──────────────────────────────────────────────────────
roads_gdf = gpd.read_file("roads.geojson")
roads_gdf["color"] = roads_gdf["highway"].apply(lambda h: ROAD_COLORS.get(h, DEFAULT_COLOR))
roads_gdf["highway_label"] = roads_gdf["highway"].fillna("unknown")
roads_gdf["road_name"] = roads_gdf["name"].fillna("Unnamed road")

roads_geojson = roads_gdf.__geo_interface__
for feat, color, label, rname in zip(
    roads_geojson["features"],
    roads_gdf["color"],
    roads_gdf["highway_label"],
    roads_gdf["road_name"],
):
    feat["properties"]["color"] = color
    feat["properties"]["highway_label"] = label
    feat["properties"]["road_name"] = rname
    feat["properties"]["tooltip_html"] = (
        f"<b>{rname}</b><br/>Type: {label}"
    )

roads_layer = pdk.Layer(
    "GeoJsonLayer",
    data=roads_geojson,
    pickable=True,
    stroked=True,
    filled=False,
    get_line_color="properties.color",
    get_line_width=18,
    line_width_min_pixels=1,
)

# ── Load & prepare mines ──────────────────────────────────────────────────────
mines_gdf = gpd.read_file("geojson/enga_mines.geojson")

with open("icons/image.png", "rb") as _f:
    _b64 = base64.b64encode(_f.read()).decode()
MINE_ICON = {
    "url": f"data:image/png;base64,{_b64}",
    "width": 128,
    "height": 128,
    "anchorY": 128,
}

mines_data = [
    {
        "lon": geom.x,
        "lat": geom.y,
        "icon": MINE_ICON,
        "tooltip_html": (
            f"⛏️ <b>{row.get('name', 'Unknown')}</b><br/>"
            f"Commodity: {row.get('commodity', 'Unknown')}"
        ),
    }
    for geom, row in zip(
        mines_gdf.geometry,
        mines_gdf.drop(columns="geometry").to_dict("records"),
    )
]

icon_layer = pdk.Layer(
    "IconLayer",
    data=mines_data,
    get_icon="icon",
    get_position=["lon", "lat"],
    get_size=5,
    size_scale=10,
    size_min_pixels=24,
    pickable=True,
)

# ── Load & prepare gold localities (mindat) ───────────────────────────────────
with open("mindat_data/v1_localities.json", encoding="utf-8") as _f:
    _mindat = json.load(_f)

gold_data = [
    {
        "lon": loc["longitude"],
        "lat": loc["latitude"],
        "tooltip_html": (
            f"🟡 <b>{loc.get('txt', 'Unknown')}</b><br/>"
            f"Elements: {loc.get('elements', '').strip('-').replace('-', ', ')}<br/>"
            + (f"{loc['description_short'].strip()[:200]}" if loc.get("description_short") else "")
        ),
    }
    for loc in _mindat.get("results", [])
    if loc.get("latitude") and loc.get("longitude")  # skip 0,0 country-level entries
]

gold_layer = pdk.Layer(
    "ScatterplotLayer",
    data=gold_data,
    get_position=["lon", "lat"],
    get_fill_color=[255, 215, 0, 220],   # gold, slightly transparent
    get_radius=4000,
    radius_min_pixels=5,
    radius_max_pixels=18,
    pickable=True,
    stroked=True,
    get_line_color=[180, 140, 0, 255],   # darker gold outline
    line_width_min_pixels=1,
)

# ── Load & prepare conflicts ──────────────────────────────────────────────────
conflicts_gdf = gpd.read_file("png_conflicts.geojson")

# Skull icon — loaded from icons/skull.png (same pattern as mine icon)
with open("icons/skull.png", "rb") as _sf:
    _skull_b64 = base64.b64encode(_sf.read()).decode()
SKULL_ICON = {
    "url": f"data:image/png;base64,{_skull_b64}",
    "width": 128,
    "height": 128,
    "anchorY": 128,
}

VIOLENCE_LABELS = {1: "State-based", 2: "Non-state", 3: "One-sided"}

conflicts_data = [
    {
        "lon": geom.x,
        "lat": geom.y,
        "deaths_best":      int(row.get("deaths_best") or 0),
        "deaths_civilians": int(row.get("deaths_civilians") or 0),
        "icon":             SKULL_ICON,
        "tooltip_html": (
            f"☠️ <b>{row.get('conflict_name', 'Unknown conflict')}</b><br/>"
            f"Type: {row.get('violence_label') or VIOLENCE_LABELS.get(row.get('type_of_violence'), 'Unknown')}<br/>"
            f"Side A: {row.get('side_a', '—')}<br/>"
            f"Side B: {row.get('side_b', '—')}<br/>"
            f"Deaths: {int(row.get('deaths_best') or 0):,} "
            f"(civilians: {int(row.get('deaths_civilians') or 0):,})<br/>"
            f"Date: {str(row.get('date_start', ''))[:10]} → {str(row.get('date_end', ''))[:10]}<br/>"
            f"Location: {row.get('adm_1', '')}"
        ),
    }
    for geom, row in zip(
        conflicts_gdf.geometry,
        conflicts_gdf.drop(columns="geometry").to_dict("records"),
    )
    if geom is not None
]

conflicts_layer = pdk.Layer(
    "IconLayer",
    data=conflicts_data,
    get_icon="icon",
    get_position=["lon", "lat"],
    get_color=[255, 0, 0, 255],
    get_size=4,
    size_scale=10,
    size_min_pixels=20,
    pickable=True,
)

# ── Map ───────────────────────────────────────────────────────────────────────
view = pdk.ViewState(latitude=-6.3, longitude=144.5, zoom=6, pitch=0)

st.pydeck_chart(
    pdk.Deck(
        layers=[roads_layer, conflicts_layer, icon_layer, gold_layer],
        initial_view_state=view,
        map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
        tooltip={
            "html": "{tooltip_html}",
            "style": {
                "backgroundColor": "#1e1e2e",
                "color": "white",
                "fontSize": "13px",
                "padding": "8px",
                "borderRadius": "6px",
            },
        },
    )
)

# ── Legend ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Road types")
    for label, rgb in ROAD_COLORS.items():
        hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)
        st.markdown(
            f'<span style="display:inline-block;width:14px;height:14px;'
            f'background:{hex_color};border-radius:3px;margin-right:8px;'
            f'vertical-align:middle"></span>{label}',
            unsafe_allow_html=True,
        )

    st.divider()
    st.header("Layers")
    st.markdown("🟡 &nbsp; Gold localities (mindat)", unsafe_allow_html=True)
    st.markdown("⛏️ &nbsp; Mining sites", unsafe_allow_html=True)
    st.markdown("☠️ &nbsp; Conflict events", unsafe_allow_html=True)

    st.divider()
    st.header("Gold localities")
    st.metric("Mindat sites (Au)", len(gold_data))

    st.divider()
    st.header("Conflicts summary")
    total_events = len(conflicts_data)
    total_deaths = sum(c["deaths_best"] for c in conflicts_data)
    total_civs   = sum(c["deaths_civilians"] for c in conflicts_data)
    st.metric("Total events",   total_events)
    st.metric("Total deaths",   f"{total_deaths:,}")
    st.metric("Civilian deaths", f"{total_civs:,}")