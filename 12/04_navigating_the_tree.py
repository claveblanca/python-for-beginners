"""
Chapter 12 — Example 04: Navigating the DOM Tree
=================================================
Covers section 12.5:
  - .parent, .parents (chain up to root)
  - .children, .descendants (walk down)
  - .next_sibling vs .find_next_sibling()
  - .previous_sibling vs .find_previous_sibling()
  - find_next(), find_previous() — search forward/backward
  - Practical pattern: scraping a definition list (<dl>)
  - Practical pattern: extracting adjacent label→value pairs

Install:
    pip install beautifulsoup4 lxml
"""

from bs4 import BeautifulSoup, Tag, NavigableString

# ── Sample HTML ───────────────────────────────────────────────────────────────

PROFILE_HTML = """
<html>
<body>

  <section id="profile">
    <h2>Developer Profile</h2>
    <dl class="metadata">
      <dt>Name</dt>      <dd>Alice Smith</dd>
      <dt>Language</dt>  <dd>Python</dd>
      <dt>Version</dt>   <dd>3.12</dd>
      <dt>Location</dt>  <dd>London, UK</dd>
      <dt>GitHub</dt>    <dd><a href="https://github.com/alice">@alice</a></dd>
    </dl>
  </section>

  <section id="posts">
    <h2>Recent Posts</h2>
    <article>
      <h3 class="post-title">Async Python in 2024</h3>
      <p class="summary">An overview of asyncio patterns.</p>
      <ul class="tags">
        <li>python</li><li>async</li><li>tutorial</li>
      </ul>
    </article>
    <article>
      <h3 class="post-title">Type Hints Deep Dive</h3>
      <p class="summary">Everything about Python typing module.</p>
      <ul class="tags">
        <li>python</li><li>typing</li><li>advanced</li>
      </ul>
    </article>
  </section>

</body>
</html>
"""

soup = BeautifulSoup(PROFILE_HTML, "lxml")


# ── 1. Moving up: .parent and .parents ───────────────────────────────────────

print("=" * 60)
print("1. MOVING UP THE TREE")
print("=" * 60)

dd_python = soup.find("dd", string="Python")

print(f"Element itself : <{dd_python.name}> {dd_python.text}")
print(f".parent        : <{dd_python.parent.name}>")
print(f".parent.parent : <{dd_python.parent.parent.name}> id={dd_python.parent.parent.get('id')}")

# .parents is a generator — walk all the way to the document root
ancestor_names = [a.name for a in dd_python.parents if hasattr(a, "name")]
print(f"Ancestor chain : {' → '.join(a for a in ancestor_names if a)}")


# ── 2. Moving down: .children and .descendants ────────────────────────────────

print("\n" + "=" * 60)
print("2. MOVING DOWN THE TREE")
print("=" * 60)

dl = soup.find("dl", class_="metadata")

# .children returns a generator — includes NavigableString whitespace nodes
all_children = list(dl.children)
tag_children  = [c for c in dl.children if isinstance(c, Tag)]

print(f"Total .children (incl. whitespace): {len(all_children)}")
print(f"Tag children only                 : {len(tag_children)}")
print("Tags:", [f"<{c.name}>{c.text.strip()}" for c in tag_children])

# .descendants walks every node at any depth — useful for counting
all_tags = [d for d in dl.descendants if isinstance(d, Tag)]
print(f"\n.descendants (all tags at any depth): {len(all_tags)}")
for d in all_tags:
    if d.name == "a":
        print(f"  Found <a> inside dl: {d.text} → {d['href']}")


# ── 3. Sideways: siblings ─────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("3. SIBLING NAVIGATION")
print("=" * 60)

# .next_sibling may be a whitespace NavigableString, not the tag you want.
dt_version = soup.find("dt", string="Version")

raw_next = dt_version.next_sibling
print(f".next_sibling type : {type(raw_next).__name__!r}")
print(f".next_sibling repr : {repr(str(raw_next)[:30])}")   # likely '\n' or '  '

