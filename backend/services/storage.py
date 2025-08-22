"""
Storage service for handling file uploads.

This service will be responsible for:
- Validating file type and size
- Saving files to the uploads directory
- Managing file paths and references
"""

import os
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile


async def save_file(file: UploadFile, receipt_id: str, upload_dir: str) -> Tuple[str, str, int]:
    """
    Save an uploaded file to the uploads directory.
    
    This is a placeholder stub for Phase 1.1. Will be implemented in Phase 1.3.
    
    Args:
        file: The uploaded file
        receipt_id: The receipt ID used for creating a folder
        upload_dir: The base upload directory path
        
    Returns:
        Tuple containing (path, mime_type, size)
    """
    # For Phase 1.1, we don't save anything, just return placeholders
    return (
        f"{upload_dir}/{receipt_id}/original{Path(file.filename).suffix}",
        file.content_type or "application/octet-stream",
        0  # Will be the actual file size in Phase 1.3
    )


def validate_file(file: UploadFile) -> Optional[str]:
    """
    Validate file type and size.
    
    Args:
        file: The uploaded file
        
    Returns:
        Error message if validation fails, None otherwise
    """
    # Validate mime type
    allowed_mime_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_mime_types:
        return f"Unsupported file type: {file.content_type}. Please upload JPEG, PNG, or PDF."
    
    # File size validation will be added in Phase 1.3
    
    return None
