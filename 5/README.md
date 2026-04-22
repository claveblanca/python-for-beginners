# Chapter 5 — Working with Data Structures

Lists, tuples, sets, and dictionaries — Python's built-in collections.

## Prerequisites

- Python 3.10+ installed
- Completed [Chapter 4](../4/) (functions, modules)

## The files

| # | File | Topic |
|---|------|-------|
| 1 | `lists.py` | Creating, indexing, slicing, modifying, sorting, comprehensions, copying, unpacking |
| 2 | `tuples_and_sets.py` | Tuples (immutable, unpacking, namedtuple) and sets (unique values, operations, frozenset) |
| 3 | `dictionaries.py` | Key-value pairs, access, iteration, comprehensions, nesting, defaultdict, merging |

## How to run

```bash
cd 5
python lists.py
python tuples_and_sets.py
python dictionaries.py
```

## Concepts introduced

### Lists
- `[]` — ordered, mutable collection
- `.append()`, `.insert()`, `.remove()`, `.pop()`, `.extend()`
- Indexing `[0]`, slicing `[a:b]`, reverse `[::-1]`
- `len()`, `min()`, `max()`, `sum()`, `sorted()`
- `.sort()`, `.reverse()`, `.count()`, `.index()`
- `in` membership test
- List comprehension — `[expr for x in seq if cond]`
- `.copy()` vs. reference
- Unpacking — `first, *rest = [1, 2, 3, 4]`

### Tuples
- `()` — ordered, immutable
- Single-element tuple needs trailing comma: `(42,)`
- Unpacking — `x, y = (3, 7)`
- Tuples as dictionary keys
- `namedtuple` — named fields

### Sets
- `set()` / `{}` — unordered, unique values
- `.add()`, `.discard()`, `.remove()`
- Union `|`, intersection `&`, difference `-`, symmetric `^`
- Very fast `in` membership test
- Set comprehension — `{expr for x in seq}`
- `frozenset` — immutable set

### Dictionaries
- `{key: value}` — key-value mapping
- `d[key]`, `.get(key, default)`
- `.keys()`, `.values()`, `.items()`
- `del d[key]`, `.pop(key)`
- `.update()`, `.setdefault()`
- Dictionary comprehension — `{k: v for k, v in …}`
- Nested dictionaries
- `defaultdict` — auto-initializing values
- Merging — `{**a, **b}` or `a | b` (Python 3.9+)
