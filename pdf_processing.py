"""
PDF processing module for OCR operations
Handles text extraction and table detection from PDF files
"""
import logging

import pytesseract
import pdf2image
import cv2
import numpy as np

logger = logging.getLogger(__name__)


def ocr_pdf(pdf_data: bytes) -> str:
    """
    Extract text from PDF using OCR

    Args:
        pdf_data: PDF file as bytes

    Returns:
        Extracted text as string
    """
    try:
        # Convert PDF to images
        images = pdf2image.convert_from_bytes(pdf_data)

        all_text = []

        # Process each page
        for page_num, image in enumerate(images, 1):
            logger.info("Processing page %d/%d", page_num, len(images))

            # Convert PIL Image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Preprocess
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # OCR
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(thresh, config=custom_config, lang='eng')

            all_text.append(f"--- Page {page_num} ---\n{text.strip()}\n")

        full_text = "\n".join(all_text)
        logger.info(
            "PDF OCR completed. Extracted %d characters from %d pages",
            len(full_text),
            len(images)
        )

        return full_text

    except Exception as exc:
        logger.error("Error in PDF OCR: %s", str(exc))
        raise ValueError(f"PDF OCR processing failed: {str(exc)}") from exc


def extract_table_from_pdf(pdf_data: bytes) -> list:
    """
    Extract tables from PDF

    Args:
        pdf_data: PDF file as bytes

    Returns:
        List of detected tables from all pages
    """
    try:
        # Convert PDF to images
        images = pdf2image.convert_from_bytes(pdf_data)

        all_tables = []

        # Process each page
        for page_num, image in enumerate(images, 1):
            logger.info("Extracting tables from page %d/%d", page_num, len(images))

            # Convert PIL Image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Convert to grayscale and threshold
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

            # Combine lines
            table_mask = cv2.add(horizontal_lines, vertical_lines)

            # Find contours
            contours, _ = cv2.findContours(
                table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Extract tables
            page_tables = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)

                # Filter small regions
                if w > 100 and h > 100:
                    table_region = opencv_image[y:y+h, x:x+w]

                    # Extract text
                    table_text = pytesseract.image_to_string(
                        table_region, config='--psm 6'
                    )

                    # Split into rows
                    rows = [
                        row.strip() for row in table_text.split('\n') if row.strip()
                    ]

                    if rows:
                        page_tables.append({
                            'page': page_num,
                            'position': {
                                'x': int(x),
                                'y': int(y),
                                'width': int(w),
                                'height': int(h)
                            },
                            'rows': rows
                        })

            if page_tables:
                all_tables.extend(page_tables)
                logger.info("Found %d tables on page %d", len(page_tables), page_num)

        logger.info("Total tables extracted: %d", len(all_tables))
        return all_tables

    except Exception as exc:
        logger.error("Error extracting tables from PDF: %s", str(exc))
        return []