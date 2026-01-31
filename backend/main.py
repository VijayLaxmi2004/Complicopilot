from typing import Dict, Any
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Routers
from api.health import router as health_router
from api.receipts import router as receipts_router

from api.auth import router as auth_router
from models.entities import Base
from database.session import engine

load_dotenv()

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@db:5432/complicopilot")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

app = FastAPI(title="CompliCopilot API", version=APP_VERSION)

# CORS for local dev (tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5500",
        "http://localhost:5501",
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach config (optional access as app.state.settings)
app.state.settings = {
    "DATABASE_URL": DATABASE_URL,
    "UPLOAD_DIR": UPLOAD_DIR,
    "LOG_LEVEL": LOG_LEVEL,
    "VERSION": APP_VERSION,
}

# Ensure DB tables exist in local/dev (safe if already migrated)
@app.on_event("startup")
def _create_tables_if_missing() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # In production prefer Alembic migrations; swallow errors here to avoid masking real startup issues
        pass

@app.get("/", tags=["root"])
def root() -> Dict[str, Any]:
    return {"status": "ok", "service": "backend", "version": APP_VERSION}

# Include API routers (already prefixed internally)
app.include_router(health_router)
app.include_router(receipts_router)
app.include_router(auth_router)
