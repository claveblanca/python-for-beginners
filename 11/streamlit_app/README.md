# Streamlit — Interactive Sales Dashboard

Streamlit converts a plain Python script into an interactive web app.
Every time a widget changes, the script re-runs top to bottom and the UI updates automatically — no callbacks, no JavaScript.

Run the app:

```bash
pip install streamlit plotly pandas numpy
streamlit run app.py   # → http://localhost:8501
```

---

## 1. Page config

Always the first Streamlit call — sets the browser tab title, icon, and layout width.

```python
import streamlit as st

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",    # "wide" uses the full browser width; default is "centered"
)
```

---

## 2. Caching expensive computations — `@st.cache_data`

Without caching, the function re-runs on every widget interaction.
`@st.cache_data` caches the return value and skips re-execution unless the inputs change.

```python
@st.cache_data
def load_data() -> pd.DataFrame:
    # simulate a slow DB query or file load
    import time; time.sleep(2)
    return pd.read_csv("sales.csv")

df = load_data()   # only runs once; subsequent calls return the cached result
```

---

## 3. Sidebar — filters and navigation

`st.sidebar.*` places any widget in a collapsible panel on the left.

```python
st.sidebar.title("Filters")

selected_products = st.sidebar.multiselect(
    "Products",
    options=df["product"].unique(),
    default=df["product"].unique(),   # pre-select all
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
```

Every time the user changes a widget, the script re-runs and `selected_products` gets the new value automatically.

---

## 4. Columns — side-by-side layout

`st.columns()` returns a list of column containers. Use `with col:` or `col.method()`.

```python
# equal-width columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", "$1,200,000")
col2.metric("Total Sales",   "48,000")

# weighted columns (left is twice as wide as right)
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Revenue Over Time")
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    st.subheader("Revenue by Product")
    st.plotly_chart(fig_pie, use_container_width=True)
```

---

## 5. Metric cards — KPI display

`st.metric` renders a labelled value with an optional delta (change indicator).

```python
col1, col2 = st.columns(2)

col1.metric(
    label="Total Revenue",
    value="$1,200,000",
    delta="+8% vs last month",    # green if positive, red if negative
)

col2.metric(
    label="Avg Revenue / Month",
    value=f"${filtered.groupby('month')['revenue'].sum().mean():,.0f}",
)
```

---

## 6. Displaying Plotly charts

Pass any Plotly figure to `st.plotly_chart()`. `use_container_width=True` makes it fill its column.

```python
import plotly.express as px

fig = px.line(
    monthly_df,
    x="month",
    y="revenue",
    color="product",
    markers=True,
)
st.plotly_chart(fig, use_container_width=True)
```

---

## 7. Expander — collapsible sections

Useful for hiding verbose content (raw data, debug info) behind a toggle.

```python
with st.expander("View raw data"):
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

# anything indented under `with st.expander` is hidden until the user clicks it
```

---

## 8. Common display elements

```python
st.title("📊 Sales Dashboard")          # large page title
st.subheader("Revenue Over Time")       # section heading
st.markdown("**Bold** and *italic*")    # markdown text
st.divider()                            # horizontal rule
st.dataframe(df)                        # scrollable interactive table
st.write(df.describe())                 # smart display for any Python object
st.success("Done!")                     # green alert box
st.warning("Check your filters.")       # yellow alert box
st.error("Something went wrong.")       # red alert box
```

---

## Key concepts

| Concept | What it does |
|---|---|
| Script reruns top-to-bottom | Every widget interaction triggers a full re-run |
| `@st.cache_data` | Memoises a function's return value to skip re-computation |
| `st.sidebar.*` | Places widgets in the left-hand collapsible panel |
| `st.columns([2, 1])` | Side-by-side layout with optional width ratios |
| `st.metric()` | KPI card with optional delta / trend indicator |
| `st.plotly_chart()` | Renders any Plotly figure inline |
| `st.dataframe()` | Interactive, sortable table from a DataFrame |
| `st.expander()` | Collapsible section for secondary content |
| `use_container_width=True` | Makes charts/tables fill their column width |

## Technologies Used

- **Streamlit** — reactive Python web app framework (script-reruns model)
- **Plotly Express / Graph Objects** — interactive charts rendered via `st.plotly_chart`
- **pandas** — data filtering and aggregation
- **numpy** — synthetic dataset generation
