"""
Database entity models using SQLAlchemy ORM.

These models define the database schema and relationships.
They will be used for migrations and queries in Phase 1.2 and beyond.
"""

# This file is a placeholder in Phase 1.1
# It will be implemented in Phase 1.2 with actual SQLAlchemy models

# from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# import uuid
# from datetime import datetime

# Example model shape for Phase 1.2 (commented out for Phase 1.1):

# Base = declarative_base()


# class Receipt(Base):
#     __tablename__ = "receipts"
#
#     id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
#     vendor = Column(String, nullable=False)
#     date = Column(String, nullable=False)  # ISO format YYYY-MM-DD
#     amount = Column(Float, nullable=False)
#     currency = Column(String, default="INR")
#     category = Column(String, nullable=False)
#     gstin = Column(String, default="")
#     tax_amount = Column(Float, nullable=True)
#     status = Column(String, nullable=False, default="needs_review")
#     filename = Column(String)
#     mime_type = Column(String)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
#
#     # Relationships
#     issues = relationship("ComplianceIssue", back_populates="receipt", cascade="all, delete-orphan")


# class ComplianceIssue(Base):
#     __tablename__ = "compliance_issues"
#
#     id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
#     receipt_id = Column(String, ForeignKey("receipts.id"))
#     level = Column(String, nullable=False)  # warning, error
#     code = Column(String, nullable=False)
#     message = Column(String, nullable=False)
#     data = Column(JSON, nullable=True)
#     resolved = Column(Boolean, default=False)
#     created_at = Column(DateTime, server_default=func.now())
#
#     # Relationships
#     receipt = relationship("Receipt", back_populates="issues")
