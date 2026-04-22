"""
Plotly — Chart Gallery (no server required)
Each chart opens in the browser as a standalone HTML file.

Run: python app.py
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ── Shared dataset ────────────────────────────────────────────────────────────

def make_sales_df() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    months = pd.date_range("2024-01", periods=12, freq="MS")
    products = ["Laptop", "Phone", "Tablet", "Monitor"]
    regions = ["North", "South", "East", "West"]

    rows = []
    for month in months:
        for product in products:
            for region in regions:
                rows.append({
                    "month": month,
                    "product": product,
                    "region": region,
                    "sales": int(rng.integers(200, 2000)),
                    "revenue": round(float(rng.uniform(5_000, 80_000)), 2),
                    "units": int(rng.integers(10, 200)),
                })
    return pd.DataFrame(rows)


df = make_sales_df()


# ── 1. Line chart — Revenue over time per product ─────────────────────────────

def chart_line() -> go.Figure:
    monthly = df.groupby(["month", "product"])["revenue"].sum().reset_index()
    fig = px.line(
        monthly,
        x="month",
        y="revenue",
        color="product",
        markers=True,
        title="Revenue Over Time by Product",
        labels={"revenue": "Revenue ($)", "month": "Month", "product": "Product"},
        template="plotly_white",
    )
    fig.update_layout(hovermode="x unified")
    return fig


# ── 2. Bar chart — Total sales by region ─────────────────────────────────────

def chart_bar() -> go.Figure:
    by_region = df.groupby("region")["sales"].sum().reset_index()
    fig = px.bar(
        by_region,
        x="region",
        y="sales",
        color="region",
        text_auto=True,
        title="Total Sales by Region",
        labels={"sales": "Units Sold", "region": "Region"},
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(textposition="outside")
    return fig


# ── 3. Pie / Donut — Revenue share by product ────────────────────────────────

def chart_pie() -> go.Figure:
    by_product = df.groupby("product")["revenue"].sum().reset_index()
    fig = px.pie(
        by_product,
        names="product",
        values="revenue",
        hole=0.45,
        title="Revenue Share by Product",
        template="plotly_white",
    )
    fig.update_traces(textinfo="percent+label")
    return fig


# ── 4. Scatter — Units vs Revenue (bubble = sales) ───────────────────────────

def chart_scatter() -> go.Figure:
    agg = (
        df.groupby("product")
        .agg(units=("units", "sum"), revenue=("revenue", "sum"), sales=("sales", "sum"))
        .reset_index()
    )
    fig = px.scatter(
        agg,
        x="units",
        y="revenue",
        size="sales",
        color="product",
        hover_name="product",
        title="Units vs Revenue (bubble size = sales)",
        labels={"units": "Total Units", "revenue": "Total Revenue ($)"},
        template="plotly_white",
        size_max=60,
    )
    return fig


# ── 5. Heatmap — Revenue: Product × Region ────────────────────────────────────

def chart_heatmap() -> go.Figure:
    pivot = df.pivot_table(
        index="product", columns="region", values="revenue", aggfunc="sum"
    )
    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="Viridis",
            text=pivot.values.round(0),
            texttemplate="$%{text:,.0f}",
            hovertemplate="Product: %{y}<br>Region: %{x}<br>Revenue: $%{z:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Revenue Heatmap — Product × Region",
        template="plotly_white",
    )
    return fig


# ── 6. Subplot dashboard — 4 charts in a 2x2 grid ────────────────────────────

def chart_dashboard() -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Revenue Over Time",
            "Sales by Region",
            "Revenue Share",
            "Units vs Revenue",
        ),
        specs=[
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "domain"}, {"type": "xy"}],
        ],
    )

    # Row 1, Col 1 — Line
    monthly = df.groupby(["month", "product"])["revenue"].sum().reset_index()
    for product, group in monthly.groupby("product"):
        fig.add_trace(
            go.Scatter(x=group["month"], y=group["revenue"], name=product, mode="lines+markers"),
            row=1, col=1,
        )

    # Row 1, Col 2 — Bar
    by_region = df.groupby("region")["sales"].sum().reset_index()
    fig.add_trace(
        go.Bar(x=by_region["region"], y=by_region["sales"], name="Sales", showlegend=False),
        row=1, col=2,
    )

    # Row 2, Col 1 — Pie
    by_product = df.groupby("product")["revenue"].sum().reset_index()
    fig.add_trace(
        go.Pie(labels=by_product["product"], values=by_product["revenue"],
               hole=0.4, showlegend=False),
        row=2, col=1,
    )

    # Row 2, Col 2 — Scatter
    agg = df.groupby("product").agg(
        units=("units", "sum"), revenue=("revenue", "sum")
    ).reset_index()
    fig.add_trace(
        go.Scatter(
            x=agg["units"], y=agg["revenue"],
            mode="markers+text",
            text=agg["product"],
            textposition="top center",
            marker=dict(size=14, color=list(range(len(agg))), colorscale="Plasma"),
            showlegend=False,
        ),
        row=2, col=2,
    )

    fig.update_layout(
        title_text="Sales Overview Dashboard",
        height=700,
        template="plotly_white",
    )
    return fig


# ── Main — render all charts ──────────────────────────────────────────────────

charts = {
    "01_line_revenue.html": chart_line(),
    "02_bar_sales.html": chart_bar(),
    "03_pie_revenue.html": chart_pie(),
    "04_scatter_units_revenue.html": chart_scatter(),
    "05_heatmap.html": chart_heatmap(),
    "06_dashboard_subplot.html": chart_dashboard(),
}

for filename, fig in charts.items():
    fig.write_html(filename, include_plotlyjs="cdn")
    print(f"Saved → {filename}")

print("\nOpen any .html file in your browser to explore the charts.")
