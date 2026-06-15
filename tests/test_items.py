"""Integration tests for the items endpoints.

Uses an in-memory SQLite DB (aiosqlite) so no Postgres needed to run tests.
Pattern: override the get_db dependency to inject a test session.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app

# ── Test DB setup (SQLite in-memory, no Postgres needed) ───────────────────

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.dependency_overrides[get_db] = override_get_db
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── Tests ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_item(client: AsyncClient):
    payload = {"title": "Test item", "description": "A test", "owner": "abhishek"}
    resp = await client.post("/items/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == 1
    assert data["title"] == "Test item"
    assert data["owner"] == "abhishek"


@pytest.mark.asyncio
async def test_list_items(client: AsyncClient):
    # Create two items
    for title in ["Item A", "Item B"]:
        await client.post("/items/", json={"title": title, "owner": "abhishek"})

    resp = await client.get("/items/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_item(client: AsyncClient):
    create_resp = await client.post(
        "/items/", json={"title": "Fetch me", "owner": "abhishek"}
    )
    item_id = create_resp.json()["id"]

    resp = await client.get(f"/items/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Fetch me"


@pytest.mark.asyncio
async def test_get_item_not_found(client: AsyncClient):
    resp = await client.get("/items/999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_items_filter_by_owner(client: AsyncClient):
    await client.post("/items/", json={"title": "Mine", "owner": "abhishek"})
    await client.post("/items/", json={"title": "Theirs", "owner": "other_user"})

    resp = await client.get("/items/?owner=abhishek")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["owner"] == "abhishek"
