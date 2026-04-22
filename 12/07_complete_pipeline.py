"""
Chapter 12 — Example 07: A Complete Parsing Pipeline
=====================================================
Covers section 12.8:
  - Fetching a live page with requests + User-Agent
  - Parsing with BeautifulSoup + lxml
  - Cleaning noise with decompose()
  - Extracting structured data with select() and get()
  - Collecting and filtering internal links with urljoin/urlparse
  - Saving results to JSON and CSV
  - Wrapping everything in a reusable Scraper class

Install:
    pip install beautifulsoup4 lxml requests
"""

import csv
import json
import re
import time
import requests
from dataclasses import dataclass, field, asdict
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# ── Configuration ─────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

NOISE_SELECTORS = [
    "script", "style", "noscript", "iframe",
    "nav", "header", "footer", "aside",
    ".cookie-banner", ".ad", ".advertisement",
    ".sidebar", "#sidebar",
    ".social-share", ".newsletter-signup",
    ".comments", "#comments",
]

ARTICLE_SELECTORS = [
    "article",
    "div.article-body",
    "div.post-content",
    "div.entry-content",
    "div.content-body",
    "main article",
    "main",
    "div#content",
]


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class PageResult:
    url:          str
    title:        str        = ""
    description:  str        = ""
    article_text: str        = ""
    word_count:   int        = 0
    links:        list[dict] = field(default_factory=list)
    images:       list[str]  = field(default_factory=list)
    error:        str | None = None


# ── Core helpers ──────────────────────────────────────────────────────────────

def fetch(url: str, timeout: int = 10) -> requests.Response:
    """Fetch a URL, raising on HTTP errors."""
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp


