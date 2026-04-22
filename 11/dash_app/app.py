"""
Dash — Interactive Sales Dashboard
Run: python app.py  →  http://localhost:8050
"""

from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Dataset ───────────────────────────────────────────────────────────────────

def make_sales_df() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    months = pd.date_range("2024-01", periods=12, freq="MS")
    products = ["Laptop", "Phone", "Tablet", "Monitor"]
    regions  = ["North", "South", "East", "West"]

    rows = []
    for month in months:
        for product in products:
            for region in regions:
                rows.append({
                    "month":   month.strftime("%Y-%m"),
                    "product": product,
                    "region":  region,
                    "sales":   int(rng.integers(200, 2000)),
                    "revenue": round(float(rng.uniform(5_000, 80_000)), 2),
                    "units":   int(rng.integers(10, 200)),
                })
    return pd.DataFrame(rows)


df = make_sales_df()
ALL_PRODUCTS = df["product"].unique().tolist()
ALL_REGIONS  = df["region"].unique().tolist()
ALL_MONTHS   = sorted(df["month"].unique().tolist())

# ── App & layout ──────────────────────────────────────────────────────────────

app = Dash(__name__, title="Sales Dashboard")

app.layout = html.Div(
    style={"fontFamily": "Inter, sans-serif", "backgroundColor": "#f8f9fa", "padding": "24px"},
    children=[

        html.H1("📊 Sales Dashboard", style={"marginBottom": "4px"}),
        html.P("Interactive dashboard built with Dash + Plotly",
               style={"color": "#6c757d", "marginTop": 0}),

        # ── Filters row ───────────────────────────────────────────────────────
        html.Div(
            style={"display": "flex", "gap": "24px", "flexWrap": "wrap", "marginBottom": "24px"},
            children=[

                html.Div([
                    html.Label("Products", style={"fontWeight": "600"}),
                    dcc.Checklist(
                        id="filter-products",
                        options=[{"label": p, "value": p} for p in ALL_PRODUCTS],
                        value=ALL_PRODUCTS,
                        inline=True,
                        inputStyle={"marginRight": "4px"},
                        labelStyle={"marginRight": "16px"},
                    ),
                ]),

                html.Div([
                    html.Label("Regions", style={"fontWeight": "600"}),
                    dcc.Checklist(
                        id="filter-regions",
                        options=[{"label": r, "value": r} for r in ALL_REGIONS],
                        value=ALL_REGIONS,
                        inline=True,
                        inputStyle={"marginRight": "4px"},
                        labelStyle={"marginRight": "16px"},
                    ),
                ]),

                html.Div([
                    html.Label("Month range", style={"fontWeight": "600"}),
                    dcc.RangeSlider(
                        id="filter-months",
                        min=0,
                        max=len(ALL_MONTHS) - 1,
                        value=[0, len(ALL_MONTHS) - 1],
                        marks={i: m for i, m in enumerate(ALL_MONTHS)},
                        allowCross=False,
                    ),
                ], style={"minWidth": "480px"}),
            ],
        ),

        # ── KPI cards ─────────────────────────────────────────────────────────
        html.Div(id="kpi-cards", style={"display": "flex", "gap": "16px", "marginBottom": "24px"}),

        # ── Charts row 1 ──────────────────────────────────────────────────────
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "16px", "marginBottom": "16px"},
            children=[
                html.Div([
                    html.H3("Revenue Over Time", style={"margin": "0 0 8px"}),
                    dcc.Graph(id="chart-line"),
                ], style=_card()),
                html.Div([
                    html.H3("Revenue by Product", style={"margin": "0 0 8px"}),
                    dcc.Graph(id="chart-pie"),
                ], style=_card()),
            ],
        ),

        # ── Charts row 2 ──────────────────────────────────────────────────────
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "24px"},
            children=[
                html.Div([
                    html.H3("Sales by Region", style={"margin": "0 0 8px"}),
                    dcc.Graph(id="chart-bar"),
                ], style=_card()),
                html.Div([
                    html.H3("Revenue Heatmap — Product × Region", style={"margin": "0 0 8px"}),
                    dcc.Graph(id="chart-heatmap"),
                ], style=_card()),
            ],
        ),

        # ── Data table ────────────────────────────────────────────────────────
        html.Div([
            html.H3("Raw Data", style={"margin": "0 0 8px"}),
            dash_table.DataTable(
                id="data-table",
                page_size=10,
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": "#343a40", "color": "white", "fontWeight": "bold"},
                style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"}],
            ),
        ], style=_card()),
    ],
)


