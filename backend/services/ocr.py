"""
OCR service for extracting data from receipts.

This service will be responsible for:
- Processing receipt images/PDFs
- Extracting structured data fields
- Providing confidence scores
"""

from typing import Dict, Any
import os
import json


def extract(file_path: str) -> Dict[str, Any]:
    """
    Extract data from a receipt file.
    
    This is a placeholder stub for Phase 1.1. Will be implemented in Phase 1.4.
    
    Args:
        file_path: Path to the receipt file
        
    Returns:
        Dictionary with extracted fields
    """
    # In Phase 1.1, we return hardcoded data
    # In Phase 1.4, this will call the cloud OCR service
    return {
        "vendor": "Example Vendor",
        "date": "2025-08-22",
        "amount": 100.00,
        "currency": "INR",
        "tax_amount": 18.00,
        "gstin": "",
        "category_suggested": "meals",
        "confidence": 0.92
    }
