"""
Streamlit — Interactive Sales Dashboard
Run: streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Shared dataset ────────────────────────────────────────────────────────────

@st.cache_data
def load_data() -> pd.DataFrame:
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

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────

st.sidebar.title("Filters")

selected_products = st.sidebar.multiselect(
    "Products",
    options=df["product"].unique(),
    default=df["product"].unique(),
)

selected_regions = st.sidebar.multiselect(
    "Regions",
    options=df["region"].unique(),
    default=df["region"].unique(),
)

date_range = st.sidebar.date_input(
    "Date range",
    value=(df["month"].min(), df["month"].max()),
)

# ── Filter data ───────────────────────────────────────────────────────────────

mask = (
    df["product"].isin(selected_products)
    & df["region"].isin(selected_regions)
    & (df["month"] >= pd.Timestamp(date_range[0]))
    & (df["month"] <= pd.Timestamp(date_range[-1]))
)
filtered = df[mask]

# ── Header ────────────────────────────────────────────────────────────────────

st.title("📊 Sales Dashboard")
st.markdown("Interactive dashboard built with **Streamlit** + **Plotly**.")

# ── KPI cards ─────────────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"${filtered['revenue'].sum():,.0f}")
col2.metric("Total Sales",   f"{filtered['sales'].sum():,}")
col3.metric("Total Units",   f"{filtered['units'].sum():,}")
col4.metric("Avg Revenue / Month",
            f"${filtered.groupby('month')['revenue'].sum().mean():,.0f}")

st.divider()

# ── Row 1: Line chart + Pie chart ─────────────────────────────────────────────

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Revenue Over Time")
    monthly = (
        filtered.groupby(["month", "product"])["revenue"]
        .sum()
        .reset_index()
    )
    fig_line = px.line(
        monthly,
        x="month",
        y="revenue",
        color="product",
        markers=True,
        labels={"revenue": "Revenue ($)", "month": "Month"},
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    st.subheader("Revenue by Product")
    by_product = filtered.groupby("product")["revenue"].sum().reset_index()
    fig_pie = px.pie(by_product, names="product", values="revenue", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Row 2: Bar chart + Heatmap ────────────────────────────────────────────────

col_left2, col_right2 = st.columns([1, 1])

with col_left2:
    st.subheader("Sales by Region")
    by_region = filtered.groupby("region")["sales"].sum().reset_index()
    fig_bar = px.bar(
        by_region,
        x="region",
        y="sales",
        color="region",
        text_auto=True,
        labels={"sales": "Units Sold"},
    )
    fig_bar.update_traces(textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right2:
    st.subheader("Revenue Heatmap — Product × Region")
    pivot = filtered.pivot_table(
        index="product", columns="region", values="revenue", aggfunc="sum"
    )
    fig_heat = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="Blues",
            text=pivot.values.round(0),
            texttemplate="%{text:,.0f}",
        )
    )
    fig_heat.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_heat, use_container_width=True)

# ── Raw data expander ─────────────────────────────────────────────────────────

with st.expander("View raw data"):
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True)
