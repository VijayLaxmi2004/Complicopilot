#!/usr/bin/env python3
"""
Simple OCR test script to verify Tesseract is working properly.
"""

import os
import sys
from pathlib import Path
from services.ocr import OCRService
from services.parser import ParserService

def test_ocr_with_uploaded_files():
    """Test OCR with files in the uploads directory."""
    uploads_dir = Path("uploads")
    
    if not uploads_dir.exists():
        print("❌ Uploads directory not found")
        return
    
    # Find image files
    image_files = list(uploads_dir.glob("*.png")) + list(uploads_dir.glob("*.jpg")) + list(uploads_dir.glob("*.jpeg"))
    
    if not image_files:
        print("❌ No image files found in uploads directory")
        return
    
    print(f"📁 Found {len(image_files)} image files")
    
    ocr_service = OCRService()
    parser_service = ParserService()
    
    for img_file in image_files[:3]:  # Test first 3 files
        print(f"\n🖼️  Testing: {img_file.name}")
        print("=" * 50)
        
        try:
            # Extract text
            extracted_text = ocr_service.extract_text_from_image(str(img_file))
            print(f"📝 OCR Text ({len(extracted_text)} chars):")
            print(repr(extracted_text))
            
            # Parse structured data
            parsed_data = parser_service.parse(extracted_text)
            print(f"\n🔍 Parsed Data:")
            for key, value in parsed_data.items():
                print(f"  {key}: {value}")
            
        except Exception as e:
            print(f"❌ Error processing {img_file.name}: {e}")

if __name__ == "__main__":
    test_ocr_with_uploaded_files()
