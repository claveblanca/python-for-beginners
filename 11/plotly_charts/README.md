# Plotly Charts

Plotly produces interactive charts that run in the browser — hover, zoom, pan, and export are built in with no extra code.

Run `app.py` to generate all charts as standalone HTML files:

```bash
python app.py
# opens 01_line_revenue.html, 02_bar_sales.html … in the current folder
```

---

## 1. Line chart — `px.line`

Best for trends over time. `color="product"` automatically splits one line per product.

```python
import plotly.express as px

fig = px.line(
    monthly_df,
    x="month",
    y="revenue",
    color="product",      # one line per category
    markers=True,         # show dots at each data point
    title="Revenue Over Time by Product",
    labels={"revenue": "Revenue ($)", "month": "Month"},
    template="plotly_white",
)
fig.update_layout(hovermode="x unified")  # show all series values at once on hover
fig.show()
```

---

## 2. Bar chart — `px.bar`

Best for comparing totals across categories. `text_auto=True` labels each bar automatically.

```python
fig = px.bar(
    by_region_df,
    x="region",
    y="sales",
    color="region",
    text_auto=True,                                   # add value labels on bars
    color_discrete_sequence=px.colors.qualitative.Set2,
    template="plotly_white",
)
fig.update_traces(textposition="outside")  # labels above the bars
fig.show()
```

---

## 3. Pie / Donut chart — `px.pie`

Best for showing proportions. `hole=0.45` turns it into a donut.

```python
fig = px.pie(
    by_product_df,
    names="product",
    values="revenue",
    hole=0.45,            # 0 = full pie, >0 = donut
    template="plotly_white",
)
fig.update_traces(textinfo="percent+label")  # show both % and name on slices
fig.show()
```

---

## 4. Scatter / Bubble chart — `px.scatter`

Best for showing relationships between two numeric variables. Add `size=` for a third dimension.

```python
fig = px.scatter(
    agg_df,
    x="units",
    y="revenue",
    size="sales",         # bubble size encodes a third variable
    color="product",
    hover_name="product", # bold label in the tooltip
    size_max=60,
    template="plotly_white",
)
fig.show()
```

---

## 5. Heatmap — `go.Heatmap`

Best for a matrix of values (rows × columns). Uses `graph_objects` directly for full control.

```python
import plotly.graph_objects as go

fig = go.Figure(
    go.Heatmap(
        z=pivot.values,                  # 2-D array of values
        x=pivot.columns.tolist(),        # column labels (x-axis)
        y=pivot.index.tolist(),          # row labels (y-axis)
        colorscale="Viridis",
        text=pivot.values.round(0),
        texttemplate="$%{text:,.0f}",   # format shown inside each cell
        hovertemplate=(
            "Product: %{y}<br>"
            "Region: %{x}<br>"
            "Revenue: $%{z:,.0f}<extra></extra>"
        ),
    )
)
fig.update_layout(title="Revenue Heatmap — Product × Region", template="plotly_white")
fig.show()
```

---

## 6. Subplots — `make_subplots`

Combine multiple chart types in a grid. Use `specs` to mix `"xy"` (cartesian) and `"domain"` (pie) cells.

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Revenue Over Time", "Sales by Region",
                    "Revenue Share",     "Units vs Revenue"),
    specs=[
        [{"type": "xy"},     {"type": "xy"}],
        [{"type": "domain"}, {"type": "xy"}],  # "domain" required for Pie
    ],
)

fig.add_trace(go.Scatter(x=..., y=..., name="Laptop"), row=1, col=1)
fig.add_trace(go.Bar(x=...,     y=...),                row=1, col=2)
fig.add_trace(go.Pie(labels=..., values=..., hole=0.4), row=2, col=1)
fig.add_trace(go.Scatter(x=..., y=..., mode="markers"), row=2, col=2)

fig.update_layout(height=700, template="plotly_white", title_text="Dashboard")
fig.show()
```

---

## Saving to HTML

Any Plotly figure can be saved as a standalone HTML file — no server needed.

```python
fig.write_html("chart.html", include_plotlyjs="cdn")
# include_plotlyjs="cdn"    → small file, requires internet to open
# include_plotlyjs=True     → self-contained (~3 MB), works offline
```

---

## Key concepts

| Concept | What it does |
|---|---|
| `px.*` (Plotly Express) | One-liner charts from a DataFrame — quickest way to get started |
| `go.*` (Graph Objects) | Low-level building blocks — full control over every trace |
| `template=` | Built-in themes: `"plotly_white"`, `"plotly_dark"`, `"ggplot2"`, `"seaborn"` |
| `fig.update_layout()` | Change title, margins, fonts, legend, hover mode, etc. |
| `fig.update_traces()` | Modify properties of plotted data (colours, labels, line style) |
| `fig.show()` | Open in browser (or inline in Jupyter) |
| `fig.write_html()` | Save as a shareable HTML file |

## Technologies Used

- **Plotly Express** (`plotly.express`) — high-level chart API
- **Plotly Graph Objects** (`plotly.graph_objects`) — low-level trace API
- **pandas** — data aggregation and pivot tables
- **numpy** — synthetic data generation
