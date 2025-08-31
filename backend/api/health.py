from fastapi import APIRouter, status
from typing import Dict, Any
from datetime import datetime, timezone

router = APIRouter(
    prefix="/api/v1/health",
    tags=["health"],
)

@router.get("/", status_code=status.HTTP_200_OK)
def get_health() -> Dict[str, Any]:
    """
    Health check endpoint that returns the status of the backend service.
    
    Returns:
        Dict with status, service name, and version information
    """
    return {
        "status": "ok",
        "service": "backend",
        "endpoint": "/api/v1/health",
        "version": "0.1.0",
        "time": datetime.now(timezone.utc).isoformat(),
    }