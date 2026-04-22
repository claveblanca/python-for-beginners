# Chapter 17 — SOCMINT with Python

Code from *Machine Learning with Python*, Chapter 17.  
Collect, clean, and analyse social-media data using Reddit, spaCy, TextBlob, NetworkX, and folium.

---

## Project layout

```
socmint/
├── collectors/
│   └── reddit.py          Fetch posts and comments from Reddit via PRAW
├── processing/
│   ├── cleaning.py        Strip URLs, mentions, markdown, emoji from raw text
│   ├── sentiment.py       TextBlob (fast) and RoBERTa (accurate) sentiment scoring
│   └── ner.py             Named entity extraction and corpus-level frequency counts
├── analysis/
│   ├── network.py         Build reply graphs, rank influencers, detect communities
│   ├── geo.py             Geocode place names, render interactive Leaflet maps
│   └── bots.py            Account-level bot scoring and posting-regularity detection
├── pipeline/
│   └── pipeline.py        Scheduled end-to-end pipeline with SQLite storage
├── requirements.txt
└── README.md
```

---

## Installation

```bash
pip install -r requirements.txt

# Download the spaCy English model (small, fast):
python -m spacy download en_core_web_sm

# For higher NER accuracy, use the transformer model instead:
# python -m spacy download en_core_web_trf
```

---

## Reddit credentials

PRAW requires a Reddit application.

1. Go to <https://www.reddit.com/prefs/apps> and create a new app.
2. Choose type **script** and set the redirect URI to `http://localhost:8080`.
3. Export the credentials as environment variables:

```bash
export REDDIT_CLIENT_ID=your_client_id
export REDDIT_CLIENT_SECRET=your_client_secret
export REDDIT_USER_AGENT='socmint-book/1.0 by u/your_username'
```

Or place them in a `.env` file (never commit this file):

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=socmint-book/1.0 by u/your_username
```

---

## Module reference

### `collectors/reddit.py`

Fetch posts and comments from any public subreddit.

```python
from collectors.reddit import fetch_subreddit_posts, fetch_post_comments

# Fetch the 25 hottest posts from r/worldnews
posts = fetch_subreddit_posts("worldnews", mode="hot", limit=25)
for p in posts:
    print(f"[{p.score:>6}] {p.title[:70]}")

# Fetch up to 200 comments from a specific post
comments = fetch_post_comments("1abc23", limit=200)
print(comments[0])
```

**`fetch_subreddit_posts(subreddit_name, mode, limit)`**
- `mode`: `"hot"` | `"new"` | `"top"` | `"rising"`
- Returns a list of `RedditPost` dataclasses with fields: `post_id`, `subreddit`, `title`, `selftext`, `score`, `num_comments`, `author`, `created_utc`, `url`, `flair`.

**`fetch_post_comments(post_id, limit)`**
- Returns a flat list of dicts with keys: `comment_id`, `post_id`, `author`, `body`, `score`, `depth`, `created_utc`.

---

### `processing/cleaning.py`

Normalise raw social-media text before passing it to any NLP model.

```python
from processing.cleaning import clean_text, demojize

# Strip URLs, mentions, markdown, and emoji; lowercase
clean = clean_text("Check this! **https://example.com** u/user123 🔥")
# → 'check this!'

# Keep emoji but convert to text descriptors
text = demojize("Great news! 🎉 Ceasefire holding 🕊️")
# → "Great news!  :party_popper:  Ceasefire holding  :dove: "
```

`clean_text(text, keep_emoji=False)` — pass `keep_emoji=True` to retain emoji characters in output.

`demojize(text)` — use before sentiment analysis to preserve the emotional signal carried by emoji.

---

### `processing/sentiment.py`

Two scoring approaches: fast rule-based (TextBlob) and accurate transformer (RoBERTa).

```python
from processing.sentiment import (
    score_sentiment_textblob,
    score_sentiment_transformer,
    score_batch_transformer,
)

# Fast — no model download, good for triage
result = score_sentiment_textblob("The situation is getting worse every day.")
# → {'polarity': -0.35, 'subjectivity': 0.6, 'label': 'negative'}

# Accurate — downloads ~500 MB model on first call
result = score_sentiment_transformer("Absolutely devastating. Words fail.")
# → {'label': 'negative', 'score': 0.9871}

# Batched — always prefer this over looping for throughput
texts   = ["Great outcome.", "Terrible decision.", "Status quo."]
results = score_batch_transformer(texts)
```

**Choosing between the two:**

| | TextBlob | Transformer |
|---|---|---|
| Speed | Very fast | Slower (GPU helps) |
| Accuracy | Moderate | High |
| Model download | None | ~500 MB |
| Handles irony/negation | Poor | Good |
| Best for | High-volume triage | Production scoring |

---

### `processing/ner.py`

Extract and count named entities (people, organisations, locations) across posts.

```python
from processing.ner import extract_entities, entity_frequency

# Single document
entities = extract_entities(
    "Zelensky met NATO's Stoltenberg in Kyiv on Monday."
)
for e in entities:
    print(f"[{e['label']:8s}] {e['text']}")
# → [PERSON  ] Zelensky
# → [ORG     ] NATO
# → [PERSON  ] Stoltenberg
# → [GPE     ] Kyiv
# → [DATE    ] Monday

# Aggregate across many posts
titles = [p.title for p in posts]
freq   = entity_frequency(titles)
for loc, count in freq['GPE'].most_common(5):
    print(f"  {loc:<20s} {count:>3d}")
