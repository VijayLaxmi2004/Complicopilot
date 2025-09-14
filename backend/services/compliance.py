import pandas as pd
import tempfile

# Generate CSV from batch OCR/parsed data
def generate_csv_from_batch(batch_results: List[dict]) -> str:
    """
    Given a list of dicts (each with keys like filename, ocr_text, parsed),
    generate a CSV file and return its path.
    """
    # Flatten parsed dict for each result
    rows = []
    for item in batch_results:
        row = {"filename": item.get("filename", "")}
        parsed = item.get("parsed", {})
        if isinstance(parsed, dict):
            for k, v in parsed.items():
                row[k] = v
        row["ocr_text"] = item.get("ocr_text", "")
        rows.append(row)
    df = pd.DataFrame(rows)
    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="", encoding="utf-8") as tmp:
        df.to_csv(tmp.name, index=False)
        return tmp.name
"""
Compliance service for validating and checking receipts.

This service will be responsible for:
- Validating receipt data against compliance rules
- Flagging issues with GST numbers
- Checking date validity, amount ranges, etc.
"""

from typing import Dict, Any, List
import re
from datetime import datetime


GSTIN_REGEX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"


def evaluate(extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluate receipt data for compliance issues.
    
    This is a placeholder stub for Phase 1.1. Will be implemented in Phase 1.4.
    
    Args:
        extracted_data: Extracted receipt data
        
    Returns:
        List of compliance issues
    """
    issues = []
    
    # In Phase 1.4, this will contain actual rule checks
    # For now, just stub out the basic checks

    # Check for GSTIN presence
    if not extracted_data.get("gstin"):
        issues.append({
            "level": "warning",
            "code": "GST_MISSING",
            "message": "GST number not detected on receipt",
            "data": {}
        })
    
    # Check amount > 0
    amount = extracted_data.get("amount", 0)
    if amount <= 0:
        issues.append({
            "level": "error",
            "code": "INVALID_AMOUNT",
            "message": "Receipt amount must be greater than zero",
            "data": {"amount": amount}
        })
    
    return issues


def validate_gstin(gstin: str) -> bool:
    """
    Validate GSTIN format.
    
    Args:
        gstin: GST Identification Number
        
    Returns:
        True if valid, False otherwise
    """
    # Basic GSTIN format validation (placeholder)
    # In Phase 1.4, this will have the actual regex pattern
    if not gstin:
        return False
        
    # Simple pattern for Phase 1.1
    pattern = r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$"
    return bool(re.match(pattern, gstin))
