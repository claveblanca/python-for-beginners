# Chapter 14 — Financial News Scraping & Sentiment Analysis

## Scope

This chapter builds a three-stage intelligence pipeline for financial news:

1. **Scrape** the latest article headlines and URLs from Investing.com
2. **Fetch** the full article body for each URL, then classify its tone using a pre-trained NLP model
3. **Visualise** the results in an interactive Streamlit dashboard

The pipeline is deliberately split into three independent scripts that communicate via files (`output.txt` → `results.json`), so each stage can be run and debugged separately.

```
latest_news.py  ──►  output.txt  ──►  news_sentiment.py  ──►  results.json  ──►  dashboard.py
  (scrape)               │               (fetch + NLP)               │              (UI)
                    titles & URLs                              sentiment scores
```

---

## Technologies

| Tool | Role |
|---|---|
| **requests** | HTTP client for fetching pages |
| **curl_cffi** | Chrome TLS impersonation — bypasses WAF 403 blocks |
| **BeautifulSoup** | HTML parsing and content extraction |
| **Hugging Face Transformers** | Pre-trained sentiment model (`cardiffnlp/twitter-roberta-base-sentiment-latest`) |
| **PyTorch** | Inference backend for the Transformers model |
| **Streamlit** | Interactive results dashboard |

---

## Phase 1 — Scrape the latest news listing

**File:** `latest_news.py`

Financial news sites like Investing.com actively block automated clients. A plain `requests.get()` returns HTTP 403. The solution is **TLS fingerprint impersonation**: `curl_cffi` replaces the Python TLS handshake with one that is byte-for-byte identical to Chrome's.

### 1.1 Session warm-up and TLS impersonation

```python
import requests
from curl_cffi import requests as curl_requests  # pip install curl-cffi

BASE = "https://www.investing.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Mode": "navigate",
    # ... full Chrome header set
}

def fetch(url: str) -> str:
    session = curl_requests.Session()

    # 1. Warm the session — visit homepage first so the WAF sees
    #    a normal multi-page browsing session, not a direct deep-link.
    session.get(BASE + "/", headers=HEADERS, timeout=15, impersonate="chrome131")

    # 2. Fetch the actual target page
    res = session.get(url, headers=HEADERS, timeout=15, impersonate="chrome131")
    res.raise_for_status()
    return res.text
```

### 1.2 Parsing article links with BeautifulSoup

Article URLs on Investing.com follow the pattern `/news/<category>/<slug>-<id>`.
The parser finds all `<a>` tags, filters by path structure, deduplicates, and extracts the link text as the title.

```python
from bs4 import BeautifulSoup

def parse_articles(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    articles, seen = [], set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        # normalise absolute URLs → relative path
        if href.startswith(BASE):
            href = href[len(BASE):]
        # keep only article paths: /news/<category>/<slug>
        if not href.startswith("/news/") or href.count("/") < 3:
            continue
        url = BASE + href.split("?")[0]
        if url in seen:
            continue
        seen.add(url)
        title = a.get_text(separator=" ", strip=True)
        if title:
            articles.append({"title": title, "url": url})

    return articles
```

### 1.3 Running Phase 1

```bash
# print to terminal
python latest_news.py --limit 10

# save to file for Phase 2
python latest_news.py --limit 10 -o output.txt

# debug mode — shows raw href samples if no articles found
python latest_news.py --debug
```

Output format written to `output.txt`:

```
  1. BofA names top chip stocks as server CPU TAM seen reaching $125bn by 2030
     https://www.investing.com/news/stock-market-news/bofa-names-top-...
  2. Can Nvidia's results shift market focus back to AI?
     https://www.investing.com/news/stock-market-news/can-nvidias-results-...
```

---

## Phase 2 — Fetch article content and run sentiment analysis

**File:** `news_sentiment.py`

### 2.1 Loading the sentiment model

