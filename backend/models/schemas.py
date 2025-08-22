from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class ReceiptBase(BaseModel):
    """Base model with common receipt fields."""
    vendor: str
    date: str  # Use ISO format YYYY-MM-DD
    amount: float
    currency: str = "INR"
    category: str
    gstin: str = ""
    tax_amount: Optional[float] = None
    status: str = "needs_review"  # pending, processing, approved, needs_review, failed


class ReceiptCreate(ReceiptBase):
    """Model for creating a receipt (from API)."""
    pass


class ReceiptUpdate(BaseModel):
    """Model for updating a receipt (PATCH)."""
    vendor: Optional[str] = None
    date: Optional[str] = None  # Use ISO format YYYY-MM-DD
    amount: Optional[float] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    gstin: Optional[str] = None
    tax_amount: Optional[float] = None
    status: Optional[str] = None


class ComplianceIssue(BaseModel):
    """Model for compliance issues found in receipts."""
    level: str  # warning, error
    code: str
    message: str
    data: Optional[Dict] = None
    resolved: bool = False


class ReceiptOut(ReceiptBase):
    """Model for returning a receipt (including generated fields)."""
    id: str
    filename: str
    mime_type: str
    issues: List[ComplianceIssue] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PaginatedResponse(BaseModel):
    """Generic paginated response model."""
    items: List
    total: int
    page: int
    size: int
