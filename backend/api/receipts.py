# Example usage for future API integration:
# from services.ocr import OCRService
# svc = OCRService()
# text = svc.extract_text_from_image(receipt_image_path_or_bytes)
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query, Body, Form
from fastapi.responses import FileResponse
# AUTHENTICATION DISABLED FOR DEVELOPMENT
# from api.auth import get_current_firebase_user
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


# New endpoint for multiple file upload and batch processing
@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def create_receipts_batch(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload multiple receipt images, run OCR and parser, and return batch results as JSON.
    Returns individual success/error status for each file.
    """
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    max_size = 10 * 1024 * 1024  # 10 MB per file
    max_files = 10  # Maximum files per batch
    parser = ParserService()
    results = []
    errors = []

    # Limit number of files
    files_to_process = files[:max_files]
    if len(files) > max_files:
        errors.append({"error": f"Only first {max_files} files will be processed"})

    for file in files_to_process:
        if not file or not file.filename:
            errors.append({"filename": None, "error": "No file uploaded"})
            continue
        if file.content_type not in allowed_types:
            errors.append({"filename": file.filename, "error": f"File type {file.content_type} not allowed"})
            continue
        try:
            file.file.seek(0, io.SEEK_END)
            size = file.file.tell()
            file.file.seek(0)
        except Exception:
            size = 0
        if size > max_size:
            errors.append({"filename": file.filename, "error": "File too large (max 10MB)"})
            continue

        # Save file
        file_path = UPLOADS_DIR / f"{uuid.uuid4()}_{file.filename}"
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # OCR processing
            text = ocr_service.extract_text_from_image(str(file_path))
            parsed = parser.parse(text)

            # Clean amount for database
            amount_str = parsed.get("total") or "0"
            amount_clean = amount_str.replace(",", "") if isinstance(amount_str, str) else amount_str

            # Create receipt in database
            receipt = Receipt(
                id=str(uuid.uuid4()),
                vendor=parsed.get("vendor", "Unknown"),
                date=parsed.get("date", ""),
                amount=float(amount_clean),
                currency="INR",
                category="uncategorized",
                gstin=parsed.get("gstin", ""),
                tax_amount=None,
                status="needs_review",
                filename=file.filename,
                mime_type=file.content_type,
                extracted=parsed
            )

            db.add(receipt)
            db.commit()
            db.refresh(receipt)

            results.append({
                "success": True,
                "id": receipt.id,
                "filename": file.filename,
                "vendor": receipt.vendor,
                "date": receipt.date,
                "amount": receipt.amount,
                "currency": receipt.currency,
                "category": receipt.category,
                "gstin": receipt.gstin,
                "status": receipt.status,
                "extracted": receipt.extracted or {}
            })

        except Exception as e:
            # Clean up file on error
            if file_path.exists():
                file_path.unlink()
            errors.append({
                "success": False,
                "filename": file.filename,
                "error": str(e)
            })

    return {
        "total": len(files_to_process),
        "successful": len(results),
        "failed": len([e for e in errors if "filename" in e]),
        "results": results,
        "errors": errors
    }


# Single file upload endpoint
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload a single receipt image, run OCR and parser, and return the result.
    """
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    max_size = 10 * 1024 * 1024  # 10 MB
    
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail=error_response("MISSING_FILE", "No file uploaded"))
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail=error_response("INVALID_TYPE", f"File type {file.content_type} not allowed"))
    
    # Check file size
    file.file.seek(0, io.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > max_size:
        raise HTTPException(status_code=413, detail=error_response("FILE_TOO_LARGE", "File size exceeds 10MB"))
    
    # Save file
    file_path = UPLOADS_DIR / f"{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Run OCR
        text = ocr_service.extract_text_from_image(str(file_path))
        
        # Parse the extracted text
        parser = ParserService()
        parsed = parser.parse(text)
        
        # Create receipt in database
        # Remove commas from amount (Indian number format: 1,170.00)
        amount_str = parsed.get("total") or "0"
        amount_clean = amount_str.replace(",", "") if isinstance(amount_str, str) else amount_str

        receipt = Receipt(
            id=str(uuid.uuid4()),
            vendor=parsed.get("vendor", "Unknown"),
            date=parsed.get("date", ""),
            amount=float(amount_clean),
            currency=parsed.get("currency", "INR"),
            category=parsed.get("category", "uncategorized"),
            gstin=parsed.get("gstin", ""),
            tax_amount=parsed.get("tax_amount"),
            status="needs_review",
            filename=file.filename,
            mime_type=file.content_type,
            extracted=parsed
        )
        
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        
        return {
            "id": receipt.id,
            "vendor": receipt.vendor,
            "date": receipt.date,
            "amount": receipt.amount,
            "currency": receipt.currency,
            "category": receipt.category,
            "gstin": receipt.gstin,
            "tax_amount": receipt.tax_amount,
            "status": receipt.status,
            "filename": receipt.filename,
            "mime_type": receipt.mime_type,
            "extracted": receipt.extracted or {},
            "ocr_text": text
        }
    
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=error_response("PROCESSING_ERROR", str(e)))


@router.get("/")
async def list_receipts(
    q: Optional[str] = None,
    gstin: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
async def delete_receipt(
    id: str, 
    db: Session = Depends(get_db)
) -> None:
    """Delete a receipt by ID."""
    obj = db.get(Receipt, id)
    if not obj:
        raise HTTPException(status_code=404, detail=error_response("NOT_FOUND", f"Receipt with ID {id} not found"))
    db.delete(obj)
    db.commit()
    return None