The model is loaded **once at startup** outside any loop. Loading inside a loop would re-download the weights on every article — instead it stays in GPU/CPU memory for the whole run.

```python
from transformers import pipeline

# loaded once — stays in memory for the entire run
_sentiment = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    top_k=None,   # return scores for all classes, not just the top one
)
```

The model `cardiffnlp/twitter-roberta-base-sentiment-latest` is a RoBERTa transformer fine-tuned on 124M tweets and financial text. It classifies text into **positive**, **neutral**, or **negative** and returns a confidence score for each.

### 2.2 Parsing the output.txt input file

```python
import re
from pathlib import Path

def parse_output_file(path: Path) -> list[dict]:
    """Parse the numbered Title / URL format written by latest_news.py."""
    entries, title = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s+\d+\.\s+(.+)$", line)  # "  1. Title"
        if m:
            title = m.group(1).strip()
        elif title and line.strip().startswith("http"):
            entries.append({"title": title, "url": line.strip()})
            title = None
    return entries
```

### 2.3 Fetching the article body

Investing.com places article body text inside `<div id="article">`.
The function returns an empty string on any error — the pipeline continues to the next article rather than aborting.

```python
from bs4 import BeautifulSoup

def fetch_article_text(session, url: str) -> str:
    try:
        res = session.get(url, headers=HEADERS, timeout=20, impersonate="chrome131")
        if res.status_code != 200:
            return ""
        soup = BeautifulSoup(res.text, "html.parser")
        body = soup.find("div", id="article")   # target element
        if not body:
            return ""
        return body.get_text(separator=" ", strip=True)
    except Exception:
        return ""
```

### 2.4 Running sentiment inference

The model has a 512-token limit. The text is truncated to 512 characters before inference to avoid silent errors. `top_k=None` returns scores for all three classes; we take the highest.

```python
def analyze(text: str) -> dict:
    text = text.strip()[:512]    # model token limit
    if not text:
        return {"label": "empty", "confidence": 0.0}

    raw = _sentiment(text)[0]    # list of {label, score} for each class
    top = max(raw, key=lambda x: x["score"])

    return {
        "label":      top["label"].lower(),      # "positive" | "neutral" | "negative"
        "confidence": round(top["score"], 4),    # 0.0 – 1.0
    }
```

### 2.5 The full pipeline loop

```python
results = []
for i, entry in enumerate(entries, 1):
    body = fetch_article_text(session, entry["url"])
    if not body:
        results.append({**entry, "sentiment": "unavailable",
                        "confidence": 0.0, "body_fetched": False, "text": ""})
        continue

    sentiment = analyze(body)
    results.append({
        "title":       entry["title"],
        "url":         entry["url"],
        "sentiment":   sentiment["label"],
        "confidence":  sentiment["confidence"],
        "body_fetched": True,
        "text":        body,
    })
```

### 2.6 Running Phase 2

```bash
# reads output.txt, prints summary to terminal
python news_sentiment.py

# save full results (with article text) to JSON
python news_sentiment.py -i output.txt -o results.json
```

Terminal output:

```
🟢  [POSITIVE  72%]  BofA names top chip stocks…
🟡  [NEUTRAL   74%]  Can Nvidia's results shift market focus back to AI?
🟡  [NEUTRAL   74%]  Trump's comments on Iran war…
🟢  [POSITIVE  74%]  ASML gains after UBS calls it Europe's top semiconductor pick
🟢  [POSITIVE  77%]  Stocks rise as Nvidia gains pre-earnings…
```

---

## Phase 3 — Streamlit dashboard

**File:** `dashboard.py`

### 3.1 Loading results and guard against missing file

```python
import streamlit as st
import json
from pathlib import Path

RESULTS_FILE = Path("results.json")

@st.cache_data          # cache so the file isn't re-read on every widget interaction
def load(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

if not RESULTS_FILE.exists():
    st.error("File not found. Run `news_sentiment.py -o results.json` first.")
    st.stop()           # halt execution — nothing below this runs

articles = load(RESULTS_FILE)
```

