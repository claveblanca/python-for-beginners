"""
Chapter 13 — Example 02: Sentiment Analysis in Depth
=====================================================
Covers section 13.2:
  - The analyze_sentiment() function — robust version
  - Confidence thresholds: when NOT to trust the model
  - Multi-class sentiment (positive / neutral / negative)
  - Processing a batch from a CSV-like dataset
  - Aggregating results: distribution + average confidence
  - Handling edge cases: empty input, very long text, emojis

Install:
    pip install transformers torch
"""

import statistics
from transformers import pipeline

# ── Load model once at module level (not inside the function) ─────────────────
# Loading inside the function would re-download weights on every call.
sentiment_pipeline = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    top_k=None,          # return all class scores every time
)

MAX_CHARS    = 512       # model token limit — truncate longer inputs
MIN_CONF     = 0.65      # below this threshold, return "uncertain"


# ── Core analysis function (section 13.2) ─────────────────────────────────────

def analyze_sentiment(text: str) -> dict:
    """
    Analyse the sentiment of a text string.

    Returns a dict:
      label       — 'positive', 'neutral', 'negative', or 'uncertain'
      confidence  — float 0–1 (top class score)
      all_scores  — {label: score} for every class
      truncated   — True if the input was cut to fit the model
    """
    # Step 1 — validate input
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    text = text.strip()
    if not text:
        return {
            "label":      "empty",
            "confidence": 0.0,
            "all_scores": {},
            "truncated":  False,
        }

    # Step 2 — truncate if necessary (model has a token limit)
    truncated = len(text) > MAX_CHARS
    if truncated:
        text = text[:MAX_CHARS]

    # Step 3 — run inference; pipeline returns a list of lists when top_k>1
    raw = sentiment_pipeline(text)[0]       # list of {label, score} dicts
    all_scores = {r["label"].lower(): r["score"] for r in raw}
    top        = max(raw, key=lambda x: x["score"])

    label      = top["label"].lower()
    confidence = top["score"]

    # Step 4 — apply confidence threshold
    if confidence < MIN_CONF:
        label = "uncertain"

    return {
        "label":      label,
        "confidence": round(confidence, 4),
        "all_scores": {k: round(v, 4) for k, v in all_scores.items()},
        "truncated":  truncated,
    }


def format_result(text: str, result: dict) -> str:
    """Pretty-print a single analysis result."""
    label = result["label"].upper()
    conf  = result["confidence"]
    bar   = "█" * int(conf * 20)
    trunc = " [truncated]" if result["truncated"] else ""
    preview = text[:60] + ("…" if len(text) > 60 else "")
    return (
        f"  Text       : {preview!r}{trunc}\n"
        f"  Sentiment  : {label}\n"
        f"  Confidence : {bar:<22} {conf:.3f}\n"
    )


# ── 1. Basic usage ─────────────────────────────────────────────────────────────

print("=" * 60)
print("1. BASIC USAGE")
print("=" * 60)

test_cases = [
    "I absolutely love this product — exceeded every expectation!",
    "Broke after two days. Terrible quality. Never again.",
    "The product works as described. Delivery was on time.",
    "Not bad, not great. I've seen better for the price.",
]

for text in test_cases:
    result = analyze_sentiment(text)
    print(format_result(text, result))


# ── 2. Edge cases ──────────────────────────────────────────────────────────────

print("=" * 60)
print("2. EDGE CASES")
print("=" * 60)

edge_cases = {
    "empty string":   "",
    "only spaces":    "     ",
    "single emoji":   "😊",
    "mixed emoji":    "Great product! 😍🎉 Would buy again 💯",
    "very negative":  "🤬🤬🤬 WORST PURCHASE OF MY LIFE",
    "long text":      "Good " * 200,   # 200 repetitions — will be truncated
    "numbers only":   "12345 67890",
    "punctuation":    "!!!???...",
}

for name, text in edge_cases.items():
    result = analyze_sentiment(text)
    trunc  = " [TRUNCATED]" if result["truncated"] else ""
    print(f"  {name:<20} → {result['label']:<12} conf={result['confidence']:.3f}{trunc}")


# ── 3. Confidence threshold in action ─────────────────────────────────────────

