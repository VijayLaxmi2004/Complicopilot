"""
Database entity models using SQLAlchemy ORM.

These models define the database schema and relationships.
They will be used for migrations and queries in Phase 1.2 and beyond.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, JSON
from datetime import datetime
from typing import Optional, List
import uuid

# Phase 1.2: define SQLAlchemy entities here (Receipts, ComplianceIssues, etc.)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Integer, default=1)


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # ISO YYYY-MM-DD
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="INR")
    category: Mapped[str] = mapped_column(
        String, nullable=False, default="uncategorized")
    gstin: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cgst: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sgst: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    igst: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hsn_codes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    tax_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="needs_review")
    filename: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    extracted: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    issues: Mapped[list["ComplianceIssue"]] = relationship(
        "ComplianceIssue", back_populates="receipt", cascade="all, delete-orphan"
    )


class ComplianceIssue(Base):
    __tablename__ = "compliance_issues"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4()))
    receipt_id: Mapped[str] = mapped_column(String, ForeignKey("receipts.id"))
    level: Mapped[str] = mapped_column(
        String, nullable=False)  # warning, error
    code: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    # Relationships
    receipt: Mapped[Receipt] = relationship("Receipt", back_populates="issues")
