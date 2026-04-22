"""
Chapter 12 — Example 01: The DOM and Basic Parsing
====================================================
Covers sections 12.1 and 12.2:
  - Understanding HTML as a tree (DOM)
  - Parsing HTML strings with BeautifulSoup + lxml
  - Accessing tags, text, and attributes directly
  - Fetching and parsing a live web page

Install:
    pip install beautifulsoup4 lxml requests
"""

import requests
from bs4 import BeautifulSoup

# ── Section 12.1  The DOM — HTML as a Tree ────────────────────────────────────

# This snippet represents a typical article structure found on news sites.
# The <article> is the root; it has four direct children.
ARTICLE_HTML = """
<article>
    <h1 class="title">Python for Data Science</h1>
    <p class="byline">By Alice Smith</p>
    <p class="summary">Python has become the language of choice for data scientists
    thanks to its readable syntax and rich ecosystem.</p>
    <a href="/topics/python">More on Python</a>
</article>
"""

print("=" * 60)
print("1. PARSING AN HTML STRING")
print("=" * 60)

soup = BeautifulSoup(ARTICLE_HTML, "lxml")

# Dot-notation shortcut: soup.tagname → first matching tag
print("\n--- soup.h1 (full tag) ---")
print(soup.h1)

print("\n--- soup.h1.text (text only) ---")
print(soup.h1.text)

print("\n--- soup.h1['class'] (attribute access) ---")
print(soup.h1["class"])          # returns a list — CSS classes are multi-valued

print("\n--- soup.a['href'] ---")
print(soup.a["href"])

print("\n--- soup.p (first <p> only) ---")
print(soup.p.text)


# ── Section 12.2  Parsing a Live Web Page ────────────────────────────────────

print("\n" + "=" * 60)
print("2. FETCHING AND PARSING A LIVE PAGE")
print("=" * 60)

# Always include a User-Agent — many servers reject bare Python/requests calls.
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Chapter12Bot/1.0)"}
URL     = "https://example.com"

try:
    response = requests.get(URL, headers=HEADERS, timeout=10)
    response.raise_for_status()          # raises on 4xx / 5xx

    live_soup = BeautifulSoup(response.text, "lxml")

    print(f"\nPage title  : {live_soup.title.text.strip()}")
    print(f"Status code : {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")

    # Count top-level elements inside <body>
    body_children = [t for t in live_soup.body.children
                     if hasattr(t, "name") and t.name]
    print(f"Body child elements: {[t.name for t in body_children]}")

except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except requests.exceptions.ConnectionError:
    print("Could not reach the server — check your internet connection.")
except requests.exceptions.Timeout:
    print("Request timed out after 10 seconds.")


# ── Inspecting the parsed tree ────────────────────────────────────────────────

print("\n" + "=" * 60)
print("3. INSPECTING THE PARSED TREE")
print("=" * 60)

COMPLEX_HTML = """
<html>
<head><title>Demo Page</title></head>
<body>
  <header><nav><a href="/">Home</a><a href="/about">About</a></nav></header>
  <main>
    <article id="post-1">
      <h1 class="post-title">Understanding BeautifulSoup</h1>
      <div class="meta">
        <span class="author">Jane Doe</span>
        <span class="date">2024-03-15</span>
      </div>
      <div class="body">
        <p>BeautifulSoup parses HTML into a tree of Python objects.</p>
        <p>Each tag, attribute, and text node becomes a Python object.</p>
      </div>
    </article>
  </main>
  <footer><p>&copy; 2024 Demo Site</p></footer>
</body>
</html>
"""

page = BeautifulSoup(COMPLEX_HTML, "lxml")

# .name gives the tag name; .string gives text if there is exactly one text node
print(f"Document title : {page.title.string}")
print(f"Article id     : {page.article['id']}")
print(f"Author         : {page.find('span', class_='author').text}")
print(f"Post date      : {page.find('span', class_='date').text}")

# soup.prettify() returns the tree as indented HTML — useful for debugging
print("\n--- prettified article (first 400 chars) ---")
print(page.article.prettify()[:400])
