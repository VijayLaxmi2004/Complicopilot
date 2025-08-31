from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class ComplianceIssue(BaseModel):
    """Model for compliance issues found in receipts."""
    level: str = Field(examples=["warning", "error"])
    code: str
    message: str
    data: Dict = {}
    resolved: bool = False


class ReceiptBase(BaseModel):
    """Base model with common receipt fields."""
    vendor: Optional[str] = None
    date: Optional[str] = Field(None, description="YYYY-MM-DD")
    amount: Optional[float] = None
    currency: Optional[str] = "INR"
    category: Optional[str] = None
    gstin: Optional[str] = None
    tax_amount: Optional[float] = None
    status: Optional[str] = Field(default="needs_review")


class ReceiptCreate(ReceiptBase):
    """Model for creating a receipt (from API)."""
    filename: Optional[str] = None
    mime_type: Optional[str] = None


class ReceiptUpdate(ReceiptBase):
    """Model for updating a receipt (PATCH)."""
    pass


class ReceiptOut(ReceiptBase):
    """Model for returning a receipt (including generated fields)."""
    id: str
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extracted: Dict = {}
    issues: List[ComplianceIssue] = []

    class Config:
        orm_mode = True


class PaginatedReceipts(BaseModel):
    """Generic paginated response model."""
    items: List[ReceiptOut]
    total: int
    page: int
    size: int
