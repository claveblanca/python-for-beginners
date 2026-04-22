"""
Chapter 12 — Example 03: Extracting Data from Elements
=======================================================
Covers section 12.4:
  - .text vs .get_text() — controlling separators and stripping
  - Attribute extraction: [] vs .get() with defaults
  - Extracting all links and resolving relative URLs with urljoin
  - Extracting image sources and alt text
  - Parsing an HTML table into a list of dicts
  - Structured multi-field scraping with a data class

Install:
    pip install beautifulsoup4 lxml
"""

from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# ── Sample HTML ───────────────────────────────────────────────────────────────

PAGE_HTML = """
<html>
<head><title>Tech Reviews — Home</title></head>
<body>
  <nav>
    <a href="/">Home</a>
    <a href="/reviews">Reviews</a>
    <a href="/about">About</a>
    <a name="top"></a>  <!-- anchor without href — should be skipped -->
  </nav>

  <article id="review-1">
    <h1 class="title">
      Review: <strong>MacBook Pro M3</strong>
    </h1>
    <p class="meta">
      By <span class="author">Alice Chen</span> on
      <time datetime="2024-03-15">15 March 2024</time>
    </p>
    <div class="body">
      <p>The M3 chip delivers remarkable performance improvements.</p>
      <p>Battery life exceeds Apple's stated 22-hour claim.</p>
      <figure>
        <img src="/images/mbp-front.jpg" alt="MacBook Pro front view" width="800">
        <img src="/images/mbp-side.jpg"  alt="MacBook Pro side profile" width="800">
      </figure>
    </div>
    <a href="/reviews/macbook-pro-m3" class="read-more">Read full review</a>
  </article>

  <section id="specs">
    <h2>Specifications</h2>
    <table class="specs-table">
      <thead>
        <tr><th>Component</th><th>Specification</th><th>Notes</th></tr>
      </thead>
      <tbody>
        <tr><td>CPU</td>   <td>Apple M3 Pro</td> <td>11-core</td></tr>
        <tr><td>RAM</td>   <td>18 GB</td>         <td>Unified memory</td></tr>
        <tr><td>Storage</th><td>512 GB SSD</td>   <td>PCIe 4.0</td></tr>
        <tr><td>Display</td><td>14.2-inch</td>    <td>Liquid Retina XDR</td></tr>
        <tr><td>Battery</td><td>70 Wh</td>        <td>22 hrs rated</td></tr>
      </tbody>
    </table>
  </section>

  <section id="related">
    <h2>Related Articles</h2>
    <ul>
      <li><a href="/reviews/imac-m3">iMac M3 Review</a></li>
      <li><a href="https://apple.com/macbook-pro" rel="nofollow">Apple official page</a></li>
      <li><a href="/reviews/macbook-air-m2">MacBook Air M2 Review</a></li>
    </ul>
  </section>

  <footer>
    <p>&copy; 2024 Tech Reviews. <a href="/privacy">Privacy policy</a>.</p>
  </footer>
</body>
</html>
"""

BASE_URL = "https://techreviews.example.com"
soup     = BeautifulSoup(PAGE_HTML, "lxml")


# ── 1. .text vs .get_text() ──────────────────────────────────────────────────

print("=" * 60)
print("1. .text vs .get_text()")
print("=" * 60)

title_tag = soup.find("h1", class_="title")

# .text concatenates all text nodes without any separator
print(f".text (raw)              : {repr(title_tag.text)}")

# .get_text(separator) inserts a string between each text piece
print(f".get_text(sep=' ')       : {repr(title_tag.get_text(separator=' '))}")

# strip=True removes leading/trailing whitespace from each text piece
print(f".get_text(sep=' ', strip): {repr(title_tag.get_text(separator=' ', strip=True))}")

# .strings returns a generator of individual text nodes
print(f".strings                 : {list(title_tag.strings)}")

# .stripped_strings skips blank/whitespace-only strings
print(f".stripped_strings        : {list(title_tag.stripped_strings)}")


# ── 2. Safe attribute access ──────────────────────────────────────────────────

print("\n" + "=" * 60)
print("2. ATTRIBUTE EXTRACTION")
print("=" * 60)

img = soup.find("img")

# Square bracket access — raises KeyError if attribute is absent
print(f"img['src']               : {img['src']}")
print(f"img['alt']               : {img['alt']}")

# .get() — returns None (or a default) if attribute is absent
print(f"img.get('src')           : {img.get('src')}")
print(f"img.get('loading')       : {img.get('loading')}")          # not present → None
print(f"img.get('loading', 'lazy'): {img.get('loading', 'lazy')}") # with default