# ── Helper ────────────────────────────────────────────────────────────────────

def _card() -> dict:
    return {
        "backgroundColor": "white",
        "borderRadius": "8px",
        "padding": "16px",
        "boxShadow": "0 1px 4px rgba(0,0,0,.1)",
    }


def kpi_card(label: str, value: str) -> html.Div:
    return html.Div(
        style={**_card(), "flex": "1", "textAlign": "center"},
        children=[
            html.P(label, style={"color": "#6c757d", "margin": "0 0 4px", "fontSize": "14px"}),
            html.H2(value, style={"margin": 0, "color": "#212529"}),
        ],
    )


# ── Callback ──────────────────────────────────────────────────────────────────

@app.callback(
    Output("kpi-cards",    "children"),
    Output("chart-line",   "figure"),
    Output("chart-pie",    "figure"),
    Output("chart-bar",    "figure"),
    Output("chart-heatmap","figure"),
    Output("data-table",   "data"),
    Output("data-table",   "columns"),
    Input("filter-products", "value"),
    Input("filter-regions",  "value"),
    Input("filter-months",   "value"),
)
def update_dashboard(products, regions, month_range):
    month_start = ALL_MONTHS[month_range[0]]
    month_end   = ALL_MONTHS[month_range[1]]

    filt = df[
        df["product"].isin(products or [])
        & df["region"].isin(regions or [])
        & (df["month"] >= month_start)
        & (df["month"] <= month_end)
    ]

    # KPIs
    kpis = [
        kpi_card("Total Revenue",       f"${filt['revenue'].sum():,.0f}"),
        kpi_card("Total Sales",          f"{filt['sales'].sum():,}"),
        kpi_card("Total Units",          f"{filt['units'].sum():,}"),
        kpi_card("Avg Revenue / Month",
                 f"${filt.groupby('month')['revenue'].sum().mean():,.0f}"
                 if not filt.empty else "$0"),
    ]

    # Line chart
    monthly = filt.groupby(["month", "product"])["revenue"].sum().reset_index()
    fig_line = px.line(monthly, x="month", y="revenue", color="product",
                       markers=True, template="plotly_white",
                       labels={"revenue": "Revenue ($)", "month": "Month"})
    fig_line.update_layout(margin=dict(t=10, b=10), legend_title_text="")

    # Pie chart
    by_product = filt.groupby("product")["revenue"].sum().reset_index()
    fig_pie = px.pie(by_product, names="product", values="revenue",
                     hole=0.42, template="plotly_white")
    fig_pie.update_traces(textinfo="percent+label")
    fig_pie.update_layout(margin=dict(t=10, b=10), showlegend=False)

    # Bar chart
    by_region = filt.groupby("region")["sales"].sum().reset_index()
    fig_bar = px.bar(by_region, x="region", y="sales", color="region",
                     text_auto=True, template="plotly_white",
                     labels={"sales": "Units Sold"},
                     color_discrete_sequence=px.colors.qualitative.Set2)
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(margin=dict(t=10, b=10), showlegend=False)

    # Heatmap
    if not filt.empty:
        pivot = filt.pivot_table(index="product", columns="region",
                                 values="revenue", aggfunc="sum")
        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="Blues",
            text=pivot.values.round(0),
            texttemplate="$%{text:,.0f}",
        ))
    else:
        fig_heat = go.Figure()
    fig_heat.update_layout(template="plotly_white", margin=dict(t=10, b=10))

    # Table
    table_data    = filt.to_dict("records")
    table_columns = [{"name": c, "id": c} for c in filt.columns]

    return kpis, fig_line, fig_pie, fig_bar, fig_heat, table_data, table_columns


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=8050)
