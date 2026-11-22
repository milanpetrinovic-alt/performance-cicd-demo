"""Self-contained HTTP-versus-browser workshop endpoints.

Add to app/main.py:

    from app.protocol_demo import router as protocol_demo_router
    app.include_router(protocol_demo_router)

Uses a separate /protocol-demo prefix to preserve existing API contracts.
"""

from pathlib import Path

from fastapi import APIRouter, Query
from fastapi.responses import FileResponse

router = APIRouter(tags=["Protocol vs Browser Workshop"])
STATIC = Path(__file__).resolve().parent / "static"

CATALOG = [
    {"id": "p-101", "name": "Laptop Pro 14", "category": "Laptop", "price": 1299},
    {"id": "p-102", "name": "Laptop Air 13", "category": "Laptop", "price": 899},
    {"id": "p-103", "name": "Gaming Laptop 16", "category": "Laptop", "price": 1599},
    {"id": "p-104", "name": "Wireless Mouse", "category": "Accessories", "price": 39},
    {"id": "p-105", "name": "USB-C Dock", "category": "Accessories", "price": 119},
    {"id": "p-106", "name": "Tablet Mini", "category": "Tablet", "price": 449},
]


@router.get("/protocol-demo", include_in_schema=False)
def demo_page():
    return FileResponse(STATIC / "index.html", media_type="text/html")


@router.get("/protocol-demo/search.js", include_in_schema=False)
def demo_script():
    return FileResponse(STATIC / "search.js", media_type="text/javascript")


@router.get("/protocol-demo/styles.css", include_in_schema=False)
def demo_styles():
    return FileResponse(STATIC / "styles.css", media_type="text/css")


@router.get("/protocol-demo/api/search")
def search_catalog(q: str = Query(min_length=1, max_length=80)):
    """Identical API behavior in both UI modes. No artificial server delay."""
    term = q.strip().lower()
    results = [
        item for item in CATALOG
        if term in item["name"].lower() or term in item["category"].lower()
    ]
    return {"query": q, "total": len(results), "results": results}