# Multi-valued attributes (class) are returned as a list
review = soup.find("article")
print(f"\narticle['id']            : {review['id']}")

# datetime attribute on <time> — semantic date in machine-readable format
time_tag = soup.find("time")
print(f"<time> human text        : {time_tag.text}")
print(f"<time> datetime attr     : {time_tag.get('datetime')}")


# ── 3. Extracting all links ───────────────────────────────────────────────────

print("\n" + "=" * 60)
print("3. LINK EXTRACTION WITH urljoin")
print("=" * 60)

def extract_links(soup, base: str) -> list[dict]:
    """
    Return all <a href> links on the page.
    Resolves relative paths to absolute URLs.
    Skips anchor-only tags (href="#..." or missing href).
    """
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if href.startswith("#"):        # skip pure fragment links
            continue
        absolute = urljoin(base, href)
        parsed   = urlparse(absolute)
        links.append({
            "text":     tag.get_text(strip=True),
            "url":      absolute,
            "domain":   parsed.netloc,
            "external": parsed.netloc != urlparse(base).netloc,
            "nofollow": "nofollow" in tag.get("rel", []),
        })
    return links


all_links = extract_links(soup, BASE_URL)
print(f"Total links found: {len(all_links)}\n")
print(f"{'Text':<35} {'External':<10} {'URL'}")
print("-" * 80)
for link in all_links:
    ext = "EXTERNAL" if link["external"] else "internal"
    print(f"{link['text']:<35} {ext:<10} {link['url']}")

# Filter to internal links only
internal = [l for l in all_links if not l["external"]]
print(f"\nInternal links: {len(internal)}")


# ── 4. Extracting images ──────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("4. IMAGE EXTRACTION")
print("=" * 60)

def extract_images(soup, base: str) -> list[dict]:
    """Return all images with their resolved src and alt text."""
    images = []
    for img in soup.find_all("img", src=True):   # src=True skips <img> without src
        images.append({
            "src":    urljoin(base, img["src"]),
            "alt":    img.get("alt", ""),
            "width":  img.get("width"),
        })
    return images


for img in extract_images(soup, BASE_URL):
    print(f"  src   : {img['src']}")
    print(f"  alt   : {img['alt']}")
    print(f"  width : {img['width']}px")
    print()


# ── 5. Parsing an HTML table ──────────────────────────────────────────────────

print("=" * 60)
print("5. HTML TABLE → LIST OF DICTS")
print("=" * 60)

def parse_table(table_tag) -> list[dict]:
    """
    Convert an HTML <table> into a list of dicts.
    The first row is treated as headers.
    Works for tables with <thead>/<tbody> or plain <tr> rows.
    """
    rows    = table_tag.find_all("tr")
    headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
    records = []
    for row in rows[1:]:
        cells  = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
        if len(cells) == len(headers):
            records.append(dict(zip(headers, cells)))
    return records


specs_table = soup.find("table", class_="specs-table")
specs       = parse_table(specs_table)

print(f"{'Component':<12} {'Specification':<20} {'Notes'}")
print("-" * 50)
for row in specs:
    print(f"{row['Component']:<12} {row['Specification']:<20} {row['Notes']}")


# ── 6. Structured extraction into a dataclass ─────────────────────────────────

print("\n" + "=" * 60)
print("6. STRUCTURED EXTRACTION INTO A DATACLASS")
print("=" * 60)

@dataclass
class ArticleData:
    title:    str
    author:   str
    date:     str          # ISO date from datetime attribute
    images:   list[str] = field(default_factory=list)
    read_more: str | None  = None


def extract_article(soup, base: str) -> ArticleData:
    article = soup.find("article")

    title  = article.find("h1", class_="title")
    author = article.find("span", class_="author")
    time   = article.find("time")
    images = [urljoin(base, img["src"]) for img in article.find_all("img", src=True)]
    more   = article.find("a", class_="read-more")

    return ArticleData(
        title     = title.get_text(separator=" ", strip=True) if title  else "",
        author    = author.text.strip()                        if author else "",
        date      = time.get("datetime", time.text)            if time   else "",
        images    = images,
        read_more = urljoin(base, more["href"])                if more   else None,
    )


article = extract_article(soup, BASE_URL)
print(f"Title     : {article.title}")
print(f"Author    : {article.author}")
print(f"Date      : {article.date}")
print(f"Images    : {article.images}")
print(f"Read more : {article.read_more}")