print("\n" + "=" * 60)
print(f"3. CONFIDENCE THRESHOLD (MIN_CONF = {MIN_CONF})")
print("=" * 60)

ambiguous = [
    "The product is fine.",
    "It arrived.",
    "I suppose it could be worse.",
    "Interesting choice of design.",
    "I wasn't sure what to expect.",
]

for text in ambiguous:
    result = analyze_sentiment(text)
    flag   = " ← UNCERTAIN (below threshold)" if result["label"] == "uncertain" else ""
    print(f"  [{result['confidence']:.3f}] {result['label']:<12}  {text[:50]}{flag}")


# ── 4. Batch processing from a dataset ────────────────────────────────────────

print("\n" + "=" * 60)
print("4. BATCH PROCESSING")
print("=" * 60)

# Simulated product review dataset
reviews = [
    {"id": 1, "product": "Laptop",    "review": "Incredible performance, silent fans, great display."},
    {"id": 2, "product": "Laptop",    "review": "Runs hot under load. Battery life disappointing."},
    {"id": 3, "product": "Headphones","review": "Best headphones I've ever owned. Worth every penny."},
    {"id": 4, "product": "Headphones","review": "Broke the first day. Cheap plastic everywhere."},
    {"id": 5, "product": "Laptop",    "review": "Decent machine, nothing special, does the job."},
    {"id": 6, "product": "Headphones","review": "Surprisingly good sound for the price."},
    {"id": 7, "product": "Laptop",    "review": "Fan noise is unbearable. Returned immediately."},
    {"id": 8, "product": "Headphones","review": "Comfortable to wear all day. Solid build quality."},
]

print(f"  {'ID':<4} {'Product':<13} {'Sentiment':<12} {'Conf':<7} {'Review'}")
print("  " + "-" * 75)

enriched = []
for row in reviews:
    result = analyze_sentiment(row["review"])
    row["sentiment"]  = result["label"]
    row["confidence"] = result["confidence"]
    enriched.append(row)
    print(f"  {row['id']:<4} {row['product']:<13} {result['label']:<12} "
          f"{result['confidence']:.3f}  {row['review'][:45]}")


# ── 5. Aggregate statistics ────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("5. AGGREGATE STATISTICS")
print("=" * 60)

from collections import defaultdict, Counter

# Overall distribution
overall = Counter(r["sentiment"] for r in enriched)
print("Overall sentiment distribution:")
for label, count in sorted(overall.items()):
    pct = count / len(enriched) * 100
    bar = "█" * count
    print(f"  {label:<12} {bar:<12} {count} ({pct:.0f}%)")

# Per-product breakdown
by_product: dict[str, list] = defaultdict(list)
for row in enriched:
    by_product[row["product"]].append(row)

print("\nPer-product summary:")
for product, rows in by_product.items():
    dist   = Counter(r["sentiment"] for r in rows)
    avg_conf = statistics.mean(r["confidence"] for r in rows)
    print(f"\n  {product}:")
    for label, cnt in sorted(dist.items()):
        print(f"    {label:<12} × {cnt}")
    print(f"    Avg confidence: {avg_conf:.3f}")


# ── 6. Scoring a text by sentence ────────────────────────────────────────────

print("\n" + "=" * 60)
print("6. SENTENCE-BY-SENTENCE SCORING")
print("=" * 60)

import re

def score_by_sentence(text: str) -> list[dict]:
    """
    Split text into sentences and score each individually.
    Useful for finding which part of a review is positive/negative.
    """
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    results = []
    for sent in sentences:
        r = analyze_sentiment(sent)
        results.append({"sentence": sent, **r})
    return results


mixed_review = (
    "The laptop arrived well-packaged and on time. "
    "Setup was straightforward and the display is gorgeous. "
    "However, the fan noise is quite loud under any real load. "
    "Battery life is also a disappointment — barely 6 hours. "
    "Overall a mixed bag, but I'm keeping it for the screen quality."
)

print("Mixed review — sentence breakdown:")
for item in score_by_sentence(mixed_review):
    emoji = {"positive": "✅", "negative": "❌", "neutral": "➖", "uncertain": "❓"}.get(item["label"], "?")
    print(f"  {emoji} [{item['label']:<10} {item['confidence']:.2f}]  {item['sentence'][:60]}")
