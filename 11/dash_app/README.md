# Dash — Interactive Sales Dashboard

Dash turns Python into a full reactive web app — no JavaScript needed.
Every filter, dropdown, or slider automatically updates the charts via callbacks.

Run the app:

```bash
pip install dash plotly pandas numpy
python app.py   # → http://localhost:8050
```

---

## 1. App initialisation

```python
from dash import Dash, dcc, html, Input, Output, dash_table

app = Dash(__name__, title="Sales Dashboard")
```

`Dash(__name__)` creates the Flask server under the hood.
`dcc` (Dash Core Components) — interactive widgets.
`html` — HTML elements as Python objects.

---

## 2. Layout — building the UI in Python

The layout is a tree of `html.*` and `dcc.*` components, just like HTML but written in Python.

```python
app.layout = html.Div(
    style={"fontFamily": "Inter, sans-serif", "padding": "24px"},
    children=[

        html.H1("📊 Sales Dashboard"),

        # Dropdown
        dcc.Dropdown(
            id="filter-product",
            options=[{"label": p, "value": p} for p in ["Laptop", "Phone"]],
            value="Laptop",
        ),

        # Chart placeholder — filled by a callback
        dcc.Graph(id="chart-line"),

        # Data table
        dash_table.DataTable(id="data-table", page_size=10),
    ],
)
```

Every component has an **`id`** — callbacks use these IDs to read inputs and write outputs.

---

## 3. Checklist and RangeSlider

Useful for multi-select filters and numeric/date range selection.

```python
# Multi-select checklist
dcc.Checklist(
    id="filter-regions",
    options=[{"label": r, "value": r} for r in ["North", "South", "East", "West"]],
    value=["North", "South"],   # pre-selected values
    inline=True,
)

# Range slider (returns [min_index, max_index])
months = ["2024-01", "2024-02", "2024-03", "2024-04"]

dcc.RangeSlider(
    id="filter-months",
    min=0,
    max=len(months) - 1,
    value=[0, len(months) - 1],
    marks={i: m for i, m in enumerate(months)},
    allowCross=False,           # prevent handles from crossing
)
```

---

## 4. Callbacks — reactivity

A callback is a Python function that runs automatically whenever its `Input` values change.
`Output` defines which component property to update.

```python
from dash import Input, Output
import plotly.express as px

@app.callback(
    Output("chart-line", "figure"),   # component id, property to set
    Input("filter-product", "value"), # component id, property to read
)
def update_chart(selected_product):
    filtered = df[df["product"] == selected_product]
    return px.line(filtered, x="month", y="revenue", template="plotly_white")
```

**Multiple inputs and outputs** are just lists:

```python
@app.callback(
    Output("chart-bar",  "figure"),
    Output("kpi-cards",  "children"),
    Input("filter-products", "value"),
    Input("filter-regions",  "value"),
    Input("filter-months",   "value"),
)
def update_dashboard(products, regions, month_range):
    # all three inputs arrive as arguments in the same order
    filtered = df[df["product"].isin(products) & df["region"].isin(regions)]
    fig = px.bar(filtered, x="region", y="sales", template="plotly_white")
    kpis = [html.H2(f"${filtered['revenue'].sum():,.0f}")]
    return fig, kpis
```

---

## 5. KPI cards — dynamic HTML from a callback

Callbacks can return full component trees, not just figures.

```python
def kpi_card(label: str, value: str) -> html.Div:
    return html.Div(
        style={"backgroundColor": "white", "padding": "16px",
               "borderRadius": "8px", "textAlign": "center"},
        children=[
            html.P(label, style={"color": "#6c757d", "fontSize": "14px"}),
            html.H2(value),
        ],
    )

# In the callback — return a list of components
kpis = [
    kpi_card("Total Revenue", f"${df['revenue'].sum():,.0f}"),
    kpi_card("Total Units",   f"{df['units'].sum():,}"),
]
```

> **Important:** helper functions like `kpi_card()` and `_card()` must be defined
> **before** `app.layout`, otherwise Python raises `NameError` when the layout is built.

---

## 6. DataTable — sortable, paginated table

```python
from dash import dash_table

dash_table.DataTable(
    id="data-table",
    page_size=10,
    style_table={"overflowX": "auto"},
    style_header={
        "backgroundColor": "#343a40",
        "color": "white",
        "fontWeight": "bold",
    },
    style_data_conditional=[
        {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"},
    ],
)

# populate from callback
Output("data-table", "data"),
Output("data-table", "columns"),
# ...
table_data    = filtered_df.to_dict("records")
table_columns = [{"name": c, "id": c} for c in filtered_df.columns]
return table_data, table_columns
```

---

## 7. Running the app

```python
if __name__ == "__main__":
    app.run(debug=True, port=8050)
    # debug=True  → hot reload on file save + error messages in browser
    # debug=False → for production
```

---

## Key concepts

| Concept | What it does |
|---|---|
| `app.layout` | Defines the static structure of the page |
| `@app.callback` | Wires inputs to outputs — this is what makes the app reactive |
| `dcc.Graph` | Renders any Plotly figure, updated by callbacks |
| `dcc.Checklist` / `dcc.Dropdown` | User input widgets that feed into callbacks |
| `dcc.RangeSlider` | Numeric range selector, returns `[min, max]` indices |
| `dash_table.DataTable` | Interactive, pageable, sortable table |
| `html.*` | Python wrappers for every HTML tag (`html.Div`, `html.H1`, etc.) |
| `Output(id, prop)` | Callback writes to this component's property |
| `Input(id, prop)` | Callback reads from this component's property |

## Technologies Used

- **Dash** — reactive Python web framework (built on Flask + React)
- **Plotly** — interactive chart rendering inside `dcc.Graph`
- **pandas** — data filtering and aggregation inside callbacks
- **numpy** — synthetic dataset generation
