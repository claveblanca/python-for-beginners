"""
processing/cleaning.py
Text cleaning and emoji handling for raw social-media text.

Dependencies:
    pip install emoji
"""

import re
import html
import emoji as emoji_lib

# Compiled regex patterns — compiled once at import, reused on every call
RE_URL       = re.compile(r'https?://\S+')
RE_MENTION   = re.compile(r'u/\w+')
RE_SUBREDDIT = re.compile(r'r/\w+')
RE_MARKDOWN  = re.compile(r'[*_~`#>│]+')
RE_NEWLINE   = re.compile(r'\s+')
RE_EMOJI     = re.compile(
    '[\U0001F600-\U0001F64F'
    '\U0001F300-\U0001F5FF'
    '\U0001F680-\U0001F6FF'
    '\U0001F1E0-\U0001F1FF]+',
    flags=re.UNICODE,
)


def clean_text(text: str, keep_emoji: bool = False) -> str:
    """
    Normalise raw Reddit post / comment text.

    Steps applied in order:
        1. Unescape HTML entities  (&amp; &gt; etc.)
        2. Strip URLs
        3. Strip u/username mentions
        4. Strip r/subreddit links
        5. Strip Markdown syntax characters
        6. Remove emoji (unless keep_emoji=True)
        7. Collapse whitespace

    Args:
        text:       Raw input string.
        keep_emoji: Set True to preserve emoji characters in output.

    Returns:
        Cleaned, lowercased string.
    """
    text = html.unescape(text)
    text = RE_URL.sub('', text)
    text = RE_MENTION.sub('', text)
    text = RE_SUBREDDIT.sub('', text)
    text = RE_MARKDOWN.sub(' ', text)
    if not keep_emoji:
        text = RE_EMOJI.sub('', text)
    text = RE_NEWLINE.sub(' ', text)
    return text.strip().lower()


def demojize(text: str) -> str:
    """
    Replace Unicode emoji with descriptive text tokens.

    Preserves sentiment signal from emoji in a form that text
    classifiers can process.

    Example:
        "Great news! 🎉"  →  "Great news!  :party_popper: "

    Args:
        text: Raw string, may contain Unicode emoji.

    Returns:
        String with emoji replaced by :descriptor: tokens.
    """
    return emoji_lib.demojize(text, delimiters=(' :', ': '))


if __name__ == "__main__":
    samples = [
        'Check this out! **https://example.com** u/analyst123 🔥🔥',
        'r/worldnews &gt; breaking: major escalation confirmed!!!',
        'Great news! 🎉 The ceasefire is holding 🕊️ #peace',
    ]
    print("--- clean_text ---")
    for t in samples[:2]:
        print(repr(clean_text(t)))

    print("\n--- demojize ---")
    print(demojize(samples[2]))
