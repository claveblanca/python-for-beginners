"""
Chapter 12 — Example 05: Cleaning HTML and Extracting Text
===========================================================
Covers section 12.6:
  - .decompose() — removing noise tags in-place
  - .replace_with() — swapping a tag for its text content
  - clean_html() — stripping scripts, styles, and nav elements
  - Whitespace normalisation after get_text()
  - ARTICLE_SELECTORS fallback chain
  - Extracting structured text: headings + paragraphs as sections
  - Word count and reading-time estimate

Install:
    pip install beautifulsoup4 lxml
"""

import re
from bs4 import BeautifulSoup

# ── Realistic "noisy" page HTML ───────────────────────────────────────────────

NOISY_HTML = """
<html>
<head>
  <title>How Python Became the Language of AI</title>
  <style>
    body { font-family: Arial; } .ad { display: block; }
  </style>
</head>
<body>
  <header>
    <nav>
      <a href="/">Home</a> | <a href="/tech">Tech</a> | <a href="/ai">AI</a>
    </nav>
  </header>

  <div class="cookie-banner">
    We use cookies. <button>Accept</button> <button>Decline</button>
  </div>

  <aside class="sidebar">
    <h3>Advertisement</h3>
    <div class="ad">Buy our course — 50% off!</div>
  </aside>

  <article class="post-content">
    <h1>How Python Became the Language of AI</h1>
    <p class="byline">By <strong>Alice Chen</strong> &middot; 12 min read</p>

    <h2>A Brief History</h2>
    <p>Python was created by Guido van Rossum in 1991 with a focus on readability.
    Its clean syntax made it popular in academia long before the AI boom.</p>

    <h2>The NumPy Turning Point</h2>
    <p>The release of NumPy in 2006 gave Python the numerical foundation
    it needed to compete with MATLAB and R for scientific computing.</p>

    <p>Libraries like SciPy and Matplotlib followed, cementing Python's
    position in the scientific Python ecosystem.</p>

    <h2>Deep Learning and the Modern Era</h2>
    <p>When TensorFlow launched in 2015 and PyTorch in 2016, both chose
    Python as their primary interface. The rest is history.</p>

    <script>
      console.log("analytics ping");
      fetch("/track?page=ai-python");
    </script>

    <blockquote cite="https://source.example.com">
      "Python's simplicity is its greatest strength."
    </blockquote>
  </article>

  <section class="comments">
    <h3>Comments (42)</h3>
    <div class="comment">Great article!</div>
    <div class="comment">Very informative, thanks.</div>
  </section>

  <footer>
    <p>&copy; 2024 Tech Blog. All rights reserved.</p>
    <nav><a href="/privacy">Privacy</a> | <a href="/terms">Terms</a></nav>
  </footer>
</body>
</html>
"""


# ── 1. .decompose() — removing tags in-place ─────────────────────────────────

print("=" * 60)
print("1. .decompose() — REMOVING NOISE IN-PLACE")
print("=" * 60)

soup = BeautifulSoup(NOISY_HTML, "lxml")

# Count noise tags before removal
noise_tags = ["script", "style", "nav", "header", "footer",
              "aside", "section.comments", ".cookie-banner"]

# decompose() removes the tag AND all its contents from the tree permanently.
# Always iterate over a list() copy — modifying a live ResultSet mid-iteration
# causes elements to be skipped.
for selector in noise_tags:
    for tag in list(soup.select(selector)):
        tag.decompose()

raw_text = soup.get_text()
print(f"Characters after decompose: {len(raw_text)}")
print(f"First 200 chars:\n{raw_text[:200]}")


# ── 2. Whitespace normalisation ───────────────────────────────────────────────

print("\n" + "=" * 60)
print("2. WHITESPACE NORMALISATION")
print("=" * 60)

def normalize_text(raw: str) -> str:
    """
    Remove blank lines and normalise consecutive whitespace.
    Steps:
      1. Split into lines
      2. Strip each line
      3. Drop empty lines
      4. Collapse internal multi-spaces to one
    """
    lines = [re.sub(r" {2,}", " ", line.strip())
             for line in raw.splitlines()
             if line.strip()]
    return "\n".join(lines)


dirty = soup.get_text(separator="\n")
clean = normalize_text(dirty)
print("Cleaned text:")
print(clean)


# ── 3. clean_html() helper ────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("3. clean_html() HELPER")
print("=" * 60)

NOISE_TAGS = ["script", "style", "nav", "header", "footer",
              "aside", "iframe", "noscript", ".cookie-banner",
              ".ad", ".sidebar", ".comments", "#cookie"]

def clean_html(soup):
    """
    Remove all common noise elements from a BeautifulSoup tree in-place.
    Always pass a copy if you need the original tree intact.
    Returns the same soup object for chaining.
    """
    for selector in NOISE_TAGS:
        for tag in list(soup.select(selector)):
            tag.decompose()
    return soup


