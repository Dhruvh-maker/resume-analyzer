"""
PDF text extraction service.
Handles parsing uploaded PDF files and extracting readable text content.
"""

import io
import logging

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

logger = logging.getLogger(__name__)


def extract_text(file_bytes: bytes) -> str:
    """
    Extract text content from a PDF file.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If the PDF is empty, encrypted, or unreadable.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except PdfReadError as e:
        logger.error(f"Failed to read PDF: {e}")
        raise ValueError("The uploaded file is not a valid PDF or is corrupted.") from e

    # Check if encrypted
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported. Please upload an unprotected file.")

    # Check if empty
    if len(reader.pages) == 0:
        raise ValueError("The uploaded PDF has no pages.")

    # Extract text from all pages
    text_parts: list[str] = []
    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text.strip())
        else:
            logger.warning(f"Page {page_num} yielded no text (may be an image-based page).")

    full_text = "\n\n".join(text_parts)

    if not full_text.strip():
        raise ValueError(
            "Could not extract any text from the PDF. "
            "It may be a scanned/image-based resume — try a text-based PDF instead."
        )

    logger.info(f"Extracted {len(full_text)} characters from {len(reader.pages)} page(s).")
    return full_text
