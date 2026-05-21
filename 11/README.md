# Chapter 11 — Data Visualization: Streamlit, Plotly & Dash

All three projects visualize the **same synthetic sales dataset** (products × regions × months) so you can compare how each tool handles identical requirements.

---

## Project structure

```
11/
├── streamlit_app/    # Streamlit + Plotly — data app with sidebar filters
├── plotly_charts/    # Pure Plotly — generates standalone HTML chart files
└── dash_app/         # Dash + Plotly — full SPA with callbacks & data table
```

---

## Streamlit (`streamlit_app/`)

Streamlit turns a Python script into an interactive web app with no front-end code.

### Run
```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py      # → http://localhost:8501
```

### What's included
- Sidebar multiselect filters (products, regions) and a date range picker
- 4 KPI metric cards (auto-updating)
- Line chart — revenue over time
- Donut chart — revenue share by product
- Bar chart — sales by region
- Heatmap — revenue: product × region
- Raw data expander

---

## Plotly (`plotly_charts/`)

Pure Plotly with no server. Each chart is saved as a self-contained `.html` file you open in any browser.

### Run
```bash
cd plotly_charts
pip install -r requirements.txt
python app.py
```

### Charts generated
| File | Chart type |
|------|-----------|
| `01_line_revenue.html` | Line — revenue over time |
| `02_bar_sales.html` | Bar — sales by region |
| `03_pie_revenue.html` | Donut — revenue by product |
| `04_scatter_units_revenue.html` | Bubble scatter |
| `05_heatmap.html` | Heatmap — product × region |
| `06_dashboard_subplot.html` | 2×2 subplot dashboard |

---

## Dash (`dash_app/`)

Dash is a full reactive web framework. Filters are wired to all charts via **callbacks** — every interaction re-computes the figures server-side.

### Run
```bash
cd dash_app
pip install -r requirements.txt
python app.py             # → http://localhost:8050
```

### What's included
- Checklist filters (products, regions)
- Range slider for month selection
- 4 KPI cards
- Line, pie, bar, and heatmap charts — all reactive
- Paginated data table (DataTable component)

---

## Framework comparison

| | Streamlit | Plotly (standalone) | Dash |
|---|---|---|---|
| **Server needed** | Yes (built-in) | No | Yes (Flask/ASGI) |
| **Reactivity** | Re-runs full script | None (static HTML) | Callbacks (fine-grained) |
| **UI components** | Widgets built-in | Charts only | Full HTML + components |
| **Routing / multi-page** | Pages folder | N/A | `dcc.Location` / pages |
| **Learning curve** | Very low | Low | Medium |
| **Best for** | Quick data apps, notebooks | Generating reports | Production dashboards |
| **Customization** | Limited | Full chart API | Full HTML/CSS/JS |

---

## Key code patterns

### Reactivity

```python
# Streamlit — whole script re-runs on every widget interaction
selected = st.multiselect("Products", options=products)
filtered = df[df["product"].isin(selected)]
fig = px.line(filtered, ...)
st.plotly_chart(fig)

# Dash — only the callback body re-runs
@app.callback(Output("chart", "figure"), Input("dropdown", "value"))
def update(selected):
    filtered = df[df["product"].isin(selected)]
    return px.line(filtered, ...)
```

### Layout

```python
# Streamlit — imperative, top-to-bottom
col1, col2 = st.columns(2)
col1.plotly_chart(fig_line)
col2.plotly_chart(fig_pie)

# Dash — declarative HTML tree
html.Div([
    dcc.Graph(id="line", figure=fig_line),
    dcc.Graph(id="pie",  figure=fig_pie),
], style={"display": "grid", "gridTemplateColumns": "1fr 1fr"})
```

### Plotly subplots

```python
from plotly.subplots import make_subplots
fig = make_subplots(rows=2, cols=2)
fig.add_trace(go.Scatter(...), row=1, col=1)
fig.add_trace(go.Bar(...),     row=1, col=2)
fig.show()          # opens browser
fig.write_html("out.html")   # saves file
```

## Technologies Used

- **Streamlit** — interactive data app framework (zero-boilerplate web UI)
- **Plotly** — interactive charts (Express + Graph Objects)
- **Dash** — reactive single-page dashboards built on Plotly
- **pandas** — data manipulation and analysis
- **numpy** — numerical computing
