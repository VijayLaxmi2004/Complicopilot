from __future__ import annotations

import io
import os
import sys
import logging
from pathlib import Path
from typing import Optional, Union, Tuple, List

import numpy as np
from PIL import Image
import cv2
import pytesseract


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _ensure_tesseract_cmd():
    # Allow overriding Tesseract path via env for Windows or custom installs.
    cmd = os.getenv("TESSERACT_CMD")
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd


def _as_numpy_bgr(img: Union[str, Path, bytes, Image.Image, np.ndarray]) -> np.ndarray:
    # Load various input types into a BGR numpy image for OpenCV.
    if isinstance(img, np.ndarray):
        if img.ndim == 2:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        if img.shape[2] == 3:
            return img
        if img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    if isinstance(img, (str, Path)):
        pil = Image.open(img).convert("RGB")
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    if isinstance(img, bytes):
        pil = Image.open(io.BytesIO(img)).convert("RGB")
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    if isinstance(img, Image.Image):
        pil = img.convert("RGB")
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    raise TypeError(f"Unsupported image type: {type(img)}")


def _resize_max(img: np.ndarray, max_side: int = 1600) -> np.ndarray:
    h, w = img.shape[:2]
    scale = max_side / max(h, w)
    if scale < 1.0:
        return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def _deskew(gray: np.ndarray) -> np.ndarray:
    # Estimate skew using image moments; rotate to correct skew.
    coords = np.column_stack(np.where(gray < 250))
    if coords.size == 0:
        return gray
    rect = cv2.minAreaRect(coords.astype(np.float32))
    angle = rect[-1]
    if angle < -45:
        angle = 90 + angle
    rotate_angle = -angle
    h, w = gray.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), rotate_angle, 1.0)
    return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def _preprocess_pipeline_binarize(bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = _resize_max(gray)
    gray = cv2.bilateralFilter(gray, d=7, sigmaColor=75, sigmaSpace=75)
    gray = _deskew(gray)
    # Adaptive threshold is robust to lighting
    bin_img = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
    )
    # Morphology to remove noise
    kernel = np.ones((2, 2), np.uint8)
    bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, kernel, iterations=1)
    # Upscale text a bit for OCR
    bin_img = cv2.resize(bin_img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    return bin_img


def _preprocess_pipeline_otsu(bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = _resize_max(gray)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, bin_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    bin_img = cv2.resize(bin_img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    return bin_img


def _preprocess_pipeline_clahe(bgr: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    bgr2 = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    gray = cv2.cvtColor(bgr2, cv2.COLOR_BGR2GRAY)
    _, bin_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    bin_img = cv2.resize(bin_img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    return bin_img


class OCRService:
    def __init__(self, lang: str = "eng", oem: int = 3, psm: int = 6):
        """
        lang: Tesseract language (e.g., 'eng')
        oem:  OCR Engine Mode (3 = default LSTM)
        psm:  Page segmentation mode (6 = assume a block of text)
        """
        _ensure_tesseract_cmd()
        self.lang = lang
        self.oem = oem
        self.psm = psm

    def _tess_config(self) -> str:
        return f"--oem {self.oem} --psm {self.psm}"

    def extract_text_from_image(
        self, img: Union[str, Path, bytes, Image.Image, np.ndarray]
    ) -> str:
        """
        High-level OCR with multiple preprocessing strategies and fallbacks.
        """
        bgr = _as_numpy_bgr(img)
        pipelines = [
            _preprocess_pipeline_binarize,
            _preprocess_pipeline_otsu,
            _preprocess_pipeline_clahe,
        ]
        best_text = ""
        for i, pipeline in enumerate(pipelines, start=1):
            try:
                processed = pipeline(bgr)
                text = pytesseract.image_to_string(processed, lang=self.lang, config=self._tess_config())
                normalized = self._normalize(text)
                logger.info("Pipeline %d produced %d chars", i, len(normalized))
                if len(normalized) > len(best_text):
                    best_text = normalized
                # Early exit if strong signal
                if self._looks_good(normalized):
                    return normalized
            except Exception as e:
                logger.warning("OCR pipeline %d failed: %s", i, e)
        return best_text

    def extract_lines_with_confidence(
        self, img: Union[str, Path, bytes, Image.Image, np.ndarray], min_conf: int = 60
    ) -> List[Tuple[str, int]]:
        """
        Returns (line_text, confidence) filtered by min_conf using image_to_data.
        """
        bgr = _as_numpy_bgr(img)
        processed = _preprocess_pipeline_binarize(bgr)
        data = pytesseract.image_to_data(
            processed, lang=self.lang, config=self._tess_config(), output_type=pytesseract.Output.DICT
        )
        lines: List[Tuple[str, int]] = []
        for i in range(len(data["text"])):
            txt = data["text"][i].strip()
            conf = int(data["conf"][i]) if data["conf"][i] != "-1" else -1
            if txt and conf >= min_conf:
                lines.append((txt, conf))
        return lines

    @staticmethod
    def _normalize(text: str) -> str:
        # Strip trailing whitespace and normalize newlines
        return "\n".join([line.rstrip() for line in text.splitlines()]).strip()

    @staticmethod
    def _looks_good(text: str) -> bool:
        # Heuristic: receipts usually contain a few of these tokens.
        tokens = ["total", "subtotal", "qty", "cash", "tax", "change", "visa", "mastercard"]
        lc = text.lower()
        hits = sum(1 for t in tokens if t in lc)
        return hits >= 2 or len(text) > 80

TEST_IMAGES_DIR = Path(__file__).parent / "uploads" / "receipts" / "test"