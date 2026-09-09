import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.database import init_db
from app.routes import inventory, matches, wishlist
from app.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

# Docs advertise every mutating endpoint. Off by default for public clones;
# enable locally with ENABLE_API_DOCS=true in backend/.env
_ENABLE_API_DOCS = os.getenv("ENABLE_API_DOCS", "false").lower() in {
    "1",
    "true",
    "yes",
}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from app.database import SessionLocal
    from app.services.match_cleanup_service import purge_expired_handled_matches

    init_db()
    db = SessionLocal()
    try:
        purge_expired_handled_matches(db)
    finally:
        db.close()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Bike Wishlist Tracker",
    description="Track dealership inventory and match it against customer wishlists.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if _ENABLE_API_DOCS else None,
    redoc_url="/redoc" if _ENABLE_API_DOCS else None,
    openapi_url="/openapi.json" if _ENABLE_API_DOCS else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventory.router)
app.include_router(wishlist.router)
app.include_router(matches.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    def serve_frontend():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        icon = FRONTEND_DIST / "favicon.ico"
        if icon.exists():
            return FileResponse(icon)
        return FileResponse(FRONTEND_DIST / "index.html")
