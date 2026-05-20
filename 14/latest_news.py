"""
Parse the latest-news listing from https://www.investing.com/news/latest-news
and print each article's title and URL.

Investing.com blocks plain requests with HTTP 403. Install curl_cffi for
Chrome TLS impersonation which usually bypasses it:

    pip install curl-cffi

Usage:
    python latest_news.py
    python latest_news.py --limit 10
    python latest_news.py --json
"""
import json
import sys

import requests
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as curl_requests
    _HAVE_CURL_CFFI = True
except ImportError:
    curl_requests = None
    _HAVE_CURL_CFFI = False

URL = "https://www.investing.com/news/latest-news"
BASE = "https://www.investing.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


def _get(session, url: str, *, referer: str | None = None) -> requests.Response:
    headers = dict(HEADERS)
    if referer:
        headers["Referer"] = referer
        headers["Sec-Fetch-Site"] = "same-origin"
    if _HAVE_CURL_CFFI:
        return session.get(url, headers=headers, timeout=15, impersonate="chrome131")
    return session.get(url, headers=headers, timeout=15)


def fetch(url: str) -> str:
    session = curl_requests.Session() if _HAVE_CURL_CFFI else requests.Session()
    # warm the session on the homepage so the WAF sees a normal navigation
    _get(session, BASE + "/")
    res = _get(session, url, referer=BASE + "/")
    res.raise_for_status()
    return res.text


def parse_articles(html: str, *, debug: bool = False) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    all_anchors = soup.find_all("a", href=True)
    if debug:
        print(f"[debug] total <a> tags found: {len(all_anchors)}", file=sys.stderr)
        print("[debug] sample hrefs (first 20):", file=sys.stderr)
        for a in all_anchors[:20]:
            print(f"  {a['href']!r:60s}  text={a.get_text(strip=True)[:60]!r}", file=sys.stderr)

    articles = []
    seen = set()
    for a in all_anchors:
        href = a["href"]
        # normalise absolute URLs to path-only
        if href.startswith(BASE):
            href = href[len(BASE):]
        # article paths look like /news/<category>/<slug>-<id>
        if not href.startswith("/news/") or href.count("/") < 3:
            continue
        full_url = BASE + href.split("?")[0].split("#")[0]
        if full_url in seen:
            continue
        seen.add(full_url)
        title = a.get_text(separator=" ", strip=True)
        if not title:
            continue
        articles.append({"title": title, "url": full_url})

    if debug:
        print(f"[debug] articles matched after filter: {len(articles)}", file=sys.stderr)
        if not articles:
            print("[debug] HTML snippet (first 2000 chars):", file=sys.stderr)
            print(html[:2000], file=sys.stderr)

    return articles


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Investing.com latest-news listing.")
    parser.add_argument("--limit", type=int, default=None, help="Max articles to show.")
    parser.add_argument("--json", action="store_true", help="Output as JSON lines.")
    parser.add_argument("--debug", action="store_true", help="Print diagnostic info to stderr.")
    args = parser.parse_args()

    try:
        html = fetch(URL)
    except requests.HTTPError as exc:
        msg = f"HTTP error: {exc}"
        if getattr(exc.response, "status_code", None) == 403 and not _HAVE_CURL_CFFI:
            msg += "\nTip: install curl-cffi for Chrome TLS impersonation: pip install curl-cffi"
        print(msg, file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        sys.exit(1)

    articles = parse_articles(html, debug=args.debug)
    if args.limit:
        articles = articles[: args.limit]

    if args.json:
        for article in articles:
            print(json.dumps(article, ensure_ascii=False))
        return

    for i, article in enumerate(articles, 1):
        print(f"{i:>3}. {article['title']}")
        print(f"     {article['url']}")


if __name__ == "__main__":
    main()
