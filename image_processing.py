"""
Image processing module for OCR operations
Handles text extraction and table detection from images
"""
import io
import logging

import pytesseract
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def preprocess_image(image):
    """
    Preprocess image for better OCR results

    Args:
        image: OpenCV image (numpy array)

    Returns:
        Preprocessed image
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Noise removal
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

        return denoised
    except Exception as exc:
        logger.error("Error in preprocessing: %s", str(exc))
        return image


def ocr_image(image_data: bytes) -> str:
    """
    Extract text from image using OCR

    Args:
        image_data: Image file as bytes

    Returns:
        Extracted text as string
    """
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))

        # Convert PIL Image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Preprocess image
        processed_image = preprocess_image(opencv_image)

        # Perform OCR with custom config
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed_image, config=custom_config, lang='eng')

        logger.info("OCR completed. Extracted %d characters", len(text))
        return text.strip()

    except Exception as exc:
        logger.error("Error in OCR: %s", str(exc))
        raise ValueError(f"OCR processing failed: {str(exc)}") from exc


def extract_table_from_img(image_data: bytes) -> list:
    """
    Extract tables from image

    Args:
        image_data: Image file as bytes

    Returns:
        List of detected tables (as list of rows)
    """
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))

        # Convert PIL Image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Preprocess
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

        # Detect horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

        horizontal_lines = cv2.morphologyEx(
            thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2
        )
        vertical_lines = cv2.morphologyEx(
            thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2
        )

        # Combine lines to detect table structure
        table_mask = cv2.add(horizontal_lines, vertical_lines)

        # Find contours
        contours, _ = cv2.findContours(
            table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        tables = []

        # Extract tables from detected regions
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Filter small regions
            if w > 100 and h > 100:
                table_region = opencv_image[y:y+h, x:x+w]

                # Extract text from table region
                table_text = pytesseract.image_to_string(table_region, config='--psm 6')

                # Split into rows
                rows = [row.strip() for row in table_text.split('\n') if row.strip()]

                if rows:
                    tables.append({
                        'position': {
                            'x': int(x),
                            'y': int(y),
                            'width': int(w),
                            'height': int(h)
                        },
                        'rows': rows
                    })

        logger.info("Detected %d tables", len(tables))
        return tables

    except Exception as exc:
        logger.error("Error extracting tables: %s", str(exc))
        return []