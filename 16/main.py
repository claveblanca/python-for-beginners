import base64
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
        "name": row.get("name", "Unknown"),
        "commodity": row.get("commodity", "Unknown"),
        "icon": MINE_ICON,
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
        "conflict_name":    row.get("conflict_name", "Unknown conflict"),
        "side_a":           row.get("side_a", "—"),
        "side_b":           row.get("side_b", "—"),
        "deaths_best":      int(row.get("deaths_best") or 0),
        "deaths_civilians": int(row.get("deaths_civilians") or 0),
        "violence_label":   row.get("violence_label")
                            or VIOLENCE_LABELS.get(row.get("type_of_violence"), "Unknown"),
        "date_start":       str(row.get("date_start", ""))[:10],
        "date_end":         str(row.get("date_end", ""))[:10],
        "adm_1":            row.get("adm_1", ""),
        "icon":             SKULL_ICON,
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
view = pdk.ViewState(latitude=-5.5, longitude=143.0, zoom=10, pitch=0)

st.pydeck_chart(
    pdk.Deck(
        layers=[roads_layer, icon_layer, conflicts_layer],
        initial_view_state=view,
        map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
        tooltip={
            "html": (
                # Roads
                "<b>{road_name}</b><br/>Type: {highway_label}<br/>"
                # Mines
                "<b>{name}</b><br/>Commodity: {commodity}<br/>"
                # Conflicts
                "☠️ <b>{conflict_name}</b><br/>"
                "Type: {violence_label}<br/>"
                "Side A: {side_a}<br/>"
                "Side B: {side_b}<br/>"
                "Deaths: {deaths_best} (civilians: {deaths_civilians})<br/>"
                "Date: {date_start} → {date_end}<br/>"
                "Location: {adm_1}"
            ),
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
    st.markdown("⛏️ &nbsp; Mining sites", unsafe_allow_html=True)
    st.markdown("☠️ &nbsp; Conflict events", unsafe_allow_html=True)

    st.divider()
    st.header("Conflicts summary")
    total_events  = len(conflicts_data)
    total_deaths  = sum(c["deaths_best"] for c in conflicts_data)
    total_civs    = sum(c["deaths_civilians"] for c in conflicts_data)
    st.metric("Total events",   total_events)
    st.metric("Total deaths",   f"{total_deaths:,}")
    st.metric("Civilian deaths", f"{total_civs:,}")