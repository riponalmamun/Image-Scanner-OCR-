"""
FastAPI OCR Application
Provides endpoints for OCR processing of images and PDFs
"""
import logging
from pathlib import Path

import pytesseract
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from image_processing import ocr_image, extract_table_from_img
from pdf_processing import ocr_pdf, extract_table_from_pdf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set tesseract executable path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/tiff", "image/bmp"}
ALLOWED_PDF_TYPES = {"application/pdf"}

app = FastAPI(
    title="OCR API",
    description="API for OCR processing of images and PDFs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_index():
    """Serve the main HTML page"""
    index_path = Path("index.html")
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse("index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OCR API"}


def validate_file(file: UploadFile, allowed_types: set) -> None:
    """Validate uploaded file"""
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )


async def read_file_with_limit(file: UploadFile, max_size: int) -> bytes:
    """Read file with size limit"""
    file_data = await file.read()
    if len(file_data) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {max_size / (1024*1024):.1f}MB"
        )
    return file_data


@app.post("/ocr-image/")
async def ocr_image_upload(file: UploadFile = File(...)) -> JSONResponse:
    """
    Extract text and tables from an uploaded image

    Args:
        file: Image file (JPEG, PNG, TIFF, BMP)

    Returns:
        JSON with extracted text and tables
    """
    try:
        # Validate file type
        validate_file(file, ALLOWED_IMAGE_TYPES)

        # Read file with size limit
        image_data = await read_file_with_limit(file, MAX_FILE_SIZE)

        logger.info("Processing image: %s (%d bytes)", file.filename, len(image_data))

        # Process image
        extracted_text = ocr_image(image_data)
        tables = extract_table_from_img(image_data)

        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "text": extracted_text,
            "tables": tables,
            "text_length": len(extracted_text) if extracted_text else 0,
            "table_count": len(tables) if tables else 0
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error processing image: %s", str(exc), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(exc)}"
        ) from exc


@app.post("/ocr-pdf/")
async def ocr_pdf_upload(file: UploadFile = File(...)) -> JSONResponse:
    """
    Extract text and tables from an uploaded PDF

    Args:
        file: PDF file

    Returns:
        JSON with extracted text and tables
    """
    try:
        # Validate file type
        validate_file(file, ALLOWED_PDF_TYPES)

        # Read file with size limit
        pdf_data = await read_file_with_limit(file, MAX_FILE_SIZE)

        logger.info("Processing PDF: %s (%d bytes)", file.filename, len(pdf_data))

        # Process PDF
        extracted_text = ocr_pdf(pdf_data)
        tables = extract_table_from_pdf(pdf_data)

        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "text": extracted_text,
            "tables": tables,
            "text_length": len(extracted_text) if extracted_text else 0,
            "table_count": len(tables) if tables else 0
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error processing PDF: %s", str(exc), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(exc)}"
        ) from exc


@app.exception_handler(Exception)
async def global_exception_handler(_request, exc):
    """Global exception handler"""
    logger.error("Unhandled exception: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )