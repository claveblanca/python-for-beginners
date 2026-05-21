"""
dashboard.py — Streamlit app to explore news_sentiment results.

Run:
    streamlit run dashboard.py
    streamlit run dashboard.py -- --file other_results.json
"""

import argparse
import json
from pathlib import Path

import streamlit as st

# ── CLI argument for custom results file ──────────────────────────────────────
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--file", default="results.json")
args, _ = parser.parse_known_args()
RESULTS_FILE = Path(args.file)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="News Sentiment", page_icon="📰", layout="wide")

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

if not RESULTS_FILE.exists():
    st.error(f"File not found: `{RESULTS_FILE}`. Run `news_sentiment.py` first.")
    st.stop()

articles = load(RESULTS_FILE)

# ── Sentiment styling ─────────────────────────────────────────────────────────
SENTIMENT_EMOJI = {"positive": "🟢", "negative": "🔴", "neutral": "🟡", "unavailable": "⚪"}
SENTIMENT_COLOR = {"positive": "#d4edda", "negative": "#f8d7da", "neutral": "#fff3cd", "unavailable": "#e2e3e5"}

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📰 News Sentiment Dashboard")
st.caption(f"Source: `{RESULTS_FILE}`  •  {len(articles)} article(s)")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_summary, tab_articles, tab_raw = st.tabs(["📊 Summary", "📰 Articles", "🗂️ Raw JSON"])

# ─────────────────────────── TAB 1: Summary ───────────────────────────────────
with tab_summary:
    fetched   = [a for a in articles if a.get("body_fetched")]
    unfetched = [a for a in articles if not a.get("body_fetched")]

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total articles", len(articles))
    col2.metric("Body fetched",   len(fetched))
    col3.metric("Avg confidence", f"{sum(a['confidence'] for a in articles) / len(articles):.0%}")
    col4.metric("Unavailable",    len(unfetched))

    st.divider()

    # Sentiment breakdown
    from collections import Counter
    counts = Counter(a["sentiment"] for a in articles)

    st.subheader("Sentiment breakdown")
    cols = st.columns(len(counts))
    for col, (label, count) in zip(cols, counts.items()):
        emoji = SENTIMENT_EMOJI.get(label, "⚪")
        col.metric(f"{emoji} {label.capitalize()}", count)

    st.divider()

    # Per-article confidence bar
    st.subheader("Confidence per article")
    for a in articles:
        emoji = SENTIMENT_EMOJI.get(a["sentiment"], "⚪")
        label = f"{emoji} {a['title'][:80]}{'…' if len(a['title']) > 80 else ''}"
        st.progress(a["confidence"], text=f"{label}  —  {a['confidence']:.0%}")

# ─────────────────────────── TAB 2: Articles ──────────────────────────────────
with tab_articles:
    # Sidebar-style filter inside the tab
    sentiments = sorted({a["sentiment"] for a in articles})
    selected = st.multiselect(
        "Filter by sentiment",
        options=sentiments,
        default=sentiments,
    )

    filtered = [a for a in articles if a["sentiment"] in selected]
    st.caption(f"Showing {len(filtered)} of {len(articles)} article(s)")

    for a in filtered:
        color = SENTIMENT_COLOR.get(a["sentiment"], "#e2e3e5")
        emoji = SENTIMENT_EMOJI.get(a["sentiment"], "⚪")

        with st.expander(f"{emoji} {a['title']}", expanded=False):
            col_l, col_r = st.columns([3, 1])
            with col_l:
                st.markdown(f"[🔗 Open article]({a['url']})")
            with col_r:
                st.markdown(
                    f"<div style='background:{color};padding:6px 12px;"
                    f"border-radius:6px;text-align:center;font-weight:600'>"
                    f"{emoji} {a['sentiment'].upper()}  {a['confidence']:.0%}</div>",
                    unsafe_allow_html=True,
                )

            if a.get("text"):
                st.markdown("**Article text:**")
                st.markdown(
                    f"<div style='background:#f8f9fa;padding:12px;border-radius:6px;"
                    f"font-size:14px;line-height:1.6;max-height:300px;overflow-y:auto'>"
                    f"{a['text']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.warning("Article body not available.")

# ─────────────────────────── TAB 3: Raw JSON ──────────────────────────────────
with tab_raw:
    st.subheader("Raw results.json")
    st.json(articles)
