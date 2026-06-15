"""Pydantic schemas — request validation + response serialisation.

Separation of concerns:
  - ORM model  (models.py)   = what lives in the DB
  - Pydantic schema (here)   = what enters/exits the API boundary
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ── Request schemas (what the caller sends) ────────────────────────────────

class ItemCreate(BaseModel):
    """Payload required to create a new item."""

    title: str = Field(..., min_length=1, max_length=200, examples=["Buy groceries"])
    description: str | None = Field(None, max_length=2000, examples=["Milk, eggs, bread"])
    owner: str = Field(..., min_length=1, max_length=100, examples=["abhishek"])


class ItemUpdate(BaseModel):
    """All fields optional — PATCH semantics (only send what changes)."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)


# ── Response schemas (what the API returns) ────────────────────────────────

class ItemResponse(BaseModel):
    """Full item representation returned from the API."""

    model_config = ConfigDict(from_attributes=True)  # lets Pydantic read ORM objects

    id: int
    title: str
    description: str | None
    owner: str
    created_at: datetime
    updated_at: datetime


class ItemListResponse(BaseModel):
    """Paginated list wrapper — adding pagination here later is non-breaking."""

    items: list[ItemResponse]
    total: int


# ── Generic response helpers ───────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
