from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import SessionLocal, create_tables
from app.routers import admin, ai, auth, bookings, flights, reviews
from app.utils.seed import seed_database

# ── Create the FastAPI app ─────────────────────────────
app = FastAPI(
    title="Airline Reservation System",
    description="A modern airline reservation system with seat selection, booking management, and admin dashboard.",
    version="2.0.0",
)

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Mount static files ─────────────────────────────────
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# ── Register API routers ──────────────────────────────
app.include_router(auth.router)
app.include_router(flights.router)
app.include_router(bookings.router)
app.include_router(admin.router)
app.include_router(ai.router)
app.include_router(reviews.router)



# ── Startup event ──────────────────────────────────────
@app.on_event("startup")
def on_startup():
    """Create tables and seed data on first run."""
    create_tables()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


from fastapi import HTTPException


# ── Serve the SPA ──────────────────────────────────────
@app.get("/")
@app.get("/{path:path}")
def serve_spa(path: str = ""):
    """Serve the single-page application for all non-API routes."""
    if path.startswith("api/") or path.startswith("static/"):
        raise HTTPException(status_code=404, detail="API route not found")

    html_path = BASE_DIR / "templates" / "index.html"
    if html_path.exists():
        return FileResponse(str(html_path))
    return {"message": "Airline Reservation System API", "docs": "/docs"}

