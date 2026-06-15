"""Application entry point.

Startup sequence:
  1. Create DB tables (dev convenience — swap for Alembic in prod)
  2. Mount routers
  3. Expose /health for readiness checks
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables
from app.routers import items


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Runs once on startup (before yield) and once on shutdown (after yield)."""
    await create_tables()
    yield
    # add cleanup here if needed (e.g. close external connections)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS — lock this down to your real frontend origin in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(items.router)


# ── Health check ────────────────────────────────────────────────────────────

@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness probe — orchestrators (k8s, Render, etc.) hit this."""
    return {"status": "ok", "version": settings.app_version}
