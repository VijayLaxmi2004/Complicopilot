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


ALLOWED_MIME = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


def validate_file(filename: str, mime_type: str, size: int) -> Tuple[bool, str]:
    """
    Basic file validation used before saving.
    Returns (is_valid, reason_if_invalid).
    """
    if mime_type not in ALLOWED_MIME:
        return False, f"Unsupported type: {mime_type}"
    if size > MAX_SIZE_BYTES:
        return False, "File too large (max 10MB)"
    return True, ""


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


# Phase 1.2: implement disk storage under UPLOAD_DIR
def save_file(bytes_data: bytes, dest_path: str) -> None:
    """
    Save file bytes to dest_path. To be implemented in Phase 1.2.
    """
    # with open(dest_path, "wb") as f:
    #     f.write(bytes_data)
    raise NotImplementedError("Implement in Phase 1.2")
