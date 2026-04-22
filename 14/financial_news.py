"""
Fetch Investing.com latest news listing and load full text for each article.

The site often returns HTTP 403 to plain ``requests``. This script uses a normal
browser header set, warms the session on the homepage, and uses ``curl-cffi``
(Chrome TLS impersonation) when installed — install with:

    pip install curl-cffi

Usage:
    python financial.py                         # latest-news listing (single page)
    python financial.py --category stock-market-news   # URLs from news_stock_market sitemap (default)
    python financial.py --category stock-market-news --use-listing-pages   # HTML pagination instead
    python financial.py --sitemap-url URL       # custom sitemap (index or urlset)
    python financial.py --delay 1.5             # seconds between article fetches
    python financial.py --limit 5               # only first N articles (after URLs collected)
    python financial.py --json                  # one JSON object per line to stdout
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from typing import Callable, Iterator
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as curl_requests

    _HAVE_CURL_CFFI = True
except ImportError:
    curl_requests = None  # type: ignore[assignment]
    _HAVE_CURL_CFFI = False

LIST_URL = "https://www.investing.com/news/latest-news"
BASE = "https://www.investing.com"
STOCK_MARKET_SITEMAP_URL = "https://www.investing.com/news_stock_market_sitemap.xml"

# Investing.com often returns 403 to bare clients; these mimic a current Chrome fetch.
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
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

# TLS fingerprint that matches Chrome (often avoids 403 when plain requests is blocked).
_CFFI_IMPERSONATE = "chrome131"

# /news/<category>/<slug>-<article_id>
_ARTICLE_PATH = re.compile(r"^/news/[^/]+/[^/]+-\d+$")


def _new_session() -> requests.Session:
    if _HAVE_CURL_CFFI:
        return curl_requests.Session()  # type: ignore[union-attr]
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def _http_get(session: requests.Session, url: str, *, referer: str | None) -> requests.Response:
    h = dict(HEADERS)
    if referer:
        h["Referer"] = referer
        h["Sec-Fetch-Site"] = "same-origin"
    else:
        h["Sec-Fetch-Site"] = "none"
    if _HAVE_CURL_CFFI:
        return session.get(  # type: ignore[union-attr]
            url,
            headers=h,
            timeout=30,
            impersonate=_CFFI_IMPERSONATE,
        )
    return session.get(url, headers=h, timeout=30)


def _warm_session(session: requests.Session) -> None:
    """Load homepage first so cookies / WAF sees a normal navigation."""
    _http_get(session, f"{BASE}/", referer=None)


def _normalize_href(href: str) -> str:
    href = href.split("#", 1)[0].split("?", 1)[0]
    return href


def is_news_article_url(url: str) -> bool:
    try:
        p = urlparse(url)
        if p.netloc not in ("www.investing.com", "investing.com"):
            return False
        path = p.path.rstrip("/") or "/"
        return bool(_ARTICLE_PATH.match(path))
    except Exception:
        return False


def fetch_listing_html(session: requests.Session) -> str:
    _warm_session(session)
    res = _http_get(session, LIST_URL, referer=f"{BASE}/")
    res.raise_for_status()
    return res.text


def _category_first_page_url(category_slug: str) -> str:
    return f"{BASE}/news/{category_slug.strip().strip('/')}"


def _category_listing_page_url(category_slug: str, page: int) -> str:
    base = _category_first_page_url(category_slug)
    if page <= 1:
        return base
    return f"{base}/{page}"


def parse_max_listing_page(html: str, category_slug: str) -> int:
    """Largest page number found in pagination links (at least 1)."""
    cat = category_slug.strip().strip("/")
    page_link = re.compile(rf"/news/{re.escape(cat)}/(\d+)(?:/|$)")
    soup = BeautifulSoup(html, "html.parser")
    nums: list[int] = []
    for a in soup.find_all("a", href=True):
        raw = _normalize_href(a["href"])
        full = urljoin(BASE, raw)
        path = urlparse(full).path
        m = page_link.search(path)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else 1


def collect_category_article_links(html: str, category_slug: str) -> list[tuple[str, str]]:
    """Article links that belong to /news/<category_slug>/… only."""
    cat = category_slug.strip().strip("/")
    prefix_path = f"/news/{cat}/"
    soup = BeautifulSoup(html, "html.parser")
    seen: dict[str, str] = {}
    for a in soup.find_all("a", href=True):
        raw = _normalize_href(a["href"])
        full = urljoin(BASE, raw)
        try:
            path = urlparse(full).path
        except Exception:
            continue
        if not path.startswith(prefix_path):
            continue
        if not is_news_article_url(full):
            continue
        title = a.get_text(separator=" ", strip=True)
        if not title:
            continue
        if full not in seen:
            seen[full] = title
    return list(seen.items())


def _sitemap_child_elements(root: ET.Element) -> list[ET.Element]:
    """Children ignoring XML namespace prefix."""
    return [c for c in list(root) if isinstance(c.tag, str)]


def _tag_local(tag: str) -> str:
    return tag.rpartition("}")[2] if "}" in tag else tag


def fetch_urls_from_sitemap(
    session: requests.Session,
    sitemap_url: str,
    *,
    listing_delay: float,
    url_keep: Callable[[str], bool] | None = None,
) -> tuple[list[tuple[str, str]], str]:
    """
    Download a sitemap index and/or urlset(s), return (url, title) pairs.
    Title is taken from XML when present (e.g. nested title); otherwise empty (filled from HTML later).
    """
    _warm_session(session)
    queue: list[str] = [sitemap_url]
    seen_maps: set[str] = set()
    pairs: list[tuple[str, str]] = []
    seen_urls: set[str] = set()
    first_fetch = True

    while queue:
        u = queue.pop(0)
        if u in seen_maps:
            continue
        seen_maps.add(u)
        if not first_fetch and listing_delay > 0:
            time.sleep(listing_delay)
        first_fetch = False
        res = _http_get(session, u, referer=f"{BASE}/")
        res.raise_for_status()
        root = ET.fromstring(res.content)
        local = _tag_local(root.tag)
        if local == "sitemapindex":
            for sm in _sitemap_child_elements(root):
                if _tag_local(sm.tag) != "sitemap":
                    continue
                for el in _sitemap_child_elements(sm):
                    if _tag_local(el.tag) == "loc" and el.text:
                        queue.append(el.text.strip())
        elif local == "urlset":
            for item in _sitemap_child_elements(root):
                if _tag_local(item.tag) != "url":
                    continue
                loc_text: str | None = None
                title_text = ""
                for el in item.iter():
                    if not isinstance(el.tag, str):
                        continue
                    ln = _tag_local(el.tag)
                    if ln == "loc" and el.text:
                        loc_text = el.text.strip()
                    elif ln == "title" and el.text and el.text.strip():
                        title_text = el.text.strip()
                if not loc_text:
                    continue
                if url_keep is not None and not url_keep(loc_text):
                    continue
                if loc_text in seen_urls:
                    continue
                seen_urls.add(loc_text)
                pairs.append((loc_text, title_text))
        else:
            raise ValueError(f"Unknown sitemap root: {root.tag!r}")

    return pairs, sitemap_url


def gather_category_article_pairs(
    session: requests.Session,
    category_slug: str,
    *,
    listing_delay: float,
    max_listing_pages: int | None,
) -> tuple[list[tuple[str, str]], str]:
    """
    Fetch every listing page for a category (e.g. stock-market-news) and return
    unique (url, title) pairs plus the referer URL to use for article requests.
    """
    _warm_session(session)
    cat = category_slug.strip().strip("/")
    first_url = _category_first_page_url(cat)
    res = _http_get(session, first_url, referer=f"{BASE}/")
    res.raise_for_status()
    html = res.text

    seen: dict[str, str] = {}

    def merge(page_html: str) -> None:
        for url, title in collect_category_article_links(page_html, cat):
            if url not in seen:
                seen[url] = title

    merge(html)

    max_p = parse_max_listing_page(html, cat)
    if max_listing_pages is not None:
        max_p = min(max_p, max_listing_pages)

    if max_p <= 1:
        page = 2
        while True:
            if max_listing_pages is not None and page > max_listing_pages:
                break
            if listing_delay > 0:
                time.sleep(listing_delay)
            res = _http_get(session, _category_listing_page_url(cat, page), referer=first_url)
            if res.status_code != 200:
                break
            before = len(seen)
            merge(res.text)
            if len(seen) == before:
                break
            page += 1
    else:
        for page in range(2, max_p + 1):
            if max_listing_pages is not None and page > max_listing_pages:
                break
            if listing_delay > 0:
                time.sleep(listing_delay)
            res = _http_get(session, _category_listing_page_url(cat, page), referer=first_url)
            if res.status_code != 200:
                break
            merge(res.text)

    return list(seen.items()), first_url


@dataclass
class NewsArticle:
    url: str
    title: str
    content: str
    published: str | None = None
    error: str | None = None


def collect_listing_links(html: str) -> list[tuple[str, str]]:
    """Return ordered unique (url, title) pairs from the latest-news page."""
    soup = BeautifulSoup(html, "html.parser")
    seen: dict[str, str] = {}
    for a in soup.find_all("a", href=True):
        raw = _normalize_href(a["href"])
        full = urljoin(BASE, raw)
        if not is_news_article_url(full):
            continue
        title = a.get_text(separator=" ", strip=True)
        if not title:
            continue
        if full not in seen:
            seen[full] = title
    return list(seen.items())


def _strip_noise(node) -> None:
    for sel in (
        "script",
        "style",
        "nav",
        "iframe",
        "form",
        ".socialShare",
        "[data-test='article-comments']",
        ".commentSection",
    ):
        for el in node.select(sel):
            el.decompose()


def extract_article_html(soup: BeautifulSoup) -> str | None:
    for selector in (
        "div#article",
        "div.articlePage",
        "div#articleText",
        "div[data-test='article-content']",
        "div.article-WYSIWYG",
        "article",
    ):
        node = soup.select_one(selector)
        if not node:
            continue
        _strip_noise(node)
        text = node.get_text(separator="\n", strip=True)
        if len(text) > 80:
            return text
    og = soup.find("meta", property="og:description")
    if og and og.get("content"):
        return og["content"].strip()
    return None


def _published_from_span(soup: BeautifulSoup) -> str | None:
    """
    Investing.com shows e.g. ``Published 04/10/2026, 02:00 PM`` inside a <span>
    (byline row under the headline).
    """
    for span in soup.find_all("span"):
        text = span.get_text(separator=" ", strip=True)
        if not text:
            continue
        m = re.match(r"^Published\s+(.+)$", text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def extract_published_date(soup: BeautifulSoup) -> str | None:
    """Publish time from meta / structured data (often ISO 8601), else visible span."""
    for prop in (
        "article:published_time",
        "article:modified_time",
        "og:updated_time",
        "og:published_time",
    ):
        m = soup.find("meta", property=prop)
        if m and m.get("content"):
            return m["content"].strip()
    for name in ("date", "pubdate", "publishdate", "sailthru.date"):
        m = soup.find("meta", attrs={"name": name})
        if m and m.get("content"):
            return m["content"].strip()
    meta = soup.find("meta", attrs={"itemprop": "datePublished"})
    if meta and meta.get("content"):
        return meta["content"].strip()
    for t in soup.find_all("time"):
        dt = t.get("datetime")
        if dt:
            return dt.strip()
    span = soup.find(attrs={"itemprop": "datePublished"})
    if span is not None:
        if span.get("datetime"):
            return span["datetime"].strip()
        if span.get("content"):
            return span["content"].strip()
        text = span.get_text(strip=True)
        if text:
            return text
    return _published_from_span(soup)


def fetch_article(
    session: requests.Session,
    url: str,
    list_title: str,
    *,
    referer: str | None = None,
) -> NewsArticle:
    try:
        res = _http_get(session, url, referer=referer if referer is not None else LIST_URL)
        if res.status_code != 200:
            return NewsArticle(
                url=url,
                title=list_title,
                content="",
                error=f"HTTP {res.status_code}",
            )
        soup = BeautifulSoup(res.text, "html.parser")
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else list_title
        published = extract_published_date(soup)
        content = extract_article_html(soup) or ""
        if not content:
            return NewsArticle(
                url=url,
                title=title,
                content="",
                published=published,
                error="Could not extract article body",
            )
        return NewsArticle(
            url=url,
            title=title,
            content=content,
            published=published,
        )
    except requests.RequestException as exc:
        return NewsArticle(url=url, title=list_title, content="", error=str(exc))


def _stock_market_sitemap_filter(url: str) -> bool:
    if not is_news_article_url(url):
        return False
    path = urlparse(url).path
    return path.startswith("/news/stock-market-news/")


def iter_latest_news(
    session: requests.Session,
    *,
    delay: float,
    limit: int | None,
    category_slug: str | None,
    listing_delay: float,
    max_listing_pages: int | None,
    sitemap_url: str | None,
    use_listing_pages: bool,
) -> Iterator[NewsArticle]:
    if sitemap_url:
        pairs, list_referer = fetch_urls_from_sitemap(
            session,
            sitemap_url,
            listing_delay=listing_delay,
            url_keep=is_news_article_url,
        )
    elif category_slug == "stock-market-news" and not use_listing_pages:
        pairs, list_referer = fetch_urls_from_sitemap(
            session,
            STOCK_MARKET_SITEMAP_URL,
            listing_delay=listing_delay,
            url_keep=_stock_market_sitemap_filter,
        )
    elif category_slug:
        pairs, list_referer = gather_category_article_pairs(
            session,
            category_slug,
            listing_delay=listing_delay,
            max_listing_pages=max_listing_pages,
        )
    else:
        html = fetch_listing_html(session)
        pairs = collect_listing_links(html)
        list_referer = LIST_URL
    if limit is not None:
        pairs = pairs[:limit]
    for i, (url, list_title) in enumerate(pairs):
        if i > 0 and delay > 0:
            time.sleep(delay)
        yield fetch_article(session, url, list_title, referer=list_referer)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Investing.com latest news articles.")
    parser.add_argument(
        "--category",
        default=None,
        metavar="SLUG",
        help=(
            'Category under /news/<slug>/ (e.g. "stock-market-news"). '
            "Default for stock-market-news: URLs from news_stock_market sitemap; "
            "use --use-listing-pages for HTML pagination."
        ),
    )
    parser.add_argument(
        "--sitemap-url",
        default=None,
        metavar="URL",
        help=(
            "Fetch article URLs from this sitemap (sitemap index or urlset). "
            "Overrides --category URL discovery when set."
        ),
    )
    parser.add_argument(
        "--use-listing-pages",
        action="store_true",
        help=(
            "With --category stock-market-news, crawl HTML listing pages instead of "
            f"{STOCK_MARKET_SITEMAP_URL}."
        ),
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        metavar="N",
        help="With --category (HTML mode), stop after at most N listing pages (default: all).",
    )
    parser.add_argument(
        "--listing-delay",
        type=float,
        default=0.35,
        help="Seconds between sitemap / listing page requests (default: 0.35).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds to wait between article requests (default: 1.0).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of articles to fetch (default: no limit).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print each article as one JSON line.",
    )
    args = parser.parse_args()

    session = _new_session()
    try:
        articles = list(
            iter_latest_news(
                session,
                delay=args.delay,
                limit=args.limit,
                category_slug=args.category,
                listing_delay=args.listing_delay,
                max_listing_pages=args.max_pages,
                sitemap_url=args.sitemap_url,
                use_listing_pages=args.use_listing_pages,
            )
        )
    except requests.HTTPError as exc:
        err = f"Failed to load listing: {exc}"
        if (
            getattr(exc.response, "status_code", None) == 403
            and not _HAVE_CURL_CFFI
        ):
            err += (
                "\nTip: install curl-cffi for browser-like TLS (pip install curl-cffi), "
                "then run again."
            )
        print(err, file=sys.stderr)
        sys.exit(1)
    except (requests.RequestException, ValueError) as exc:
        print(f"Failed to load listing or sitemap: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        for a in articles:
            print(json.dumps(asdict(a), ensure_ascii=False))
        return

    for a in articles:
        print("=" * 72)
        print(a.title)
        if a.published:
            print(f"Published: {a.published}")
        print(a.url)
        if a.error:
            print(f"[{a.error}]")
        else:
            print()
            print(a.content)
        print()


if __name__ == "__main__":
    main()
