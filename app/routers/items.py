"""Items router — 3 endpoints that demonstrate FastAPI + async SQLAlchemy patterns."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Item
from app.schemas import ItemCreate, ItemListResponse, ItemResponse, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

# Type alias so route signatures stay readable
DB = Annotated[AsyncSession, Depends(get_db)]


# ── Endpoint 1: List items (with optional owner filter + pagination) ────────

@router.get("/", response_model=ItemListResponse)
async def list_items(
    db: DB,
    owner: str | None = Query(None, description="Filter by owner username"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ItemListResponse:
    """Return a paginated list of items, optionally filtered by owner."""

    query = select(Item)
    count_query = select(func.count()).select_from(Item)

    if owner:
        query = query.where(Item.owner == owner)
        count_query = count_query.where(Item.owner == owner)

    query = query.order_by(Item.created_at.desc()).limit(limit).offset(offset)

    results = await db.execute(query)
    total_result = await db.execute(count_query)

    items = results.scalars().all()
    total = total_result.scalar_one()

    return ItemListResponse(
        items=[ItemResponse.model_validate(item) for item in items],
        total=total,
    )


# ── Endpoint 2: Create item ─────────────────────────────────────────────────

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(payload: ItemCreate, db: DB) -> ItemResponse:
    """Create a new item and persist it to Postgres."""

    item = Item(
        title=payload.title,
        description=payload.description,
        owner=payload.owner,
    )
    db.add(item)
    await db.flush()   # flush assigns the DB-generated id without committing
    await db.refresh(item)  # refresh loads server-generated timestamps

    return ItemResponse.model_validate(item)


# ── Endpoint 3: Get item by ID ──────────────────────────────────────────────

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: DB) -> ItemResponse:
    """Fetch a single item by its primary key."""

    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )

    return ItemResponse.model_validate(item)


# ── Bonus endpoint: Update item (demonstrates PATCH pattern) ───────────────

@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, payload: ItemUpdate, db: DB) -> ItemResponse:
    """Partially update an item — only supplied fields are changed."""

    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )

    # model_dump(exclude_unset=True) gives only fields the caller actually sent
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.flush()
    await db.refresh(item)

    return ItemResponse.model_validate(item)
