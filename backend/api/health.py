from fastapi import APIRouter, status
from typing import Dict, Any

router = APIRouter(
    prefix="/api/v1/health",
    tags=["health"],
)

@router.get("/", response_model=Dict[str, Any])
def get_health() -> Dict[str, Any]:
    """
    Health check endpoint that returns the status of the backend service.
    
    Returns:
        Dict with status, service name, and version information
    """
    return {
        "status": "ok",
        "service": "backend",
        "version": "0.1.0"
    }