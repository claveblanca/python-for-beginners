# Chapter 10 — REST APIs with Flask & FastAPI

Both projects implement the **same Books CRUD API** so you can compare the two frameworks side-by-side.

---

## Endpoints (identical in both)

| Method   | URL               | Description           |
|----------|-------------------|-----------------------|
| `GET`    | `/books`          | List all books        |
| `GET`    | `/books/{id}`     | Get a single book     |
| `POST`   | `/books`          | Create a book         |
| `PUT`    | `/books/{id}`     | Full update (replace) |
| `PATCH`  | `/books/{id}`     | Partial update        |
| `DELETE` | `/books/{id}`     | Delete a book         |

---

## Flask (`flask_api/`)

### Install & run
```bash
cd flask_api
pip install -r requirements.txt
python app.py          # http://localhost:5000
```

### Quick test with curl
```bash
# List all books
curl http://localhost:5000/books

# Get one book
curl http://localhost:5000/books/1

# Create a book
curl -X POST http://localhost:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "SICP", "author": "Abelson & Sussman", "year": 1996}'

# Full update
curl -X PUT http://localhost:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code 2nd Ed.", "author": "Robert C. Martin", "year": 2025}'

# Partial update
curl -X PATCH http://localhost:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"year": 2025}'

# Delete
curl -X DELETE http://localhost:5000/books/1
```

---

## FastAPI (`fastapi_api/`)

### Install & run
```bash
cd fastapi_api
pip install -r requirements.txt
python app.py          # http://localhost:8000
```

Interactive docs are available automatically at:
- Swagger UI → http://localhost:8000/docs
- ReDoc      → http://localhost:8000/redoc

### Quick test with curl
```bash
# List all books
curl http://localhost:8000/books

# Get one book
curl http://localhost:8000/books/1

# Create a book
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "SICP", "author": "Abelson & Sussman", "year": 1996}'

# Full update
curl -X PUT http://localhost:8000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code 2nd Ed.", "author": "Robert C. Martin", "year": 2025}'

# Partial update
curl -X PATCH http://localhost:8000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"year": 2025}'

# Delete
curl -X DELETE http://localhost:8000/books/1
```

---

## Framework comparison

| Feature                    | Flask                        | FastAPI                        |
|----------------------------|------------------------------|--------------------------------|
| **Type hints / validation**| Manual                       | Pydantic (automatic)           |
| **Async support**          | Limited (via extensions)     | Native (`async def`)           |
| **Auto docs (OpenAPI)**    | No (needs flask-restx, etc.) | Yes (`/docs`, `/redoc`)        |
| **Performance**            | Good                         | Excellent (Starlette + ASGI)   |
| **Learning curve**         | Very low                     | Low                            |
| **Ecosystem / maturity**   | Mature, huge ecosystem       | Newer, fast-growing            |
| **Best for**               | Simple apps, quick scripts   | Production APIs, typed projects|

### Key code differences

**Routing**
```python
# Flask
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id: int): ...

# FastAPI
@app.get("/books/{book_id}")
def get_book(book_id: int): ...
```

**Input validation**
```python
# Flask — manual
data = request.get_json()
if "title" not in data:
    abort(400, "Missing title")

# FastAPI — automatic via Pydantic
class BookCreate(BaseModel):
    title: str
    author: str
    year: int

def create_book(payload: BookCreate): ...
```

**Error responses**
```python
# Flask
abort(404, description="Not found")

# FastAPI
raise HTTPException(status_code=404, detail="Not found")
```

## Technologies Used

- **Flask** — lightweight Python web framework for the REST API
- **FastAPI** — modern async REST framework with automatic OpenAPI docs
- **Pydantic** — data validation and serialisation (FastAPI models)
- **uvicorn** — ASGI server used to run the FastAPI app
