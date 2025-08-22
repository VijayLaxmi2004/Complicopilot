from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query, Body
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from database.session import get_db
import uuid

router = APIRouter(
    prefix="/api/v1/receipts",
    tags=["receipts"],
)

# Error model for consistent error responses
def error_response(code: str, message: str, details: Any = None) -> Dict[str, Any]:
    response = {"error": {"code": code, "message": message}}
    if details is not None:
        response["error"]["details"] = details
    return response

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload a receipt file for processing.
    
    This endpoint accepts a file upload (image or PDF), processes it,
    and returns the extracted information along with compliance issues.
    
    Args:
        file: The receipt file (multipart/form-data)
        db: Database session dependency (not used in Phase 1.1)
        
    Returns:
        Receipt object with extracted data and issues
    """
    # Phase 1.1: Return a stub response
    return {
        "id": str(uuid.uuid4()),
        "status": "needs_review",
        "filename": file.filename,
        "mime_type": file.content_type,
        "extracted": {
            "vendor": "Example Vendor",
            "date": "2025-08-22",
            "amount": 100.00,
            "currency": "INR",
            "tax_amount": 18.00,
            "gstin": "",
            "category_suggested": "uncategorized"
        },
        "issues": []
    }

@router.get("/")
async def list_receipts(
    q: Optional[str] = None,
    gstin: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List receipts with optional filtering and pagination.
    
    Args:
        q: General search query
        gstin: Filter by GSTIN
        status: Filter by status
        page: Page number (1-based)
        size: Page size
        db: Database session dependency (not used in Phase 1.1)
        
    Returns:
        Paginated list of receipts
    """
    # Phase 1.1: Return empty list stub
    return {
        "items": [],
        "total": 0,
        "page": page,
        "size": size
    }

@router.get("/{id}")
async def get_receipt(
    id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get details for a specific receipt by ID.
    
    Args:
        id: Receipt ID
        db: Database session dependency (not used in Phase 1.1)
        
    Returns:
        Receipt details
        
    Raises:
        HTTPException: 404 if receipt not found
    """
    # Phase 1.1: Always return a 404 stub
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=error_response("NOT_FOUND", f"Receipt with ID {id} not found")
    )

@router.patch("/{id}")
async def update_receipt(
    id: str,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update a receipt with user-verified information.
    
    Args:
        id: Receipt ID
        payload: Updated receipt data
        db: Database session dependency (not used in Phase 1.1)
        
    Returns:
        Updated receipt
        
    Raises:
        HTTPException: 404 if receipt not found
    """
    # Phase 1.1: Echo stub with 200
    return {
        "id": id,
        "updated": payload
    }