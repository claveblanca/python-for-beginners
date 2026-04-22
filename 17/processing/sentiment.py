"""
processing/sentiment.py
Sentiment analysis: fast rule-based (TextBlob) and
high-accuracy transformer-based (cardiffnlp/twitter-roberta).

Dependencies:
    pip install textblob transformers torch
"""

from textblob import TextBlob
from transformers import pipeline as hf_pipeline

from .cleaning import clean_text


def score_sentiment_textblob(text: str) -> dict:
    """
    Score sentiment using TextBlob's rule-based analyser.

    Fast and requires no model download. Best used for high-volume
    triage where processing speed matters more than accuracy.

    Args:
        text: Raw or pre-cleaned input string.

    Returns:
        Dict with keys:
            polarity     float in [-1.0, +1.0]
            subjectivity float in [0.0, 1.0]
            label        'positive' | 'neutral' | 'negative'
    """
    blob = TextBlob(clean_text(text))
    return {
        "polarity":     round(blob.sentiment.polarity, 4),
        "subjectivity": round(blob.sentiment.subjectivity, 4),
        "label": (
            "positive" if blob.sentiment.polarity >  0.05 else
            "negative" if blob.sentiment.polarity < -0.05 else
            "neutral"
        ),
    }


# Module-level singleton — loaded once, reused on every call
_sentiment_pipe = None


def get_sentiment_pipeline():
    """
    Load and cache the transformer sentiment pipeline.

    Model: cardiffnlp/twitter-roberta-base-sentiment-latest
    Fine-tuned on social-media text; handles irony, negation, and
    domain-specific language better than TextBlob.
    Downloaded automatically on first call (~500 MB).
    """
    global _sentiment_pipe
    if _sentiment_pipe is None:
        _sentiment_pipe = hf_pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            truncation=True,
            max_length=512,
        )
    return _sentiment_pipe


def score_sentiment_transformer(text: str) -> dict:
    """
    Score sentiment using a fine-tuned RoBERTa transformer.

    Higher accuracy than TextBlob, especially on social-media language.
    Loads the model on first call; subsequent calls are fast.

    Args:
        text: Raw or pre-cleaned input string.

    Returns:
        Dict with keys:
            label  'positive' | 'neutral' | 'negative'
            score  float confidence in [0.0, 1.0]
    """
    pipe   = get_sentiment_pipeline()
    result = pipe(clean_text(text))[0]
    return {
        "label": result["label"].lower(),
        "score": round(result["score"], 4),
    }


def score_batch_transformer(texts: list[str]) -> list[dict]:
    """
    Score a list of texts in a single batched inference call.

    Always prefer this over calling score_sentiment_transformer in a
    Python loop — batch sizes of 32-64 give the best CPU throughput.

    Args:
        texts: List of raw input strings.

    Returns:
        List of dicts, each with keys: label, score.
    """
    pipe    = get_sentiment_pipeline()
    cleaned = [clean_text(t) for t in texts]
    results = pipe(cleaned)
    return [
        {"label": r["label"].lower(), "score": round(r["score"], 4)}
        for r in results
    ]


if __name__ == "__main__":
    samples = [
        "This is absolutely outrageous. The government has failed completely.",
        "Ceasefire talks making slow but genuine progress today.",
        "Aid convoy departed this morning. No incidents reported.",
    ]
    print("--- TextBlob ---")
    for s in samples:
        r = score_sentiment_textblob(s)
        print(f"  [{r['label']:8s}  {r['polarity']:+.3f}] {s[:55]}")

    print("\n--- Transformer ---")
    text = "Absolutely devastating scenes. Words fail."
    print(f"  {score_sentiment_transformer(text)}")
