"""
Read article URLs from output.txt, fetch each page, and run sentiment analysis.

Usage:
    python news_sentiment.py                    # reads output.txt in same folder
    python news_sentiment.py -i output.txt
    python news_sentiment.py -i output.txt -o results.json
"""
import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from transformers import pipeline

try:
    from curl_cffi import requests as curl_requests
    _HAVE_CURL_CFFI = True
except ImportError:
    curl_requests = None
    _HAVE_CURL_CFFI = False

BASE = "https://www.investing.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Upgrade-Insecure-Requests": "1",
}

# sentiment model — loaded once
print("Loading sentiment model...", file=sys.stderr)
_sentiment = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    top_k=None,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_session():
    if _HAVE_CURL_CFFI:
        s = curl_requests.Session()
    else:
        s = requests.Session()
    # warm session so WAF sees a normal navigation
    _get(s, BASE + "/")
    return s


def _get(session, url: str) -> requests.Response:
    kwargs = dict(headers=HEADERS, timeout=20)
    if _HAVE_CURL_CFFI:
        kwargs["impersonate"] = "chrome131"
    return session.get(url, **kwargs)


def parse_output_file(path: Path) -> list[dict]:
    """Parse lines like '  1. Title\\n     URL' from latest_news.py output."""
    entries = []
    lines = path.read_text(encoding="utf-8").splitlines()
    title = None
    for line in lines:
        # numbered title line: "  1. Some Title"
        m = re.match(r"^\s+\d+\.\s+(.+)$", line)
        if m:
            title = m.group(1).strip()
            continue
        # URL line following a title
        url = line.strip()
        if title and url.startswith("http"):
            entries.append({"title": title, "url": url})
            title = None
    return entries


def fetch_article_text(session, url: str) -> str:
    """Fetch a page and return the text content of div#article."""
    try:
        res = _get(session, url)
        if res.status_code != 200:
            print(f"  [HTTP {res.status_code}] {url}", file=sys.stderr)
            return ""
        soup = BeautifulSoup(res.text, "html.parser")
        body = soup.find("div", id="article")
        if not body:
            print(f"  [warn] div#article not found in {url}", file=sys.stderr)
            return ""
        return body.get_text(separator=" ", strip=True)
    except Exception as exc:
        print(f"  [fetch error] {exc}", file=sys.stderr)
        return ""


def analyze(text: str) -> dict:
    """Run sentiment on up to 512 chars of text."""
    text = text.strip()[:512]
    if not text:
        return {"label": "empty", "confidence": 0.0}
    raw = _sentiment(text)[0]
    top = max(raw, key=lambda x: x["score"])
    return {
        "label": top["label"].lower(),
        "confidence": round(top["score"], 4),
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Sentiment analysis on news articles.")
    parser.add_argument("-i", "--input", default="output.txt", metavar="FILE",
                        help="Input file from latest_news.py (default: output.txt)")
    parser.add_argument("-o", "--output", default=None, metavar="FILE",
                        help="Write JSON results to FILE (default: print to stdout)")
    args = parser.parse_args()

    entries = parse_output_file(Path(args.input))
    if not entries:
        print("No articles found in input file.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(entries)} article(s). Fetching...", file=sys.stderr)
    session = _make_session()
    results = []

    for i, entry in enumerate(entries, 1):
        print(f"[{i}/{len(entries)}] {entry['title']}", file=sys.stderr)
        body = fetch_article_text(session, entry["url"])
        if not body:
            print("  [skip] no article body — skipping sentiment", file=sys.stderr)
            results.append({
                "title": entry["title"],
                "url": entry["url"],
                "sentiment": "unavailable",
                "confidence": 0.0,
                "body_fetched": False,
                "text": "",
            })
            continue
        sentiment = analyze(body)
        results.append({
            "title": entry["title"],
            "url": entry["url"],
            "sentiment": sentiment["label"],
            "confidence": sentiment["confidence"],
            "body_fetched": True,
            "text": body,
        })
        label = sentiment["label"].upper()
        conf = sentiment["confidence"]
        print(f"  → {label}  ({conf:.0%})", file=sys.stderr)

    if args.output:
        Path(args.output).write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\nWrote {len(results)} result(s) to {args.output}", file=sys.stderr)
    else:
        print()
        for r in results:
            bar = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}.get(r["sentiment"], "⚪")
            print(f"{bar}  [{r['sentiment'].upper():8s} {r['confidence']:.0%}]  {r['title']}")


if __name__ == "__main__":
    main()
