from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Union, Tuple, List
import cv2
import numpy as np
import pytesseract
from PIL import Image
import io

# PDF support
try:
    from pdf2image import convert_from_path, convert_from_bytes
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _ensure_tesseract_cmd():
    """Allow overriding Tesseract path via env for Windows or custom installs."""
    cmd = os.getenv("TESSERACT_CMD")
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd
        logger.info(f"Tesseract command set to: {cmd}")


def _is_pdf_file(file_path: Union[str, Path]) -> bool:
    """Check if a file is a PDF based on extension or magic bytes."""
    path_str = str(file_path).lower()
    if path_str.endswith('.pdf'):
        return True
    # Check magic bytes
    try:
        with open(file_path, 'rb') as f:
            header = f.read(5)
            return header == b'%PDF-'
    except:
        return False


def _is_pdf_bytes(data: bytes) -> bool:
    """Check if bytes data is a PDF."""
    return data[:5] == b'%PDF-'


def _convert_pdf_to_images(pdf_input: Union[str, Path, bytes], dpi: int = 200) -> List[Image.Image]:
    """
    Convert PDF to list of PIL Images.

    Args:
        pdf_input: PDF file path or bytes
        dpi: Resolution for conversion (higher = better quality but slower)

    Returns:
        List of PIL Image objects (one per page)
    """
    if not PDF_SUPPORT:
        raise ImportError("pdf2image is not installed. Install with: pip install pdf2image")

    try:
        if isinstance(pdf_input, bytes):
            images = convert_from_bytes(pdf_input, dpi=dpi)
        else:
            images = convert_from_path(str(pdf_input), dpi=dpi)

        logger.info(f"Converted PDF to {len(images)} image(s)")
        return images
    except Exception as e:
        logger.error(f"PDF conversion failed: {e}")
        raise


def _autorotate_image(img: Image.Image) -> Image.Image:
    """Check for EXIF orientation data and rotate the image accordingly."""
    try:
        exif = img._getexif()
        if exif is None:
            return img

        orientation_key = 274  # cf. ExifTags.TAGS
        if orientation_key in exif:
            orientation = exif[orientation_key]
            
            rotation_map = {
                3: Image.ROTATE_180,
                6: Image.ROTATE_270,
                8: Image.ROTATE_90,
            }
            
            if orientation in rotation_map:
                logger.info(f"Rotating image per EXIF orientation: {orientation}")
                img = img.transpose(rotation_map[orientation])
                
    except Exception as e:
        # Ignore errors if EXIF data is unreadable
        logger.warning(f"Could not read EXIF data: {e}")
        
    return img


def _as_numpy_bgr(img: Union[str, Path, bytes, Image.Image, np.ndarray]) -> np.ndarray:
    """Load various input types into a BGR numpy image for OpenCV, with autorotation."""
    if isinstance(img, np.ndarray):
        return img if len(img.shape) == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    pil_img = None
    if isinstance(img, Image.Image):
        pil_img = img
    elif isinstance(img, (str, Path)):
        img_path = str(img)
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Image file not found: {img_path}")
        pil_img = Image.open(img_path)
    elif isinstance(img, bytes):
        pil_img = Image.open(io.BytesIO(img))

    if pil_img:
        # Apply autorotation based on EXIF data
        pil_img = _autorotate_image(pil_img)
        # Convert PIL to OpenCV format (RGB -> BGR)
        rgb_array = np.array(pil_img.convert('RGB'))
        return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)

    raise TypeError(f"Unsupported image type: {type(img)}")


def _resize_to_optimal_dpi(img: np.ndarray, optimal_width: int = 1000) -> np.ndarray:
    """Resize image to an optimal width for OCR while maintaining aspect ratio."""
    h, w = img.shape[:2]
    
    # If the image is already reasonably sized, do nothing
    if w > optimal_width * 0.8 and w < optimal_width * 1.2:
        return img

    scale = optimal_width / w
    new_w, new_h = int(w * scale), int(h * scale)
    
    # Use INTER_AREA for shrinking and INTER_CUBIC for enlarging
    interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
    
    resized = cv2.resize(img, (new_w, new_h), interpolation=interpolation)
    logger.info(f"Resized image from {w}x{h} to {new_w}x{new_h}")
    return resized


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


def _sharpen_image(gray: np.ndarray) -> np.ndarray:
    """Apply a sharpening kernel to the image."""
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    return cv2.filter2D(gray, -1, kernel)


def _denoise_image(gray: np.ndarray) -> np.ndarray:
    """Apply a non-local means denoising to the image."""
    return cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)


def _correct_perspective(bgr_img: np.ndarray) -> np.ndarray:
    """Attempt to correct perspective of a receipt-like object."""
    try:
        gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 75, 200)

        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) == 4:
                screen_cnt = approx
                
                # Ensure the contour is convex
                if not cv2.isContourConvex(screen_cnt):
                    continue

                # Get bounding box and calculate aspect ratio
                x, y, w, h = cv2.boundingRect(screen_cnt)
                aspect_ratio = w / float(h)
                
                # Check for a reasonable aspect ratio for a receipt
                if 0.2 < aspect_ratio < 5.0:
                    
                    pts = screen_cnt.reshape(4, 2)
                    rect = np.zeros((4, 2), dtype="float32")
                    
                    s = pts.sum(axis=1)
                    rect[0] = pts[np.argmin(s)]
                    rect[2] = pts[np.argmax(s)]
                    
                    diff = np.diff(pts, axis=1)
                    rect[1] = pts[np.argmin(diff)]
                    rect[3] = pts[np.argmax(diff)]
                    
                    (tl, tr, br, bl) = rect
                    
                    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
                    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
                    max_width = max(int(width_a), int(width_b))
                    
                    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
                    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
                    max_height = max(int(height_a), int(height_b))

                    dst = np.array([
                        [0, 0],
                        [max_width - 1, 0],
                        [max_width - 1, max_height - 1],
                        [0, max_height - 1]], dtype="float32")
                        
                    m = cv2.getPerspectiveTransform(rect, dst)
                    warped = cv2.warpPerspective(bgr_img, m, (max_width, max_height))
                    
                    logger.info("Perspective correction applied.")
                    return warped

        logger.warning("No suitable contour found for perspective correction.")
        return bgr_img

    except Exception as e:
        logger.error(f"Perspective correction failed: {e}")
        return bgr_img


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


