# Chapter 16 — Geospatial Intelligence WebGIS

A Streamlit + pydeck map dashboard built for a real GEOINT task:
> A gold mining company needs logistics intelligence for the Enga Region, Papua New Guinea — a conflict zone with tribal violence. Find and visualise mine locations, road networks, and conflict hotspots on a single interactive map.

**Run:**

```bash
streamlit run main.py   # → http://localhost:8501
```

---

## Data sources

| Layer | Source | How to get it |
|---|---|---|
| 🟡 Gold localities | [mindat.org](https://www.mindat.org/) via `openmindat` | `python retrieve_localities.py` |
| 🛣️ Roads by type | [OpenStreetMap](https://www.openstreetmap.org/) via Geofabrik PBF | `python extract_roads.py` |
| ☠️ Conflict events | [UCDP GED API](https://ucdp.uu.se/) | `python conflicts.py` |
| ⛏️ Mine sites | Local GeoJSON | `geojson/enga_mines.geojson` |

---

## Code snippets

### 1. Loading a GeoJSON file with GeoPandas

GeoPandas reads any GeoJSON (or Shapefile) into a GeoDataFrame — a DataFrame with a `geometry` column.

```python
import geopandas as gpd

roads_gdf = gpd.read_file("roads.geojson")

# add computed columns just like pandas
roads_gdf["color"] = roads_gdf["highway"].apply(
    lambda h: ROAD_COLORS.get(h, [120, 120, 120])
)
roads_gdf["road_name"] = roads_gdf["name"].fillna("Unnamed road")
```

---

### 2. Colouring roads by type — GeoJsonLayer

Convert the GeoDataFrame to a GeoJSON dict, inject per-feature properties, then pass to pydeck.
`get_line_color="properties.color"` tells the layer to read the colour from each feature's own properties.

```python
import pydeck as pdk

ROAD_COLORS = {
    "primary":    [255,  90,   0],   # orange
    "secondary":  [255, 210,   0],   # yellow
    "track":      [100, 200,  80],   # green
    "escape":     [255,  40,  40],   # red — evacuation routes
}

roads_geojson = roads_gdf.__geo_interface__          # GeoDataFrame → dict
for feat, color in zip(roads_geojson["features"], roads_gdf["color"]):
    feat["properties"]["color"] = color              # inject into each feature

roads_layer = pdk.Layer(
    "GeoJsonLayer",
    data=roads_geojson,
    pickable=True,
    get_line_color="properties.color",   # per-feature colour
    get_line_width=18,
    line_width_min_pixels=1,
)
```

---

### 3. Gold locality dots — ScatterplotLayer

Load mindat JSON, filter out country-level entries (lat/lon = 0), and render as gold circles.

```python
import json

with open("mindat_data/v1_localities.json", encoding="utf-8") as f:
    mindat = json.load(f)

gold_data = [
    {"lon": loc["longitude"], "lat": loc["latitude"]}
    for loc in mindat["results"]
    if loc.get("latitude") and loc.get("longitude")   # skip 0,0 entries
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
)
```

---

### 4. Custom icon markers — IconLayer

Embed a PNG icon as a base64 data URL so the map works fully offline.
`anchorY=128` pins the bottom of the icon to the coordinate (like a map pin).

```python
import base64

with open("icons/skull.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

SKULL_ICON = {
    "url": f"data:image/png;base64,{b64}",
    "width": 128,
    "height": 128,
    "anchorY": 128,    # anchor at bottom of image
}

conflicts_data = [
    {"lon": geom.x, "lat": geom.y, "icon": SKULL_ICON}
    for geom, row in zip(conflicts_gdf.geometry, conflicts_gdf.to_dict("records"))
    if geom is not None
]

conflicts_layer = pdk.Layer(
    "IconLayer",
    data=conflicts_data,
    get_icon="icon",
    get_position=["lon", "lat"],
    get_size=4,
    size_scale=10,
    size_min_pixels=20,
    pickable=True,
)
```

---

### 5. Per-layer tooltips via `tooltip_html`

Pydeck uses one shared tooltip template. Embed the full HTML in each feature so hovering a road shows road info, hovering a conflict shows conflict info — no bleed-through.

```python
# each feature carries its own pre-built HTML
for feat, rname, label in zip(...):
    feat["properties"]["tooltip_html"] = (
        f"<b>{rname}</b><br/>Type: {label}"
    )

conflicts_data = [
    {
        "lon": geom.x, "lat": geom.y, "icon": SKULL_ICON,
        "tooltip_html": (
            f"☠️ <b>{row['conflict_name']}</b><br/>"
            f"Deaths: {row['deaths_best']:,}<br/>"
            f"Date: {row['date_start'][:10]}"
        ),
    }
    ...
]

# single template — each layer injects its own content
tooltip = {"html": "{tooltip_html}"}
```

---

### 6. Composing the map

Stack all layers, set the camera, and render in Streamlit.
Layer order matters: **last layer = highest pick priority** on hover.

```python
view = pdk.ViewState(latitude=-6.3, longitude=144.5, zoom=6, pitch=0)

st.pydeck_chart(
    pdk.Deck(
        layers=[roads_layer, conflicts_layer, icon_layer, gold_layer],
        #        ↑ lowest pick priority              ↑ highest
        initial_view_state=view,
        map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
        tooltip={
            "html": "{tooltip_html}",
            "style": {"backgroundColor": "#1e1e2e", "color": "white",
                      "fontSize": "13px", "padding": "8px"},
        },
    )
)
```

---

### 7. Sidebar legend with colour swatches

Build an HTML colour swatch inline using `st.markdown` with `unsafe_allow_html=True`.

```python
with st.sidebar:
    st.header("Road types")
    for label, rgb in ROAD_COLORS.items():
        hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)
        st.markdown(
            f'<span style="display:inline-block;width:14px;height:14px;'
            f'background:{hex_color};border-radius:3px;margin-right:8px"></span>{label}',
            unsafe_allow_html=True,
        )

    st.divider()
    st.metric("Gold sites (Au)", len(gold_data))
    st.metric("Conflict events", len(conflicts_data))
```

---

## Technologies Used

- **Streamlit** — map dashboard UI
- **pydeck** — 3D geospatial visualisation (WebGL-based maps)
- **geopandas** — geospatial data manipulation and GeoJSON handling
- **pyrosm** — OpenStreetMap PBF file parsing for road extraction
- **openmindat** — client for the mindat.org mineral locality database
- **UCDP GED API** — Uppsala Conflict Data Program georeferenced event data
- **Geofabrik** — OpenStreetMap regional PBF data downloads
