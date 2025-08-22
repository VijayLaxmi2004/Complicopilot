import os
from typing import Optional, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Configuration with defaults
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://user:password@db:5432/complicopilot")
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads" if os.path.exists("/app") else "./uploads")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")

# Create FastAPI app
app = FastAPI(title="CompliCopilot API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Store config for access in endpoints if needed
app.state.config = {
    "DATABASE_URL": DATABASE_URL,
    "UPLOAD_DIR": UPLOAD_DIR,
    "LOG_LEVEL": LOG_LEVEL,
}

# Root health endpoint (legacy)
@app.get("/")
def root():
    return {"status": "ok", "service": "backend", "version": "0.1.0"}

# Import and include API routers
from api.health import router as health_router
from api.reciepts import router as receipts_router

# Include routers with their own prefixes (they include /api/v1/ already)
app.include_router(health_router)
app.include_router(receipts_router)
