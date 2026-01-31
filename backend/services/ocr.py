from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Union, Tuple, List
import cv2
import numpy as np
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _ensure_tesseract_cmd():
    """Allow overriding Tesseract path via env for Windows or custom installs."""
    cmd = os.getenv("TESSERACT_CMD")
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd
        logger.info(f"Tesseract command set to: {cmd}")


def _as_numpy_bgr(img: Union[str, Path, bytes, Image.Image, np.ndarray]) -> np.ndarray:
    """Load various input types into a BGR numpy image for OpenCV."""
    if isinstance(img, np.ndarray):
        return img if len(img.shape) == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
    if isinstance(img, (str, Path)):
        img_path = str(img)
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Image file not found: {img_path}")
        return cv2.imread(img_path, cv2.IMREAD_COLOR)
    
    if isinstance(img, bytes):
        nparr = np.frombuffer(img, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if isinstance(img, Image.Image):
        # Convert PIL to OpenCV format (RGB -> BGR)
        rgb_array = np.array(img.convert('RGB'))
        return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    
    raise TypeError(f"Unsupported image type: {type(img)}")


def _resize_max(img: np.ndarray, max_side: int = 1600) -> np.ndarray:
    """Resize image if larger than max_side while maintaining aspect ratio."""
    h, w = img.shape[:2]
    scale = max_side / max(h, w)
    if scale < 1.0:
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return img


def _deskew(gray: np.ndarray) -> np.ndarray:
    """Estimate skew using image moments; rotate to correct skew."""
    coords = np.column_stack(np.where(gray < 250))
    if coords.size == 0:
        return gray
    
    rect = cv2.minAreaRect(coords.astype(np.float32))
    angle = rect[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    
    if abs(angle) < 0.5:  # Skip rotation for very small angles
        return gray
        
    h, w = gray.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def _preprocess_pipeline_binarize(bgr: np.ndarray) -> np.ndarray:
    """Basic preprocessing with adaptive thresholding."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Adaptive threshold for better text detection
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return binary


def _preprocess_pipeline_otsu(bgr: np.ndarray) -> np.ndarray:
    """Preprocessing with Otsu's thresholding."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Otsu's thresholding
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def _preprocess_pipeline_clahe(bgr: np.ndarray) -> np.ndarray:
    """Preprocessing with CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    # Apply Gaussian blur and threshold
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


class OCRService:
    """Service for extracting text from images using Tesseract OCR."""
    
    def __init__(self, tesseract_config: str = "--oem 3 --psm 6"):
        """
        Initialize OCR service.
        
        Args:
            tesseract_config: Tesseract configuration string
        """
        self.tesseract_config = tesseract_config
        _ensure_tesseract_cmd()
        logger.info("OCRService initialized")
    
    def extract_text_from_image(self, img: Union[str, Path, bytes, Image.Image, np.ndarray]) -> str:
        """
        Extract text from a single image using multiple preprocessing techniques.
        
        Args:
            img: Image input (file path, bytes, PIL Image, or numpy array)
            
        Returns:
            Extracted text string
        """
        try:
            # Convert to OpenCV format
            bgr_image = _as_numpy_bgr(img)
            if bgr_image is None:
                raise ValueError("Failed to load image")
            
            # Resize if too large
            bgr_image = _resize_max(bgr_image)
            
            # Try multiple preprocessing approaches
            preprocessors = [
                ("binarize", _preprocess_pipeline_binarize),
                ("otsu", _preprocess_pipeline_otsu),
                ("clahe", _preprocess_pipeline_clahe),
            ]
            
            best_text = ""
            best_confidence = 0
            
            for name, preprocess_func in preprocessors:
                try:
                    # Preprocess image
                    processed = preprocess_func(bgr_image)
                    
                    # Apply deskewing
                    deskewed = _deskew(processed)
                    
                    # Extract text
                    text = pytesseract.image_to_string(deskewed, config=self.tesseract_config)
                    
                    # Get confidence score
                    try:
                        data = pytesseract.image_to_data(deskewed, output_type=pytesseract.Output.DICT)
                        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    except:
                        avg_confidence = len(text.strip())  # Fallback: use text length as confidence
                    
                    logger.info(f"OCR with {name}: confidence={avg_confidence:.1f}, text_length={len(text)}")
                    
                    # Keep best result
                    if avg_confidence > best_confidence and text.strip():
                        best_text = text
                        best_confidence = avg_confidence
                        
                except Exception as e:
                    logger.warning(f"OCR preprocessing {name} failed: {e}")
                    continue
            
            # Fallback: try raw image if all preprocessing failed
            if not best_text.strip():
                try:
                    gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
                    best_text = pytesseract.image_to_string(gray, config=self.tesseract_config)
                    logger.info("Used fallback raw OCR")
                except Exception as e:
                    logger.error(f"Fallback OCR failed: {e}")
            
            logger.info(f"Final OCR result: {len(best_text)} characters extracted")
            return best_text.strip()
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def extract_texts_from_images(self, imgs: List[Union[str, Path, bytes, Image.Image, np.ndarray]]) -> List[str]:
        """
        Extract text from a list of images (batch processing).
        Returns a list of OCR results (one per image).
        """
        results = []
        for i, img in enumerate(imgs):
            try:
                logger.info(f"Processing image {i+1}/{len(imgs)}")
                text = self.extract_text_from_image(img)
                results.append(text)
            except Exception as e:
                logger.error(f"Failed to process image {i+1}: {e}")
                results.append("")
        return results


# Optional: a module-level instance if desired by callers
ocr_service = OCRService()
