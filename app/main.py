from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import queries

app = FastAPI(title="Sales Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def make_filters(start_date, end_date, category, segment, city, status):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be after end_date")
    return {
        "start_date": start_date,
        "end_date": end_date,
        "category": category,
        "segment": segment,
        "city": city,
        "status": status,
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/filters")
def filter_options():
    return queries.get_filter_options()


@app.get("/api/dashboard")
def dashboard(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    city: Optional[str] = None,
    status: Optional[str] = None,
):
    filters = make_filters(start_date, end_date, category, segment, city, status)
    return {
        "kpis": queries.get_kpis(filters),
        "monthly": queries.get_monthly_revenue(filters),
        "by_category": queries.get_revenue_by("category", filters),
        "by_segment": queries.get_revenue_by("customer_segment", filters),
        "by_city": queries.get_revenue_by("city", filters),
        "by_status": queries.get_revenue_by("order_status", filters),
        "top_products": queries.get_top_products(filters),
    }


@app.get("/api/orders")
def orders(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    city: Optional[str] = None,
    status: Optional[str] = None,
):
    filters = make_filters(start_date, end_date, category, segment, city, status)
    return queries.get_orders(filters)


# Serve the built React app (frontend/dist) when it exists
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/")
    def index():
        return FileResponse(FRONTEND_DIST / "index.html")
