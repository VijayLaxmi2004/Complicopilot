from http.server import BaseHTTPRequestHandler
import json
import io
import cgi
import uuid
from datetime import datetime
from urllib.parse import urlparse

ALLOWED_ORIGIN = "*"  # Restrict as needed

# In-memory store (ephemeral per cold start)
STORE = {
    "receipts": {}
}


def _write_json(handler: BaseHTTPRequestHandler, status: int, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _parse_multipart(handler: BaseHTTPRequestHandler):
    ctype, pdict = cgi.parse_header(handler.headers.get('Content-Type', ''))
    if ctype != 'multipart/form-data':
        return None, {}
    # Ensure boundary is bytes
    if 'boundary' in pdict:
        pdict['boundary'] = pdict['boundary'].encode('utf-8')
    length = int(handler.headers.get('Content-Length', '0'))
    data = handler.rfile.read(length)
    fp = io.BytesIO(data)
    form = cgi.FieldStorage(fp=fp, headers=handler.headers, environ={'REQUEST_METHOD': 'POST'}, keep_blank_values=True)
    files = {}
    fields = {}
    for key in form.keys():
        item = form[key]
        if getattr(item, 'filename', None):
            files[key] = {
                'filename': item.filename,
                'content': item.file.read(),
                'type': item.type or 'application/octet-stream'
            }
        else:
            fields[key] = item.value
    return files, fields


class handler(BaseHTTPRequestHandler):  # Vercel Python entrypoint
    def do_OPTIONS(self):  # CORS preflight
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split('/') if p]
        # Routes: /api/receipts or /api/receipts/{id}
        if len(parts) >= 2 and parts[-2] == 'receipts':
            if parts[-1] == 'receipts':
                # List
                receipts = list(STORE['receipts'].values())
                return _write_json(self, 200, {"items": receipts, "count": len(receipts)})
            else:
                rid = parts[-1]
                item = STORE['receipts'].get(rid)
                if not item:
                    return _write_json(self, 404, {"error": {"code": "not_found", "message": "Receipt not found"}})
                return _write_json(self, 200, item)
        return _write_json(self, 404, {"error": {"code": "not_found", "message": "Route not found"}})

    def do_POST(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split('/') if p]
        if not (len(parts) >= 2 and parts[-1] == 'receipts'):
            return _write_json(self, 404, {"error": {"code": "not_found", "message": "Route not found"}})

        files, fields = _parse_multipart(self)
        if files is None:
            return _write_json(self, 415, {"error": {"code": "unsupported_media_type", "message": "Expected multipart/form-data"}})
        upload = files.get('file')
        if not upload:
            return _write_json(self, 400, {"error": {"code": "missing_file", "message": "Field 'file' is required"}})

        rid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + 'Z'
        item = {
            "id": rid,
            "vendor": fields.get('vendor', 'Unknown Vendor'),
            "date": fields.get('date', now[:10]),
            "amount": float(fields.get('amount', '0') or 0),
            "currency": fields.get('currency', 'INR'),
            "category": fields.get('category', 'uncategorized'),
            "gstin": fields.get('gstin', ''),
            "tax_amount": float(fields.get('tax_amount', '0') or 0),
            "status": "needs_review",
            "file": {
                "name": upload['filename'],
                "type": upload['type'],
                "size": len(upload['content'])
            },
            "created_at": now
        }
        STORE['receipts'][rid] = item
        return _write_json(self, 201, item)


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
) -> Any:
    """
    Upload multiple receipt images, run OCR and parser, and return batch results as downloadable file.
    """
    allowed_types = {"image/png", "image/jpeg", "image/jpg"}
    max_size = 10 * 1024 * 1024  # 10 MB per file
    parser = ParserService()
    batch_results = []
    file_paths = []
    errors = []

    for file in files:
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
            errors.append({"filename": file.filename, "error": "File too large"})
            continue
        file_path = UPLOADS_DIR / f"{uuid.uuid4()}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(str(file_path))

    # Batch OCR processing
    from services.ocr import ocr_service
    extracted_texts = ocr_service.extract_texts_from_images(file_paths)

    for idx, text in enumerate(extracted_texts):
        try:
            parsed = parser.parse(text)
        except Exception as e:
            parsed = {"error": str(e)}
        batch_results.append({
            "filename": files[idx].filename,
            "ocr_text": text,
            "parsed": parsed
        })

    # Generate CSV file from batch results
    from services.compliance import generate_csv_from_batch
    csv_path = generate_csv_from_batch(batch_results)
    return FileResponse(csv_path, filename="receipts_batch.csv", media_type="text/csv")

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