# Re-parse so we start fresh (the earlier soup was already modified)
fresh_soup = BeautifulSoup(NOISY_HTML, "lxml")
clean_soup = clean_html(fresh_soup)
body_text  = normalize_text(clean_soup.get_text(separator="\n"))
print(body_text)


# ── 4. ARTICLE_SELECTORS fallback chain ──────────────────────────────────────

print("\n" + "=" * 60)
print("4. ARTICLE SELECTOR FALLBACK CHAIN")
print("=" * 60)

# Different CMS platforms use different container elements.
# Try the most specific first; fall back to less specific ones.
ARTICLE_SELECTORS = [
    "article.post-content",   # This page
    "article",
    "div.article-body",
    "div.post-content",
    "div.entry-content",
    "main",
    "div#content",
]

def extract_article_text(html: str) -> tuple[str, str]:
    """
    Return (selector_used, clean_article_text).
    Falls back through ARTICLE_SELECTORS until one matches.
    Last resort: full body text.
    """
    soup = BeautifulSoup(html, "lxml")
    clean_html(soup)   # strip noise before extracting

    for selector in ARTICLE_SELECTORS:
        container = soup.select_one(selector)
        if container:
            text = normalize_text(container.get_text(separator="\n"))
            return selector, text

    # Last resort
    body = soup.find("body")
    if body:
        return "body (fallback)", normalize_text(body.get_text(separator="\n"))
    return "none", ""


selector_used, article_text = extract_article_text(NOISY_HTML)
print(f"Matched selector: {selector_used!r}")
print(f"Length          : {len(article_text)} characters")
print(f"\nExtracted text:\n{article_text}")


# ── 5. Structured extraction: headings + sections ────────────────────────────

print("\n" + "=" * 60)
print("5. STRUCTURED EXTRACTION: HEADINGS + SECTION TEXT")
print("=" * 60)

def extract_sections(html: str) -> list[dict]:
    """
    Split an article into sections defined by <h2> headings.
    Each section: {heading, text, word_count}
    """
    soup  = BeautifulSoup(html, "lxml")
    clean_html(soup)

    article = soup.select_one("article") or soup.find("body")
    sections = []
    current_heading = None
    current_paragraphs: list[str] = []

    for tag in article.find_all(["h1", "h2", "h3", "p", "blockquote"]):
        if tag.name in ("h1", "h2", "h3"):
            # Save previous section before starting a new one
            if current_paragraphs:
                text = " ".join(current_paragraphs)
                sections.append({
                    "heading":    current_heading or "(intro)",
                    "text":       text,
                    "word_count": len(text.split()),
                })
            current_heading    = tag.get_text(strip=True)
            current_paragraphs = []
        else:
            p = tag.get_text(separator=" ", strip=True)
            if p:
                current_paragraphs.append(p)

    # Flush the last section
    if current_paragraphs:
        text = " ".join(current_paragraphs)
        sections.append({
            "heading":    current_heading or "(intro)",
            "text":       text,
            "word_count": len(text.split()),
        })

    return sections


sections = extract_sections(NOISY_HTML)
total_words = sum(s["word_count"] for s in sections)
reading_time = max(1, round(total_words / 200))   # ~200 words per minute

print(f"Total words   : {total_words}")
print(f"Reading time  : ~{reading_time} min\n")
for s in sections:
    print(f"  [{s['word_count']:>3} words]  {s['heading']}")
    print(f"             {s['text'][:80]}...")
    print()


# ── 6. Stripping inline tags while keeping text ───────────────────────────────

print("=" * 60)
print("6. UNWRAPPING INLINE TAGS (<strong>, <em>, <a>)")
print("=" * 60)

INLINE_HTML = """
<p>
  The <strong>requests</strong> library is the <em>standard</em> way to make
  <a href="/http">HTTP calls</a> in Python. It handles <code>SSL</code>,
  redirects, and sessions <span class="note">transparently</span>.
</p>
"""

soup_inline = BeautifulSoup(INLINE_HTML, "lxml")
p = soup_inline.find("p")

# Option A: .get_text() — all text, no tags
print("get_text()         :", p.get_text(separator=" ", strip=True))

# Option B: .unwrap() each inline tag — keeps the tag's text but removes the tag itself
import copy
p_copy = copy.copy(p)
for tag in list(p_copy.find_all(["strong", "em", "code", "span", "a"])):
    tag.unwrap()   # replaces the tag with its contents in the tree
print("after .unwrap()    :", p_copy.get_text(separator=" ", strip=True))

# Option C: targeted replacement — links become "text (url)" for readability
p_copy2 = copy.copy(p)
for a in p_copy2.find_all("a"):
    href = a.get("href", "")
    a.replace_with(f"{a.get_text(strip=True)} ({href})")
print("links as text(url) :", p_copy2.get_text(separator=" ", strip=True))
