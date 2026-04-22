"""
Chapter 12 — Example 02: Searching the Tree
============================================
Covers section 12.3:
  - find() vs find_all()
  - Filtering by tag, class_, id, attribute value
  - CSS selectors with select() and select_one()
  - Practical selector patterns from browser DevTools

Install:
    pip install beautifulsoup4 lxml
"""

from bs4 import BeautifulSoup

# ── Sample HTML that mimics a real product listing page ──────────────────────

SHOP_HTML = """
<html>
<body>
  <h1 class="page-title">Our Products</h1>

  <div id="featured">
    <h2>Featured</h2>
    <div class="product card featured" data-id="101">
      <h3 class="name">Wireless Keyboard</h3>
      <span class="price">£39.99</span>
      <span class="badge sale">SALE</span>
      <a href="/products/101">View</a>
    </div>
  </div>

  <ul class="product-list">
    <li class="product item" data-id="201" data-category="peripherals">
      <span class="name">USB-C Hub</span>
      <span class="price">£24.99</span>
      <a href="/products/201">View</a>
    </li>
    <li class="product item" data-id="202" data-category="peripherals">
      <span class="name">HDMI Cable</span>
      <span class="price">£9.99</span>
      <a href="/products/202">View</a>
    </li>
    <li class="product item out-of-stock" data-id="203" data-category="audio">
      <span class="name">Noise-Cancelling Headphones</span>
      <span class="price">£149.99</span>
      <span class="badge">OUT OF STOCK</span>
      <a href="/products/203">View</a>
    </li>
  </ul>

  <nav id="pagination">
    <a href="/page/1" class="page active">1</a>
    <a href="/page/2" class="page">2</a>
    <a href="/page/3" class="page">3</a>
    <a href="/page/next" class="page next">Next →</a>
  </nav>
</body>
</html>
"""

soup = BeautifulSoup(SHOP_HTML, "lxml")

# ── 1. find() — first match only ─────────────────────────────────────────────

print("=" * 60)
print("1. find() — FIRST MATCH")
print("=" * 60)

print(soup.find("h1").text)                           # by tag name
print(soup.find("span", class_="price").text)         # by class (note the underscore)
print(soup.find(id="featured").find("h2").text)       # chained: find inside find
print(soup.find("li", class_="out-of-stock")
      .find("span", class_="name").text)              # nested find


# ── 2. find_all() — every match ───────────────────────────────────────────────

print("\n" + "=" * 60)
print("2. find_all() — ALL MATCHES")
print("=" * 60)

# All prices on the page
prices = soup.find_all("span", class_="price")
print("All prices:")
for p in prices:
    print(f"  {p.text}")

# All <a> tags that have an href (skips anchors without href)
links = soup.find_all("a", href=True)
print(f"\nAll links ({len(links)} found):")
for a in links:
    print(f"  {a.text:<25}  →  {a['href']}")

# All product list items
items = soup.find_all("li", class_="product")
print(f"\nProduct list items: {len(items)}")

# Limit results with the limit= argument
first_two = soup.find_all("li", limit=2)
print(f"First 2 <li> tags: {[li.find('span', class_='name').text for li in first_two]}")


# ── 3. Filtering by attribute value ──────────────────────────────────────────

print("\n" + "=" * 60)
print("3. FILTERING BY DATA ATTRIBUTES")
print("=" * 60)

# attrs= dict lets you filter on any attribute, including data-*
peripherals = soup.find_all("li", attrs={"data-category": "peripherals"})
print("Peripherals:")
for item in peripherals:
    print(f"  [{item['data-id']}] {item.find('span', class_='name').text}")

# Find a specific product by its data-id
product_101 = soup.find(attrs={"data-id": "101"})
print(f"\nProduct 101: {product_101.find('h3').text}")


# ── 4. select() and select_one() — CSS selectors ─────────────────────────────

print("\n" + "=" * 60)
print("4. CSS SELECTORS WITH select()")
print("=" * 60)

# Descendant selector: all <span> inside .product
print("Spans inside .product:")
for span in soup.select(".product span"):
    print(f"  [{span.get('class', ['?'])[0]}] {span.text}")

# Child selector: direct <li> children of .product-list
direct_items = soup.select("ul.product-list > li")
print(f"\nDirect <li> children: {len(direct_items)}")

# Compound class: element with BOTH classes
featured_card = soup.select_one(".product.featured")
print(f"\nFeatured product: {featured_card.find('h3').text}")

# Attribute presence selector
with_badge = soup.select("[class~=badge]")       # class contains the word "badge"
print(f"\nElements with 'badge' class: {[b.text for b in with_badge]}")

# Attribute value selector
sale_badge = soup.select_one(".badge.sale")
print(f"Sale badge text: {sale_badge.text if sale_badge else 'none'}")

# :not() pseudo-class — items that are NOT out of stock
in_stock = soup.select("li.product:not(.out-of-stock)")
print(f"\nIn-stock products ({len(in_stock)}):")
for item in in_stock:
    print(f"  {item.find('span', class_='name').text}")


# ── 5. Pagination links ───────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("5. EXTRACTING PAGINATION LINKS")
print("=" * 60)

# All page links except "Next"
page_links = soup.select("nav#pagination a.page:not(.next)")
print("Page links:")
for a in page_links:
    active = " ← current" if "active" in a.get("class", []) else ""
    print(f"  Page {a.text}  {a['href']}{active}")

# The next-page URL
next_link = soup.select_one("a.page.next")
print(f"\nNext page URL: {next_link['href'] if next_link else 'none (last page)'}")


# ── 6. Practical pattern: scraping a product catalogue ───────────────────────

print("\n" + "=" * 60)
print("6. COMPLETE PRODUCT SCRAPER PATTERN")
print("=" * 60)

def scrape_products(html: str) -> list[dict]:
    """Extract all products from a listing page into a list of dicts."""
    soup = BeautifulSoup(html, "lxml")
    products = []

    # Try the <ul> list first, fall back to any .product element
    containers = soup.select("ul.product-list .product") or soup.select(".product")

    for item in containers:
        name_tag  = item.select_one(".name")
        price_tag = item.select_one(".price")
        link_tag  = item.find("a", href=True)

        products.append({
            "id":           item.get("data-id"),
            "name":         name_tag.text.strip()  if name_tag  else None,
            "price":        price_tag.text.strip() if price_tag else None,
            "url":          link_tag["href"]        if link_tag  else None,
            "out_of_stock": "out-of-stock" in item.get("class", []),
        })

    return products


catalogue = scrape_products(SHOP_HTML)
for p in catalogue:
    stock = "❌ out of stock" if p["out_of_stock"] else "✅ in stock"
    print(f"  [{p['id']}] {p['name']:<35} {p['price']:<10}  {stock}")
