"""
Chapter 12 — Example 06: lxml and XPath
========================================
Covers section 12.7:
  - Parsing with lxml directly (html.fromstring)
  - XPath syntax: //, /, @, [], text(), contains()
  - XPath vs CSS selectors — choosing the right tool
  - Using lxml as BeautifulSoup's parser for speed
  - Performance comparison: html.parser vs lxml vs lxml-direct

Install:
    pip install lxml beautifulsoup4
"""

import time
from lxml import html as lhtml
from lxml import etree
from bs4 import BeautifulSoup

# ── Sample HTML ───────────────────────────────────────────────────────────────

CATALOGUE_HTML = """
<html>
<body>
  <nav id="main-nav">
    <a href="/">Home</a>
    <a href="/books">Books</a>
    <a href="/courses">Courses</a>
  </nav>

  <main>
    <h1>Python Learning Resources</h1>

    <section id="books">
      <h2>Books</h2>
      <ul class="resource-list">
        <li class="resource book" data-id="b1" data-level="beginner">
          <h3><a href="/books/automate">Automate the Boring Stuff</a></h3>
          <span class="author">Al Sweigart</span>
          <span class="price free">Free online</span>
          <span class="rating" data-score="4.8">★★★★★</span>
        </li>
        <li class="resource book" data-id="b2" data-level="intermediate">
          <h3><a href="/books/fluent">Fluent Python</a></h3>
          <span class="author">Luciano Ramalho</span>
          <span class="price">£45.99</span>
          <span class="rating" data-score="4.9">★★★★★</span>
        </li>
        <li class="resource book" data-id="b3" data-level="advanced">
          <h3><a href="/books/cpython">CPython Internals</a></h3>
          <span class="author">Anthony Shaw</span>
          <span class="price">£35.00</span>
          <span class="rating" data-score="4.7">★★★★☆</span>
        </li>
      </ul>
    </section>

    <section id="courses">
      <h2>Courses</h2>
      <ul class="resource-list">
        <li class="resource course" data-id="c1" data-level="beginner">
          <h3><a href="/courses/cs50p">CS50P — Python</a></h3>
          <span class="author">Harvard / David Malan</span>
          <span class="price free">Free</span>
          <span class="rating" data-score="4.9">★★★★★</span>
        </li>
        <li class="resource course" data-id="c2" data-level="intermediate">
          <h3><a href="/courses/fast-api">FastAPI Full Course</a></h3>
          <span class="author">Sebastián Ramírez</span>
          <span class="price">£19.99</span>
          <span class="rating" data-score="4.6">★★★★☆</span>
        </li>
      </ul>
    </section>
  </main>

  <footer>
    <p>Last updated: <time datetime="2024-04-01">April 2024</time></p>
  </footer>
</body>
</html>
"""

# ── 1. Parsing with lxml directly ────────────────────────────────────────────

print("=" * 60)
print("1. PARSING WITH lxml DIRECTLY")
print("=" * 60)

# lhtml.fromstring() returns the root element of the document.
# For full pages lhtml.document_fromstring() is more appropriate — it always
# returns an <html> element even if the input lacks one.
tree = lhtml.fromstring(CATALOGUE_HTML)

print(f"Root tag : {tree.tag}")       # 'html'
print(f"Type     : {type(tree)}")     # lxml.html.HtmlElement

# .text_content() concatenates all text inside an element (equivalent of BS .get_text())
h1 = tree.find(".//h1")              # .find() uses XPath under the hood
print(f"H1 text  : {h1.text_content()}")


# ── 2. XPath expressions ──────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("2. XPATH EXPRESSIONS")
print("=" * 60)

# //tag          — any <tag> anywhere in the tree
# /tag           — direct child
# @attr          — attribute
# text()         — text node
# [predicate]    — filter condition

# All book titles
book_titles = tree.xpath('//li[contains(@class,"book")]//h3/a/text()')
print("Book titles:")
for t in book_titles:
    print(f"  {t}")

# All hrefs on the page
all_hrefs = tree.xpath("//a/@href")
print(f"\nAll hrefs ({len(all_hrefs)}):")
for h in all_hrefs:
    print(f"  {h}")

# All free resources
free_items = tree.xpath('//*[contains(@class,"free")]')
print(f"\nFree resources ({len(free_items)}):")
for item in free_items:
    print(f"  {item.text_content().strip()}")

# Elements where data-score >= 4.8
high_rated = tree.xpath(
    '//*[@data-score and @data-score >= 4.8]'
)
print(f"\nHighly rated (≥ 4.8) resources: {len(high_rated)}")
# Note: XPath compares strings lexicographically — for numeric comparison
# use number() or Python post-filtering
high_rated_numeric = [
    el for el in tree.xpath('//*[@data-score]')
    if float(el.get("data-score", 0)) >= 4.8
]
print(f"  (numeric filter) : {len(high_rated_numeric)}")
for el in high_rated_numeric:
    parent_li = el.getparent().getparent().getparent()   # rating → li
    title = parent_li.xpath('.//h3/a/text()')
    print(f"  {title[0] if title else '?'}  — score {el.get('data-score')}")

# Using contains() for partial class matching
beginner = tree.xpath('//*[contains(@data-level,"beginner")]')
print(f"\nBeginner resources: {[el.xpath('.//h3/a/text()')[0] for el in beginner]}")

# Extracting text from specific positions (first, last)
first_author = tree.xpath('(//span[@class="author"])[1]/text()')
last_author  = tree.xpath('(//span[@class="author"])[last()]/text()')
print(f"\nFirst author : {first_author[0] if first_author else 'none'}")
print(f"Last author  : {last_author[0]  if last_author  else 'none'}")


# ── 3. XPath with namespaces (XHTML / XML) ───────────────────────────────────

print("\n" + "=" * 60)
print("3. XPATH — STRUCTURED EXTRACTION")
print("=" * 60)

def extract_resources_xpath(html_string: str) -> list[dict]:
    """
    Use XPath to extract all resources into structured dicts.
    Demonstrates getting element attributes and text in one pass.
    """
    tree = lhtml.fromstring(html_string)
    resources = []

    for li in tree.xpath('//li[contains(@class,"resource")]'):
        title_els = li.xpath('.//h3/a/text()')
        href_els  = li.xpath('.//h3/a/@href')
        author_els = li.xpath('.//span[@class="author"]/text()')
        price_els  = li.xpath('.//span[contains(@class,"price")]/text()')
        score_els  = li.xpath('.//span[@class="rating"]/@data-score')

        resources.append({
            "id":     li.get("data-id"),
            "type":   "book" if "book" in li.get("class","") else "course",
            "level":  li.get("data-level"),
            "title":  title_els[0]  if title_els  else "",
            "url":    href_els[0]   if href_els   else "",
            "author": author_els[0] if author_els else "",
            "price":  price_els[0].strip() if price_els else "",
            "score":  float(score_els[0])  if score_els else None,
        })
    return resources


resources = extract_resources_xpath(CATALOGUE_HTML)
print(f"{'ID':<5} {'Type':<8} {'Level':<14} {'Score':<7} {'Title'}")
print("-" * 70)
for r in sorted(resources, key=lambda x: -(x["score"] or 0)):
    print(f"{r['id']:<5} {r['type']:<8} {r['level']:<14} {r['score']:<7} {r['title']}")


# ── 4. lxml as BeautifulSoup's parser (best of both worlds) ─────────────────

print("\n" + "=" * 60)
print("4. lxml AS BEAUTIFULSOUP'S BACKEND PARSER")
print("=" * 60)

# You get BeautifulSoup's friendly API AND lxml's C-level parsing speed.
soup = BeautifulSoup(CATALOGUE_HTML, "lxml")   # ← just change the parser name

# The API is identical — only the parser underneath changes
courses = soup.select("#courses .resource")
print(f"Courses found via BS4 + lxml parser: {len(courses)}")
for c in courses:
    print(f"  {c.find('h3').text.strip()}")


# ── 5. Performance comparison ─────────────────────────────────────────────────

print("\n" + "=" * 60)
print("5. PERFORMANCE COMPARISON")
print("=" * 60)

# Generate a large synthetic HTML page for benchmarking
big_html = "<html><body>" + "".join(
    f'<div class="item"><h2>Title {i}</h2><p>Content paragraph {i}.</p></div>'
    for i in range(2000)
) + "</body></html>"

N = 20   # number of parse iterations

# html.parser (Python built-in)
t0 = time.perf_counter()
for _ in range(N):
    BeautifulSoup(big_html, "html.parser")
t_builtin = (time.perf_counter() - t0) / N * 1000

# lxml via BeautifulSoup
t0 = time.perf_counter()
for _ in range(N):
    BeautifulSoup(big_html, "lxml")
t_bs4_lxml = (time.perf_counter() - t0) / N * 1000

# lxml direct
t0 = time.perf_counter()
for _ in range(N):
    lhtml.fromstring(big_html)
t_lxml_direct = (time.perf_counter() - t0) / N * 1000

print(f"html.parser (built-in)  : {t_builtin:.1f} ms/parse")
print(f"BeautifulSoup + lxml    : {t_bs4_lxml:.1f} ms/parse")
print(f"lxml direct             : {t_lxml_direct:.1f} ms/parse")
print(f"\nSpeedup (lxml direct vs html.parser): {t_builtin/t_lxml_direct:.1f}×")


# ── 6. XPath vs CSS selector cheatsheet ──────────────────────────────────────

print("\n" + "=" * 60)
print("6. XPATH vs CSS SELECTOR CHEATSHEET")
print("=" * 60)

CHEATSHEET = [
    ("Any <p>",                    "//p",                        "p"),
    ("Direct child <li> of <ul>",  "//ul/li",                    "ul > li"),
    ("Class selector",             '//*[@class="item"]',         ".item"),
    ("ID selector",                '//*[@id="main"]',            "#main"),
    ("Has attribute",              "//a[@href]",                 "a[href]"),
    ("Attribute value",            '//a[@rel="nofollow"]',       'a[rel="nofollow"]'),
    ("Starts with",                '//a[starts-with(@href,"/")]',"a[href^='/']"),
    ("Ends with",                  '//a[ends-with(@href,".pdf")]',"a[href$='.pdf']"),
    ("Contains text",              '//p[contains(text(),"AI")]', "p  (no direct equiv)"),
    ("First element",              "(//li)[1]",                  "li:first-child"),
    ("Last element",               "(//li)[last()]",             "li:last-child"),
    ("Parent of element",          "//span/parent::div",         "(no parent selector)"),
    ("Text content",               "//h1/text()",                "(use .text in Python)"),
    ("Attribute value",            "//img/@src",                 "(use ['src'] in Python)"),
]

print(f"{'Task':<35} {'XPath':<45} {'CSS Selector'}")
print("-" * 110)
for task, xpath, css in CHEATSHEET:
    print(f"{task:<35} {xpath:<45} {css}")