### 3.2 Three-tab layout

```python
tab_summary, tab_articles, tab_raw = st.tabs(
    ["📊 Summary", "📰 Articles", "🗂️ Raw JSON"]
)
```

### 3.3 Summary tab — KPIs and confidence bars

```python
with tab_summary:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total articles", len(articles))
    col2.metric("Body fetched",   sum(1 for a in articles if a["body_fetched"]))
    col3.metric("Avg confidence",
                f"{sum(a['confidence'] for a in articles) / len(articles):.0%}")

    st.divider()
    st.subheader("Confidence per article")

    EMOJI = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}
    for a in articles:
        emoji = EMOJI.get(a["sentiment"], "⚪")
        st.progress(
            a["confidence"],
            text=f"{emoji} {a['title'][:80]}  —  {a['confidence']:.0%}"
        )
```

### 3.4 Articles tab — filter and expandable cards

```python
with tab_articles:
    selected = st.multiselect(
        "Filter by sentiment",
        options=sorted({a["sentiment"] for a in articles}),
        default=sorted({a["sentiment"] for a in articles}),
    )

    COLOR = {"positive": "#d4edda", "negative": "#f8d7da", "neutral": "#fff3cd"}

    for a in [x for x in articles if x["sentiment"] in selected]:
        with st.expander(f"{EMOJI.get(a['sentiment'], '⚪')} {a['title']}"):
            col_l, col_r = st.columns([3, 1])
            col_l.markdown(f"[🔗 Open article]({a['url']})")
            col_r.markdown(
                f"<div style='background:{COLOR.get(a['sentiment'], '#eee')};"
                f"padding:6px 12px;border-radius:6px;text-align:center;"
                f"font-weight:600'>{a['sentiment'].upper()}  {a['confidence']:.0%}</div>",
                unsafe_allow_html=True,
            )
            if a.get("text"):
                st.markdown(
                    f"<div style='background:#f8f9fa;padding:12px;border-radius:6px;"
                    f"font-size:14px;max-height:300px;overflow-y:auto'>{a['text']}</div>",
                    unsafe_allow_html=True,
                )
```

### 3.5 Raw JSON tab

```python
with tab_raw:
    st.json(articles)   # collapsible, searchable JSON explorer
```

### 3.6 Running Phase 3

```bash
streamlit run dashboard.py

# use a different results file
streamlit run dashboard.py -- --file my_results.json
```

---

## Full pipeline — end to end

```bash
# 1. install dependencies
pip install -r requirements.txt
pip install curl-cffi          # recommended: bypasses 403 blocks

# 2. scrape latest news headlines
python latest_news.py --limit 10 -o output.txt

# 3. fetch article bodies and run sentiment
python news_sentiment.py -i output.txt -o results.json

# 4. launch dashboard
streamlit run dashboard.py
```

---

## Key concepts

| Concept | Where used | Why |
|---|---|---|
| TLS fingerprint impersonation | `latest_news.py`, `news_sentiment.py` | Financial sites block Python's default TLS — `curl_cffi` mimics Chrome at the handshake level |
| Session warm-up | both scrapers | Visit the homepage first so the WAF sees a normal multi-page session |
| HTML parsing with CSS selectors | `latest_news.py` | Filter `<a>` tags by URL path structure to find article links |
| Target element extraction | `news_sentiment.py` | `soup.find("div", id="article")` isolates body text from nav/ads |
| Pre-trained NLP pipeline | `news_sentiment.py` | Zero training needed — load a fine-tuned model and call `.pipeline()` |
| Text truncation | `news_sentiment.py` | Transformers have a 512-token limit; truncating avoids silent errors |
| `@st.cache_data` | `dashboard.py` | Prevents re-loading the JSON file on every widget interaction |
| File-based pipeline | all scripts | Each stage writes to a file, so stages are independently runnable and debuggable |
