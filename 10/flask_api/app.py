from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# In-memory "database"
books: dict[int, dict] = {
    1: {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "year": 2008},
    2: {"id": 2, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "year": 1999},
}
next_id = 3


# ── Helpers ──────────────────────────────────────────────────────────────────

def find_book_or_404(book_id: int) -> dict:
    book = books.get(book_id)
    if book is None:
        abort(404, description=f"Book with id={book_id} not found")
    return book


def validate_body(required: list[str]) -> dict:
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Request body must be valid JSON")
    missing = [f for f in required if f not in data]
    if missing:
        abort(400, description=f"Missing required fields: {missing}")
    return data


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/books", methods=["GET"])
def list_books():
    """Return all books."""
    return jsonify(list(books.values())), 200


@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id: int):
    """Return a single book by ID."""
    return jsonify(find_book_or_404(book_id)), 200


@app.route("/books", methods=["POST"])
def create_book():
    """Create a new book."""
    global next_id
    data = validate_body(["title", "author", "year"])
    book = {
        "id": next_id,
        "title": data["title"],
        "author": data["author"],
        "year": int(data["year"]),
    }
    books[next_id] = book
    next_id += 1
    return jsonify(book), 201


@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id: int):
    """Replace a book entirely (full update)."""
    find_book_or_404(book_id)
    data = validate_body(["title", "author", "year"])
    book = {
        "id": book_id,
        "title": data["title"],
        "author": data["author"],
        "year": int(data["year"]),
    }
    books[book_id] = book
    return jsonify(book), 200


@app.route("/books/<int:book_id>", methods=["PATCH"])
def partial_update_book(book_id: int):
    """Update only the supplied fields (partial update)."""
    book = find_book_or_404(book_id)
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Request body must be valid JSON")
    for field in ("title", "author", "year"):
        if field in data:
            book[field] = int(data[field]) if field == "year" else data[field]
    return jsonify(book), 200


@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id: int):
    """Delete a book by ID."""
    find_book_or_404(book_id)
    del books[book_id]
    return "", 204


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(400)
@app.errorhandler(404)
def http_error(e):
    return jsonify({"error": e.description}), e.code


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
