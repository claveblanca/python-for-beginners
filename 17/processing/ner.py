"""
processing/ner.py
Named Entity Recognition (NER) using spaCy.

Dependencies:
    pip install spacy
    python -m spacy download en_core_web_sm     # fast, lower accuracy
    python -m spacy download en_core_web_trf    # slow, higher accuracy
"""

import spacy
from collections import Counter

# Load model once at import time.
# Swap 'en_core_web_sm' for 'en_core_web_trf' for higher accuracy.
nlp = spacy.load('en_core_web_sm')


def extract_entities(text: str) -> list[dict]:
    """
    Extract named entities from a single text string.

    Entity labels returned by en_core_web_sm:
        PERSON   — people, including fictional
        ORG      — companies, agencies, institutions
        GPE      — geopolitical entities (countries, cities, states)
        LOC      — non-GPE locations (mountain ranges, bodies of water)
        DATE     — absolute or relative dates and periods
        PRODUCT  — vehicles, weapons, foods, etc.
        EVENT    — named events (wars, sports events, etc.)

    Args:
        text: Input string (raw or cleaned).

    Returns:
        List of dicts with keys: text, label, start, end.
    """
    doc = nlp(text[:nlp.max_length])
    return [
        {
            "text":  ent.text.strip(),
            "label": ent.label_,
            "start": ent.start_char,
            "end":   ent.end_char,
        }
        for ent in doc.ents
    ]


def entity_frequency(
    texts: list[str],
    entity_types: tuple = ('PERSON', 'ORG', 'GPE'),
) -> dict[str, Counter]:
    """
    Count entity mentions across a collection of texts.

    Aggregating NER over many posts surfaces which actors, organisations,
    and locations dominate the discourse — faster than reading every post.

    Args:
        texts:        List of input strings.
        entity_types: Entity labels to count.

    Returns:
        Dict mapping each label to a Counter of {entity_text: count}.

    Example:
        freq = entity_frequency(titles)
        for loc, count in freq['GPE'].most_common(5):
            print(f"  {loc:<20s} {count:>3d}")
    """
    counters = {t: Counter() for t in entity_types}
    for text in texts:
        for ent in extract_entities(text):
            if ent['label'] in counters:
                counters[ent['label']][ent['text']] += 1
    return counters


if __name__ == "__main__":
    sample = (
        "NATO Secretary General Jens Stoltenberg met with Ukrainian President "
        "Zelensky in Kyiv on Monday. The meeting focused on F-16 deliveries "
        "and the situation near Kharkiv."
    )
    print("--- Entities ---")
    for ent in extract_entities(sample):
        print(f"  [{ent['label']:10s}] {ent['text']}")
