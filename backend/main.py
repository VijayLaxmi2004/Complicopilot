from typing import Dict, Any
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Routers
from api.health import router as health_router
from api.receipts import router as receipts_router

load_dotenv()

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@db:5432/complicopilot")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

app = FastAPI(title="CompliCopilot API", version=APP_VERSION)

# CORS for local dev (tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Attach config (optional access as app.state.settings)
app.state.settings = {
    "DATABASE_URL": DATABASE_URL,
    "UPLOAD_DIR": UPLOAD_DIR,
    "LOG_LEVEL": LOG_LEVEL,
    "VERSION": APP_VERSION,
}

@app.get("/", tags=["root"])
def root() -> Dict[str, Any]:
    return {"status": "ok", "service": "backend", "version": APP_VERSION}

# Include API routers (already prefixed internally)
app.include_router(health_router)
app.include_router(receipts_router)
