from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="Books API", version="1.0.0")


# ── Schemas ───────────────────────────────────────────────────────────────────

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, examples=["Clean Code"])
    author: str = Field(..., min_length=1, examples=["Robert C. Martin"])
    year: int = Field(..., ge=1, examples=[2008])


class BookUpdate(BaseModel):
    """Full update — all fields required."""
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    year: int = Field(..., ge=1)


class BookPatch(BaseModel):
    """Partial update — all fields optional."""
    title: Optional[str] = Field(default=None, min_length=1)
    author: Optional[str] = Field(default=None, min_length=1)
    year: Optional[int] = Field(default=None, ge=1)


class Book(BookCreate):
    id: int


# ── In-memory "database" ──────────────────────────────────────────────────────

books: dict[int, Book] = {
    1: Book(id=1, title="Clean Code", author="Robert C. Martin", year=2008),
    2: Book(id=2, title="The Pragmatic Programmer", author="Andrew Hunt", year=1999),
}
next_id = 3


# ── Helpers ───────────────────────────────────────────────────────────────────

def find_book_or_404(book_id: int) -> Book:
    book = books.get(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    return book


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/books", response_model=list[Book], tags=["Books"])
def list_books():
    """Return all books."""
    return list(books.values())


@app.get("/books/{book_id}", response_model=Book, tags=["Books"])
def get_book(book_id: int):
    """Return a single book by ID."""
    return find_book_or_404(book_id)


@app.post("/books", response_model=Book, status_code=201, tags=["Books"])
def create_book(payload: BookCreate):
    """Create a new book."""
    global next_id
    book = Book(id=next_id, **payload.model_dump())
    books[next_id] = book
    next_id += 1
    return book


@app.put("/books/{book_id}", response_model=Book, tags=["Books"])
def update_book(book_id: int, payload: BookUpdate):
    """Replace a book entirely (full update)."""
    find_book_or_404(book_id)
    book = Book(id=book_id, **payload.model_dump())
    books[book_id] = book
    return book


@app.patch("/books/{book_id}", response_model=Book, tags=["Books"])
def partial_update_book(book_id: int, payload: BookPatch):
    """Update only the supplied fields (partial update)."""
    book = find_book_or_404(book_id)
    updated = book.model_dump()
    for field, value in payload.model_dump(exclude_none=True).items():
        updated[field] = value
    books[book_id] = Book(**updated)
    return books[book_id]


@app.delete("/books/{book_id}", status_code=204, tags=["Books"])
def delete_book(book_id: int):
    """Delete a book by ID."""
    find_book_or_404(book_id)
    del books[book_id]


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
