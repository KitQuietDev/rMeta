# handlers/pdf_handler.py

"""
PDF Metadata Scrubber for rMeta

Removes embedded metadata and scans for PII in extracted text.
✅ Format: .pdf
🔐 Non-destructive to content
"""

import logging
import os
from pathlib import Path
import asyncio
import PyPDF2
from utils.pii_scanner import scan_text_for_pii

logger = logging.getLogger(__name__)
__all__ = ["scrub", "get_additional_messages"]

SUPPORTED_EXTENSIONS = {"pdf"}

# Indicates this handler supports PII detection
PII_DETECT = True

async def scrub(file_path: str) -> None:
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    if not path.is_file() or not os.access(file_path, os.R_OK | os.W_OK):
        raise PermissionError(f"Cannot read/write PDF file: {file_path}")
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    # Make the nested function sync since PyPDF2 is sync
    def scrub_pdf():
        with open(file_path, "rb") as input_pdf:
            reader = PyPDF2.PdfReader(input_pdf)
            writer = PyPDF2.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.add_metadata({})
            with open(file_path, "wb") as output_pdf:
                writer.write(output_pdf)
        logger.info(f"✅ Metadata removed from PDF: {file_path}")

    # Run the sync function in a thread pool
    await asyncio.to_thread(scrub_pdf)

    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Scrubbed output missing or empty: {file_path}")

async def get_additional_messages(file_path: str) -> list[str]:
    messages = [f"✅ Metadata stripped from PDF: {Path(file_path).name}"]

    def extract_and_scan():
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return scan_text_for_pii(text)

    try:
        pii_found = await asyncio.to_thread(extract_and_scan)
        for pii_type in pii_found:
            messages.append(f"⚠️ PII detected: {pii_type.title()} found in file")
    except Exception as e:
        logger.warning(f"⚠️ Could not scan PDF for PII: {e}")

    return messages