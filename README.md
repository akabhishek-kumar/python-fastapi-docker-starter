# python-fastapi-docker-starter

A production-ready REST API built with **FastAPI**, **PostgreSQL**, and **Docker**. Demonstrates async Python, dependency injection, Pydantic v2 validation, SQLAlchemy 2.0 ORM, and containerized multi-service deployment.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.115 |
| Database | PostgreSQL 16 (asyncpg driver) |
| ORM | SQLAlchemy 2.0 (async) |
| Validation | Pydantic v2 |
| Config | pydantic-settings (.env) |
| Container | Docker + docker-compose |
| Testing | pytest + httpx (async) |

## Project Structure

```
app/
├── config.py       # pydantic-settings — reads from .env
├── database.py     # async engine, session factory, get_db() dependency
├── models.py       # SQLAlchemy 2.0 Mapped[T] ORM models
├── schemas.py      # Pydantic v2 request/response schemas
├── main.py         # FastAPI app, lifespan, CORS, /health
└── routers/
    └── items.py    # CRUD endpoints — GET, POST, PATCH
tests/
└── test_items.py   # async tests with SQLite in-memory override
Dockerfile          # multi-layer build with pip cache optimisation
docker-compose.yml  # FastAPI + PostgreSQL with healthcheck & depends_on
```

## Quick Start

### With Docker (recommended)

```bash
git clone https://github.com/akabhishek-kumar/python-fastapi-docker-starter
cd python-fastapi-docker-starter
docker compose up --build
```

API is live at **http://localhost:8000**  
Interactive docs at **http://localhost:8000/docs**

### Without Docker

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # add your Postgres credentials
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/items/` | List all items |
| POST | `/items/` | Create item |
| GET | `/items/{id}` | Get item by ID |
| PATCH | `/items/{id}` | Update item |

## Key Concepts Demonstrated

- **Async SQLAlchemy 2.0** — `Mapped[T]` + `mapped_column()` ORM style, `AsyncSession`, `async_sessionmaker`
- **Dependency Injection** — `Annotated[AsyncSession, Depends(get_db)]` pattern
- **Pydantic v2** — `ConfigDict(from_attributes=True)`, `model_dump(exclude_unset=True)` for partial updates
- **Lifespan context manager** — startup/shutdown events (replaces deprecated `@app.on_event`)
- **Docker networking** — inter-container communication via service name (`db`) not `localhost`
- **Health checks** — `pg_isready` probe with `depends_on: condition: service_healthy`

## Running Tests

```bash
pytest tests/ -v
```

Tests use SQLite in-memory via `dependency_overrides` — no Postgres required.

---

Part of my AI Engineering learning series → [GitHub](https://github.com/akabhishek-kumar)