def clean_soup(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove noise elements in-place. Returns the same soup."""
    for selector in NOISE_SELECTORS:
        for tag in list(soup.select(selector)):
            tag.decompose()
    return soup


def normalize_text(raw: str) -> str:
    """Collapse whitespace and remove blank lines."""
    lines = [re.sub(r" {2,}", " ", line.strip())
             for line in raw.splitlines()
             if line.strip()]
    return "\n".join(lines)


def extract_article_text(soup: BeautifulSoup) -> str:
    """Try each selector in order; fall back to <body>."""
    for selector in ARTICLE_SELECTORS:
        container = soup.select_one(selector)
        if container:
            return normalize_text(
                container.get_text(separator="\n", strip=True)
            )
    body = soup.find("body")
    return normalize_text(body.get_text(separator="\n")) if body else ""


def extract_links(soup: BeautifulSoup, base: str) -> list[dict]:
    """
    Collect all <a href> links.
    Skips fragment-only links (#...) and mailto:/tel: schemes.
    Marks links as internal or external.
    """
    base_netloc = urlparse(base).netloc
    seen = set()
    links = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue

        absolute = urljoin(base, href)
        parsed   = urlparse(absolute)

        # Normalise: remove fragment and trailing slash
        clean_url = parsed._replace(fragment="").geturl().rstrip("/")
        if clean_url in seen:
            continue
        seen.add(clean_url)

        links.append({
            "url":      clean_url,
            "text":     tag.get_text(strip=True),
            "internal": parsed.netloc == base_netloc,
            "nofollow": "nofollow" in (tag.get("rel") or []),
        })

    return links


def extract_images(soup: BeautifulSoup, base: str) -> list[str]:
    """Return absolute URLs of all images with a src attribute."""
    return [
        urljoin(base, img["src"])
        for img in soup.find_all("img", src=True)
        if img["src"].strip()
    ]


def extract_meta(soup: BeautifulSoup) -> tuple[str, str]:
    """Return (title, description) from <title> and <meta name=description>."""
    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    desc_tag = (
        soup.find("meta", attrs={"name": "description"}) or
        soup.find("meta", attrs={"property": "og:description"})
    )
    description = (desc_tag.get("content", "") if desc_tag else "").strip()
    return title, description


# ── Main scraper ─────────────────────────────────────────────────────────────

def scrape_page(url: str) -> PageResult:
    """
    Full pipeline:
      1. Fetch
      2. Parse
      3. Extract meta
      4. Clean noise
      5. Extract article text
      6. Collect links and images
    """
    result = PageResult(url=url)

    try:
        resp = fetch(url)
    except requests.exceptions.HTTPError as e:
        result.error = f"HTTP {e.response.status_code}"
        return result
    except requests.exceptions.ConnectionError:
        result.error = "Connection failed"
        return result
    except requests.exceptions.Timeout:
        result.error = "Timeout"
        return result

    soup = BeautifulSoup(resp.text, "lxml")

    # Extract before cleaning — meta tags may be in <head> which we'll strip
    result.title, result.description = extract_meta(soup)

    # Clean noise
    clean_soup(soup)

    # Article text
    result.article_text = extract_article_text(soup)
    result.word_count   = len(result.article_text.split())

    # Links and images
    result.links  = extract_links(soup, url)
    result.images = extract_images(soup, url)

    return result


# ── Batch scraper with politeness delay ──────────────────────────────────────

def scrape_batch(
    urls: list[str],
    delay: float = 1.0,
    verbose: bool = True,
) -> list[PageResult]:
    """
    Scrape multiple pages with a polite delay between requests.
    Returns a list of PageResult objects (including failed ones).
    """
    results = []
    for i, url in enumerate(urls, 1):
        if verbose:
            print(f"[{i}/{len(urls)}] {url}")
        result = scrape_page(url)
        if verbose:
            if result.error:
                print(f"  ✗ {result.error}")
            else:
                print(f"  ✓ {result.word_count} words, "
                      f"{len(result.links)} links, "
                      f"{len(result.images)} images")
        results.append(result)
        if i < len(urls):
            time.sleep(delay)    # be polite — don't hammer the server
    return results


# ── Persistence helpers ───────────────────────────────────────────────────────

def save_json(results: list[PageResult], path: str) -> None:
    """Save results to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, indent=2, ensure_ascii=False)
    print(f"Saved JSON → {path}")


def save_csv(results: list[PageResult], path: str) -> None:
    """
    Save a summary CSV (one row per page).
    Drops list fields (links, images) — save the JSON for full data.
    """
    fields = ["url", "title", "description", "word_count", "error"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow({
                **{k: getattr(r, k) for k in fields},
            })
    print(f"Saved CSV  → {path}")


# ── Demo: scrape example.com and quotes.toscrape.com ─────────────────────────

if __name__ == "__main__":

    TARGET_URLS = [
        "https://example.com",
        "https://quotes.toscrape.com",           # a scraping-friendly practice site
    ]

    print("=" * 60)
    print("RUNNING SCRAPER")
    print("=" * 60)

    results = scrape_batch(TARGET_URLS, delay=1.5, verbose=True)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    for r in results:
        print(f"\nURL         : {r.url}")
        if r.error:
            print(f"Error       : {r.error}")
            continue
        print(f"Title       : {r.title}")
        print(f"Description : {r.description[:80]}")
        print(f"Words       : {r.word_count}")
        print(f"Links       : {len(r.links)} total, "
              f"{sum(1 for l in r.links if l['internal'])} internal")
        print(f"Images      : {len(r.images)}")

        if r.article_text:
            preview = r.article_text[:200].replace("\n", " ")
            print(f"Preview     : {preview}...")

        # Show first 5 internal links
        internal = [l for l in r.links if l["internal"]][:5]
        if internal:
            print("Internal links (first 5):")
            for l in internal:
                print(f"  {l['text']:<30} {l['url']}")

    # Save output files
    save_json(results, "scrape_results.json")
    save_csv(results,  "scrape_results.csv")

    print("\n" + "=" * 60)
    print("QUOTES DEEP-DIVE (quotes.toscrape.com)")
    print("=" * 60)

    # Demonstrate structured extraction on a predictable HTML structure
    quotes_result = next((r for r in results
                          if "toscrape" in r.url and not r.error), None)
    if quotes_result:
        resp = requests.get("https://quotes.toscrape.com", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "lxml")

        quotes = []
        for div in soup.select("div.quote"):
            text   = div.select_one("span.text")
            author = div.select_one("small.author")
            tags   = div.select("a.tag")
            quotes.append({
                "text":   text.get_text(strip=True)   if text   else "",
                "author": author.get_text(strip=True) if author else "",
                "tags":   [t.get_text(strip=True) for t in tags],
            })

        print(f"Extracted {len(quotes)} quotes\n")
        for q in quotes[:3]:
            print(f"  {q['text'][:70]}")
            print(f"  — {q['author']}  [{', '.join(q['tags'])}]")
            print()
