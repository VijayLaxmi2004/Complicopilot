# Example usage for future API integration:
# from services.ocr import OCRService
# svc = OCRService()
# text = svc.extract_text_from_image(receipt_image_path_or_bytes)
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query, Body, Form
from api.auth import get_current_firebase_user
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, and_
from database.session import get_db
from models.entities import Receipt
from services.ocr import ocr_service
from services.parser import ParserService
import uuid
import io
import shutil
from pathlib import Path

router = APIRouter(
    prefix="/api/v1/receipts",
    tags=["receipts"],
)

# Define a directory to save uploads
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Error model for consistent error responses
def error_response(code: str, message: str, details: Any = None) -> Dict[str, Any]:
    response = {"error": {"code": code, "message": message}}
    if details is not None:
        response["error"]["details"] = details
    return response

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_receipt(
    file: UploadFile = File(...),
    vendor: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    amount: Optional[float] = Form(None),
    currency: Optional[str] = Form("INR"),
    category: Optional[str] = Form("uncategorized"),
    gstin: Optional[str] = Form("") ,
    tax_amount: Optional[float] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_firebase_user)
) -> Dict[str, Any]:
    """
    Upload a receipt image, run OCR and parser, and persist metadata.
    Returns structured and raw data. Requires authentication.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail=error_response("MISSING_FILE", "No file uploaded"))

    # Check file type (accept only images)
    allowed_types = {"image/png", "image/jpeg", "image/jpg"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail=error_response("UNSUPPORTED_TYPE", f"File type {file.content_type} not allowed"))

    # Determine file size without consuming stream
    try:
        file.file.seek(0, io.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
    except Exception:
        size = 0

    safe_amount = float(amount) if amount is not None else 0.0
    safe_vendor = vendor or "Unknown Vendor"
    safe_date = date or "1970-01-01"

    # Save the uploaded file
    file_path = UPLOADS_DIR / f"{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Perform OCR on the uploaded file
    try:
        extracted_text = ocr_service.extract_text_from_image(str(file_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=error_response("OCR_FAILED", f"OCR failed: {str(e)}"))

    # Parse structured data from OCR text
    parser = ParserService()
    try:
        parsed = parser.parse(extracted_text)
    except Exception as e:
        parsed = {}
        # Optionally log error
        raise HTTPException(status_code=500, detail=error_response("PARSER_FAILED", f"Parser failed: {str(e)}"))

    obj = Receipt(
        vendor=parsed.get("vendor") or safe_vendor,
        date=parsed.get("date") or safe_date,
        amount=float(parsed.get("total") or safe_amount),
        currency=currency or "INR",
        category=category or "uncategorized",
        gstin=gstin or "",
        tax_amount=tax_amount,
        status="needs_review",
        filename=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        extracted={
            "file": {"size": size},
            "ocr_text": extracted_text,
            "parsed": parsed,
        },
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return {
        "id": obj.id,
        "vendor": obj.vendor,
        "date": obj.date,
        "amount": obj.amount,
        "currency": obj.currency,
        "category": obj.category,
        "gstin": obj.gstin,
        "tax_amount": obj.tax_amount,
        "status": obj.status,
        "filename": obj.filename,
        "mime_type": obj.mime_type,
        "extracted": obj.extracted or {},
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }

@router.get("/")
async def list_receipts(
    q: Optional[str] = None,
    gstin: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_firebase_user)
) -> Dict[str, Any]:
    """List receipts with optional filtering and pagination."""
    conditions = []
    if gstin:
        conditions.append(Receipt.gstin == gstin)
    if status:
        conditions.append(Receipt.status == status)
    if q:
        like = f"%{q}%"
        conditions.append(or_(Receipt.vendor.ilike(like), Receipt.category.ilike(like)))

    where_clause = and_(*conditions) if conditions else None

    # Total count
    total = db.scalar(select(func.count()).select_from(Receipt).where(where_clause)) if where_clause else db.scalar(select(func.count()).select_from(Receipt))

    # Page query
    stmt = select(Receipt).where(where_clause) if where_clause else select(Receipt)
    stmt = stmt.order_by(Receipt.created_at.desc()).offset((page - 1) * size).limit(size)
    rows = db.execute(stmt).scalars().all()

    def to_dict(obj: Receipt) -> Dict[str, Any]:
        return {
            "id": obj.id,
            "vendor": obj.vendor,
            "date": obj.date,
            "amount": obj.amount,
            "currency": obj.currency,
            "category": obj.category,
            "gstin": obj.gstin,
            "tax_amount": obj.tax_amount,
            "status": obj.status,
            "filename": obj.filename,
            "mime_type": obj.mime_type,
            "extracted": obj.extracted or {},
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }

    return {
        "items": [to_dict(r) for r in rows],
        "total": int(total or 0),
        "page": page,
        "size": size,
    }

@router.get("/{id}")
async def get_receipt(
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_firebase_user)
) -> Dict[str, Any]:
    """Get details for a specific receipt by ID."""
    obj = db.get(Receipt, id)
    if not obj:
        raise HTTPException(status_code=404, detail=error_response("NOT_FOUND", f"Receipt with ID {id} not found"))
    return {
        "id": obj.id,
        "vendor": obj.vendor,
        "date": obj.date,
        "amount": obj.amount,
        "currency": obj.currency,
        "category": obj.category,
        "gstin": obj.gstin,
        "tax_amount": obj.tax_amount,
        "status": obj.status,
        "filename": obj.filename,
        "mime_type": obj.mime_type,
        "extracted": obj.extracted or {},
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }

@router.patch("/{id}")
async def update_receipt(
    id: str,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_firebase_user)
) -> Dict[str, Any]:
    """Update a receipt with user-verified information."""
    obj = db.get(Receipt, id)
    if not obj:
        raise HTTPException(status_code=404, detail=error_response("NOT_FOUND", f"Receipt with ID {id} not found"))

    allowed = {"vendor", "date", "amount", "currency", "category", "gstin", "tax_amount", "status"}
    for k, v in payload.items():
        if k in allowed:
            setattr(obj, k, v)

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return {
        "id": obj.id,
        "vendor": obj.vendor,
        "date": obj.date,
        "amount": obj.amount,
        "currency": obj.currency,
        "category": obj.category,
        "gstin": obj.gstin,
        "tax_amount": obj.tax_amount,
        "status": obj.status,
        "filename": obj.filename,
        "mime_type": obj.mime_type,
        "extracted": obj.extracted or {},
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_receipt(id: str, db: Session = Depends(get_db), current_user=Depends(get_current_firebase_user)) -> None:
    """Delete a receipt by ID."""
    obj = db.get(Receipt, id)
    if not obj:
        raise HTTPException(status_code=404, detail=error_response("NOT_FOUND", f"Receipt with ID {id} not found"))
    db.delete(obj)
    db.commit()
    return None
