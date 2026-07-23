"""Demo FastAPI backend for Databricks Apps.

Run locally:
    uvicorn app:app --reload

On Databricks Apps the process is started via the command in app.yaml and
must bind to the port supplied through the DATABRICKS_APP_PORT env variable.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Demo FastAPI Backend",
    description="A minimal FastAPI application ready to deploy on Databricks Apps.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS: allow the external React UI to call these endpoints from a browser.
# Set ALLOWED_ORIGINS (comma-separated) in app.yaml / env for production.
# Example: ALLOWED_ORIGINS="https://my-react-app.com,http://localhost:5173"
# ---------------------------------------------------------------------------
_allowed_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# In-memory demo data store
# ---------------------------------------------------------------------------
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    in_stock: bool = True


_items: dict[int, Item] = {
    1: Item(name="Notebook", description="Spiral bound, 200 pages", price=4.99),
    2: Item(name="Pen", description="Blue ink, ballpoint", price=1.49),
}
_next_id = 3


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def root() -> dict[str, str]:
    """Landing endpoint with basic service info."""
    return {
        "service": "Demo FastAPI Backend",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint used by Databricks Apps readiness probes."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/env")
def env() -> dict[str, str | None]:
    """Expose a few (non-secret) Databricks environment values for demo purposes."""
    return {
        "app_port": os.getenv("DATABRICKS_APP_PORT"),
        "workspace_url": os.getenv("DATABRICKS_HOST"),
        "app_name": os.getenv("DATABRICKS_APP_NAME"),
    }


@app.get("/items")
def list_items() -> dict[int, Item]:
    """Return all items."""
    return _items


@app.get("/items/{item_id}")
def get_item(item_id: int) -> Item:
    """Return a single item by id."""
    item = _items.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", status_code=201)
def create_item(item: Item) -> dict[str, int | Item]:
    """Create a new item."""
    global _next_id
    item_id = _next_id
    _items[item_id] = item
    _next_id += 1
    return {"id": item_id, "item": item}


@app.delete("/items/{item_id}")
def delete_item(item_id: int) -> dict[str, str]:
    """Delete an item by id."""
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    del _items[item_id]
    return {"status": "deleted"}