```

Entity types: `PERSON`, `ORG`, `GPE` (country/city), `LOC`, `DATE`, `PRODUCT`, `EVENT`.

---

### `analysis/network.py`

Model who replies to whom and find the accounts that drive conversation.

```python
from analysis.network import (
    build_reply_network,
    top_accounts_by_centrality,
    detect_communities,
)

G      = build_reply_network(comments)
result = top_accounts_by_centrality(G, top_n=5)

print("Top accounts by in-degree (most replied-to):")
for name, score in result['in_degree']:
    print(f"  {name:<25s} {score:.4f}")

# Community detection (requires python-louvain)
partition = detect_communities(G)
from collections import Counter
sizes = Counter(partition.values())
print(f"Communities detected: {len(sizes)}")
```

`build_reply_network(comments)` — returns an `nx.DiGraph`. Each edge `A → B` means A replied to B; edge weight is the reply count.

`top_accounts_by_centrality(G, top_n)` — returns `{'in_degree': [...], 'pagerank': [...]}`.

`detect_communities(G)` — returns `{username: community_id}` dict. Requires `pip install python-louvain`.

---

### `analysis/geo.py`

Geocode place names and render them on an interactive map.

```python
from analysis.geo import geocode, build_activity_map

# Geocode a place name (cached; 1 s sleep between uncached calls)
lat, lon = geocode("Kyiv")
# → (50.4501, 30.5238)

# Build a map from a list of geolocated posts
posts_with_coords = [
    {"title": "Drone attack reported", "lat": 50.45, "lon": 30.52,
     "score": 12000, "sentiment_label": "negative"},
    {"title": "Aid convoy arrives",    "lat": 49.99, "lon": 36.23,
     "score": 3400,  "sentiment_label": "positive"},
]
build_activity_map(posts_with_coords, output_path="map.html")
# Opens map.html in a browser — red/green/blue circle markers, clickable popups
```

Marker colour encodes sentiment (`red` = negative, `green` = positive, `blue` = neutral). Marker radius scales with post score (4–20 px).

---

### `analysis/bots.py`

Score individual accounts and flag suspicious posting patterns.

```python
from analysis.bots import AccountProfile, bot_score, posting_regularity

# Account-level heuristics
profile = AccountProfile(
    username="u/news_alert_247",
    account_age_days=3,
    post_count=412,
    comment_count=88,
    karma=1,
    has_avatar=False,
    verified_email=False,
)
print(bot_score(profile))
# → {'username': 'u/news_alert_247', 'bot_score': 0.9,
#    'flags': ['HIGH_ACTIVITY_RATE', 'VERY_NEW_ACCOUNT',
#              'NO_AVATAR', 'UNVERIFIED_EMAIL']}

# Posting-interval regularity (requires datetime list)
from datetime import datetime, timedelta, timezone
base   = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
times  = [base + timedelta(seconds=60 * i) for i in range(20)]
print(posting_regularity(times))
# → {'mean_interval_s': 60.0, 'std_interval_s': 0.0,
#    'regularity_score': 1.0, 'verdict': 'SUSPICIOUS'}
```

`bot_score` returns a score in [0.0, 1.0]. Scores above 0.5 warrant investigation; above 0.8 are strongly suspicious.

`posting_regularity` measures the coefficient of variation of inter-post gaps. A regularity score above 0.7 triggers a `'SUSPICIOUS'` verdict.

---

### `pipeline/pipeline.py`

Full end-to-end pipeline: collect → analyse → store → alert.

```python
from pipeline.pipeline import SocmintPipeline

# Collect 100 posts once and write results to socmint.db
pipeline = SocmintPipeline('socmint.db')
pipeline.run_once('worldnews', limit=100)

# Run continuously, collecting every 5 minutes
pipeline.run_scheduled('worldnews', interval_s=300)
```

Each run fetches posts, scores sentiment, extracts entities, upserts all results into SQLite, and emits a `WARNING` log for any post with polarity < −0.5 and score > 5,000.

**Database schema** (`socmint.db`, table `posts`):

| Column | Type | Description |
|---|---|---|
| `post_id` | TEXT PK | Reddit post ID |
| `subreddit` | TEXT | Source subreddit |
| `title` | TEXT | Post title |
| `selftext` | TEXT | Post body |
| `score` | INTEGER | Upvote score |
| `num_comments` | INTEGER | Comment count |
| `author` | TEXT | Username |
| `created_utc` | TEXT | ISO-8601 post timestamp |
| `sentiment` | TEXT | JSON — polarity, subjectivity, label |
| `entities` | TEXT | JSON — list of NER entity dicts |
| `collected_at` | TEXT | ISO-8601 collection timestamp |

---

## Quick-start: full pipeline in 10 lines

```python
from collectors.reddit import fetch_subreddit_posts
from processing.cleaning import clean_text
from processing.sentiment import score_sentiment_textblob
from processing.ner import entity_frequency

posts   = fetch_subreddit_posts("worldnews", mode="hot", limit=50)
titles  = [p.title for p in posts]
freq    = entity_frequency(titles)

for loc, count in freq['GPE'].most_common(10):
    score = score_sentiment_textblob(loc)
    print(f"  {loc:<20s} mentions={count:>3d}  sentiment={score['label']}")
```

---

## Legal and ethical notes

- Collect only what you need — data minimisation is both an ethical principle and a GDPR requirement.
- Never de-anonymise pseudonymous accounts without a documented lawful basis.
- Respect rate limits — Reddit's API allows ~60 requests/minute for authenticated clients.
- Do not publish raw posts with usernames attached without editorial necessity.
- Reddit's API Terms of Service prohibit using collected data to train commercial AI models.
- Store collected data with access controls; do not leave `socmint.db` world-readable.
