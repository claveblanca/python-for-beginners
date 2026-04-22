"""
Chapter 13 — Example 01: The Hugging Face Pipeline API
=======================================================
Covers section 13.1:
  - Loading pipelines for different NLP tasks
  - Running single and batch inference
  - Understanding the result dictionary (label, score)
  - Choosing a specific model from the Hub
  - GPU vs CPU device selection
  - Returning all scores with top_k

Install:
    pip install transformers torch
"""

from transformers import pipeline

# ── 1. Default sentiment pipeline (DistilBERT fine-tuned on SST-2) ────────────

print("=" * 60)
print("1. DEFAULT SENTIMENT PIPELINE")
print("=" * 60)

# pipeline() downloads and caches ~250 MB on first run.
# Subsequent calls load from the local cache instantly.
sentiment = pipeline("sentiment-analysis")

# Single string — always returns a list; index [0] for the result dict
result = sentiment("I absolutely love this product!")[0]
print(f"Label : {result['label']}")
print(f"Score : {result['score']:.4f}")


# ── 2. Batch inference — more efficient than one call per text ────────────────

print("\n" + "=" * 60)
print("2. BATCH INFERENCE")
print("=" * 60)

texts = [
    "The course was absolutely fantastic — best investment I've made.",
    "Broke after two days. Terrible quality, avoid.",
    "Delivery was fast. Product is okay, nothing special.",
    "I've used this every day for a year. Highly recommended.",
    "Customer service was unhelpful and rude.",
]

# Pass a list → get a list back — much faster than looping one at a time
results = sentiment(texts)

print(f"{'Text':<55} {'Label':<10} {'Score'}")
print("-" * 80)
for text, res in zip(texts, results):
    print(f"{text[:52]:<55} {res['label']:<10} {res['score']:.3f}")


# ── 3. All scores with top_k ──────────────────────────────────────────────────

print("\n" + "=" * 60)
print("3. ALL CLASS SCORES WITH top_k")
print("=" * 60)

# top_k=None returns scores for every class, not just the top one
all_scores = sentiment("The product is decent but overpriced.", top_k=None)
print("All class scores:")
for s in sorted(all_scores, key=lambda x: -x["score"]):
    bar = "█" * int(s["score"] * 30)
    print(f"  {s['label']:<12} {bar:<32} {s['score']:.4f}")


# ── 4. Choosing a specific model from the Hugging Face Hub ───────────────────

print("\n" + "=" * 60)
print("4. SPECIFIC MODEL FROM THE HUB")
print("=" * 60)

# cardiffnlp/twitter-roberta-base-sentiment-latest: 3-class (positive/neutral/negative)
# Trained on Twitter data — better for short, informal text
twitter_sentiment = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
)

tweets = [
    "Just got my order 🎉 Packaging was perfect and arrived early!",
    "Three weeks and still no refund. Completely unacceptable 😤",
    "It works as described.",
]

print("Twitter-trained model (3-class):")
for tweet, res in zip(tweets, twitter_sentiment(tweets)):
    print(f"  [{res['label']:<10} {res['score']:.3f}]  {tweet}")


# ── 5. Other NLP pipeline tasks ───────────────────────────────────────────────

print("\n" + "=" * 60)
print("5. OTHER PIPELINE TASKS")
print("=" * 60)

# Named Entity Recognition
ner = pipeline("ner", aggregation_strategy="simple")
ner_text = "Elon Musk founded SpaceX in 2002 and Tesla is headquartered in Austin, Texas."
entities = ner(ner_text)
print("Named entities:")
for ent in entities:
    print(f"  {ent['word']:<20} {ent['entity_group']:<10} score={ent['score']:.3f}")

# Zero-shot classification — no fine-tuning needed
zero_shot = pipeline("zero-shot-classification")
zs_result = zero_shot(
    "The new firmware update broke my WiFi connection.",
    candidate_labels=["software bug", "hardware failure", "user error", "network issue"],
)
print("\nZero-shot classification:")
for label, score in zip(zs_result["labels"], zs_result["scores"]):
    bar = "█" * int(score * 25)
    print(f"  {label:<20} {bar:<28} {score:.3f}")

# Summarisation
summariser = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")
long_text = """
Python has become the dominant language in machine learning and data science.
Its clean syntax, rich ecosystem of libraries such as NumPy, Pandas, and PyTorch,
and strong community support have made it the first choice for researchers and
engineers alike. The rise of Jupyter notebooks further accelerated adoption by
enabling interactive, reproducible workflows that combine code, visualisation,
and narrative text in a single document.
"""
summary = summariser(long_text, max_length=50, min_length=20, do_sample=False)
print(f"\nSummary: {summary[0]['summary_text'].strip()}")


# ── 6. Device selection — CPU vs GPU ─────────────────────────────────────────

print("\n" + "=" * 60)
print("6. DEVICE SELECTION")
print("=" * 60)

import torch

device = 0 if torch.cuda.is_available() else -1
device_name = f"GPU (cuda:{device})" if device >= 0 else "CPU"
print(f"Running on: {device_name}")

# Pass device= to pipeline; device=0 uses the first GPU
fast_pipeline = pipeline(
    "sentiment-analysis",
    device=device,
)
res = fast_pipeline("GPU inference is much faster for large batches.")[0]
print(f"Result: {res['label']} ({res['score']:.4f})")
print("\nNote: On CPU, inference still works — just slower for large volumes.")
print("For >1000 texts/day, a GPU or cloud endpoint is recommended.")
