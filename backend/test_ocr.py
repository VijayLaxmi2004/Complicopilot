from pathlib import Path
import sys
import pytest

# Add the backend directory to the Python path to allow for module imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from services.ocr import OCRService

# Define the path to the test images directory
TEST_IMAGES_DIR = Path(__file__).parent / "uploads" / "test"

@pytest.fixture(scope="module")
def ocr_service():
    """Provides an instance of the OCRService."""
    return OCRService()

def test_receipt_extraction(ocr_service):
    """
    Tests the extract_text_from_image function with multiple receipt images.
    """
    # Ensure the test directory exists
    assert TEST_IMAGES_DIR.is_dir(), f"Test image directory not found at {TEST_IMAGES_DIR}"

    # Get a list of test images (assuming .png, .jpg, .jpeg)
    image_paths = list(TEST_IMAGES_DIR.glob("*.png")) + \
                  list(TEST_IMAGES_DIR.glob("*.jpg")) + \
                  list(TEST_IMAGES_DIR.glob("*.jpeg"))

    # Ensure there are at least two images to test
    assert len(image_paths) >= 2, f"Please add at least two receipt images to the {TEST_IMAGES_DIR} directory."

    # --- Test Case 1: First Receipt ---
    receipt_path_1 = image_paths[0]
    print(f"Testing with image: {receipt_path_1.name}")
    extracted_text_1 = ocr_service.extract_text_from_image(str(receipt_path_1))

    # Basic assertion: check if text is extracted
    assert isinstance(extracted_text_1, str)
    assert len(extracted_text_1) > 0, f"No text was extracted from {receipt_path_1.name}"
    print(f"Extracted text from {receipt_path_1.name}:\n---\n{extracted_text_1[:200]}...\n---")

    # --- Test Case 2: Second Receipt ---
    receipt_path_2 = image_paths[1]
    print(f"Testing with image: {receipt_path_2.name}")
    extracted_text_2 = ocr_service.extract_text_from_image(str(receipt_path_2))

    # Basic assertion: check if text is extracted
    assert isinstance(extracted_text_2, str)
    assert len(extracted_text_2) > 0, f"No text was extracted from {receipt_path_2.name}"
    print(f"Extracted text from {receipt_path_2.name}:\n---\n{extracted_text_2[:200]}...\n---")

    # --- Optional: Add more specific assertions based on receipt content ---
    # For example, if you know a receipt contains the word "Total":
    # assert "Total" in extracted_text_1 or "TOTAL" in extracted_text_1

if __name__ == "__main__":
    pytest.main([__file__])