def _preprocess_pipeline_clahe_pro(bgr: np.ndarray) -> np.ndarray:
    """More aggressive preprocessing with CLAHE, denoising, and sharpening."""
    
    # Correct perspective first
    corrected_bgr = _correct_perspective(bgr)
    
    gray = cv2.cvtColor(corrected_bgr, cv2.COLOR_BGR2GRAY)
    
    # Denoise
    denoised = _denoise_image(gray)
    
    # CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(10, 10))
    enhanced = clahe.apply(denoised)
    
    # Sharpen
    sharpened = _sharpen_image(enhanced)
    
    # Threshold
    _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


class OCRService:
    """Service for extracting text from images and PDFs using Tesseract OCR."""

    def __init__(self, tesseract_configs: List[str] = None):
        """
        Initialize OCR service.

        Args:
            tesseract_configs: A list of Tesseract configuration strings to try.
        """
        if tesseract_configs is None:
            self.tesseract_configs = ["--oem 3 --psm 6", "--oem 3 --psm 3", "--oem 3 --psm 4"]
        else:
            self.tesseract_configs = tesseract_configs
            
        _ensure_tesseract_cmd()
        logger.info("OCRService initialized")
        logger.info(f"PDF support available: {PDF_SUPPORT}")

    def extract_text_from_pdf(self, pdf_input: Union[str, Path, bytes]) -> str:
        """
        Extract text from a PDF file by converting pages to images and running OCR.

        Args:
            pdf_input: PDF file path or bytes

        Returns:
            Combined extracted text from all pages
        """
        if not PDF_SUPPORT:
            raise ImportError("PDF support requires pdf2image. Install with: pip install pdf2image")

        try:
            # Convert PDF to images
            images = _convert_pdf_to_images(pdf_input)

            if not images:
                logger.warning("PDF conversion returned no images")
                return ""

            # Extract text from each page
            all_text = []
            for i, page_image in enumerate(images):
                logger.info(f"Processing PDF page {i + 1}/{len(images)}")
                page_text = self._extract_text_from_pil_image(page_image)
                if page_text.strip():
                    all_text.append(f"--- Page {i + 1} ---\n{page_text}")

            combined_text = "\n\n".join(all_text)
            logger.info(f"PDF OCR complete: {len(combined_text)} characters from {len(images)} page(s)")
            return combined_text

        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            return ""

    def _extract_text_from_pil_image(self, pil_image: Image.Image) -> str:
        """Extract text from a PIL Image."""
        return self.extract_text_from_image(pil_image)

    def extract_text_from_image(self, img: Union[str, Path, bytes, Image.Image, np.ndarray], min_confidence: int = 60) -> str:
        """
        Extract text from a single image or PDF using multiple preprocessing techniques.

        Args:
            img: Image/PDF input (file path, bytes, PIL Image, or numpy array)
            min_confidence: The minimum confidence score to consider the OCR successful.

        Returns:
            Extracted text string
        """
        try:
            # Check if input is a PDF
            if isinstance(img, (str, Path)) and _is_pdf_file(img):
                logger.info(f"Detected PDF file: {img}")
                return self.extract_text_from_pdf(img)

            if isinstance(img, bytes) and _is_pdf_bytes(img):
                logger.info("Detected PDF bytes")
                return self.extract_text_from_pdf(img)

            # Convert to OpenCV format for images
            bgr_image = _as_numpy_bgr(img)
            if bgr_image is None:
                raise ValueError("Failed to load image")
            
            # Resize for optimal OCR
            bgr_image = _resize_to_optimal_dpi(bgr_image)
            
            # Try multiple preprocessing approaches
            preprocessors = [
                ("binarize", _preprocess_pipeline_binarize),
                ("otsu", _preprocess_pipeline_otsu),
                ("clahe", _preprocess_pipeline_clahe),
                ("clahe_pro", _preprocess_pipeline_clahe_pro),
            ]
            
            best_text = ""
            best_confidence = 0
            
            for name, preprocess_func in preprocessors:
                try:
                    # Preprocess image
                    processed = preprocess_func(bgr_image)
                    
                    # Apply deskewing
                    deskewed = _deskew(processed)

                    for tesseract_config in self.tesseract_configs:
                        # Extract text
                        text = pytesseract.image_to_string(deskewed, config=tesseract_config)
                        
                        # Get confidence score
                        try:
                            data = pytesseract.image_to_data(deskewed, output_type=pytesseract.Output.DICT, config=tesseract_config)
                            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                        except:
                            avg_confidence = len(text.strip())  # Fallback: use text length as confidence
                        
                        psm = tesseract_config.split(" ")[-1]
                        logger.info(f"OCR with {name} (PSM {psm}): confidence={avg_confidence:.1f}, text_length={len(text)}")
                        
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
                    best_text = pytesseract.image_to_string(gray, config=self.tesseract_configs[0])
                    logger.info("Used fallback raw OCR")
                except Exception as e:
                    logger.error(f"Fallback OCR failed: {e}")

            if best_confidence < min_confidence:
                logger.warning(f"OCR result confidence ({best_confidence:.1f}) is below threshold ({min_confidence})")

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