# .find_next_sibling() skips whitespace and finds the next matching tag
dd_value = dt_version.find_next_sibling("dd")
print(f".find_next_sibling('dd') : {dd_value.text}")

# Going backwards
dt_prev = dt_version.find_previous_sibling("dt")
print(f".find_previous_sibling('dt') : {dt_prev.text}")


# ── 4. Practical pattern: parse a <dl> into a dict ────────────────────────────

print("\n" + "=" * 60)
print("4. PARSING A <dl> INTO A DICT")
print("=" * 60)

def parse_definition_list(dl_tag) -> dict:
    """
    Convert a <dl><dt>key</dt><dd>value</dd>...</dl>
    into a plain Python dict.
    Uses find_next_sibling() to pair each <dt> with its <dd>.
    """
    result = {}
    for dt in dl_tag.find_all("dt"):
        key = dt.get_text(strip=True)
        dd  = dt.find_next_sibling("dd")
        # Use get_text for the value, so nested <a> tags are still captured as text
        result[key] = dd.get_text(strip=True) if dd else None
    return result


profile = parse_definition_list(soup.find("dl", class_="metadata"))
print("Parsed profile dict:")
for k, v in profile.items():
    print(f"  {k:<12}: {v}")


# ── 5. find_next() and find_previous() ───────────────────────────────────────

print("\n" + "=" * 60)
print("5. find_next() AND find_previous()")
print("=" * 60)

# find_next() searches forward in document order — not limited to siblings
h2_posts = soup.find("h2", string="Recent Posts")

# What is the first <h3> anywhere after this heading?
first_post_title = h2_posts.find_next("h3")
print(f"First <h3> after 'Recent Posts' : {first_post_title.text}")

# All <h3> tags after that heading
all_post_titles = h2_posts.find_all_next("h3")
print(f"All post titles after heading   : {[h.text for h in all_post_titles]}")

# find_previous() works in reverse
last_dt = soup.find_all("dt")[-1]
print(f"\nLast <dt>                       : {last_dt.text}")
print(f"find_previous('dt')             : {last_dt.find_previous('dt').text}")


# ── 6. Practical pattern: extract post metadata by traversal ─────────────────

print("\n" + "=" * 60)
print("6. EXTRACTING POST METADATA BY TREE TRAVERSAL")
print("=" * 60)

def extract_posts(soup) -> list[dict]:
    """
    Extract each article's title, summary, and tags.
    Demonstrates child navigation as an alternative to select().
    """
    posts = []
    for article in soup.find_all("article"):
        title   = article.find("h3", class_="post-title")
        summary = article.find("p",  class_="summary")
        tag_list = article.find("ul", class_="tags")

        # Extract individual tags from the <ul>
        tags = [
            li.get_text(strip=True)
            for li in (tag_list.find_all("li") if tag_list else [])
        ]

        posts.append({
            "title":   title.text.strip()   if title   else "",
            "summary": summary.text.strip() if summary else "",
            "tags":    tags,
        })
    return posts


posts = extract_posts(soup)
for post in posts:
    print(f"\nTitle   : {post['title']}")
    print(f"Summary : {post['summary']}")
    print(f"Tags    : {', '.join(post['tags'])}")


# ── 7. Distinguishing Tag nodes from text nodes ───────────────────────────────

print("\n" + "=" * 60)
print("7. TAG vs NAVIGABLESTRING — FILTERING CHILDREN")
print("=" * 60)

# Mixing tag and text children is common — always check the type before .name
section = soup.find("section", id="profile")
for child in section.children:
    if isinstance(child, Tag):
        print(f"  TAG  : <{child.name}> → {child.get_text(strip=True)[:40]}")
    elif isinstance(child, NavigableString) and child.strip():
        print(f"  TEXT : {repr(child.strip())}")
