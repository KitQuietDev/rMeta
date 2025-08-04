"""
PDF Metadata Scrubber + PII Scanner for rMeta

Scrubs embedded metadata using PyPDF2, scans visible text for potential PII types.
Rewrites file in place, returns warnings following rMeta's handler convention.
"""

import logging
import os
import re
from pathlib import Path
from typing import List

import pdfplumber
from PyPDF2 import PdfReader, PdfWriter

logger = logging.getLogger(__name__)
__all__ = ["scrub", "get_additional_messages"]

SUPPORTED_EXTENSIONS = {"pdf"}

# PII regex patterns
PII_PATTERNS = {
    "social security number": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "address": re.compile(r"\d{1,5}\s+\w+\s+(Street|St|Avenue|Ave|Rd|Road|Blvd|Boulevard)\b", re.IGNORECASE),
    "name": re.compile(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b"),  # Simplified: capitalized first & last
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "phone number": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
}


def scrub(file_path: str) -> None:
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    if not os.access(file_path, os.R_OK | os.W_OK):
        raise PermissionError(f"Cannot access PDF file: {file_path}")
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Only 'pdf' is supported.")

    try:
        reader = PdfReader(str(path))
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.add_metadata({})  # Clear metadata

        temp_path = path.with_suffix(".tmp.pdf")
        with open(temp_path, "wb") as f:
            writer.write(f)

        os.replace(temp_path, path)
        logger.info(f"📄 PDF scrubbed: {file_path}")
    except Exception as e:
        logger.error(f"❌ Error scrubbing PDF: {file_path} – {e}")
        raise RuntimeError(f"Failed to scrub PDF metadata: {e}")

    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Scrubbed PDF file missing or empty: {file_path}")


def get_additional_messages(file_path: str) -> List[str]:
    """
    Scans PDF for potential PII content and builds warning messages.

    Returns:
        List[str]: List of formatted warning messages (if any).
    """
    messages = []
    triggered = set()

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                for pii_type, pattern in PII_PATTERNS.items():
                    if pii_type in triggered:
                        continue
                    if pattern.search(text):
                        messages.append(
                            f"🕵️ Possible PII signal in {Path(file_path).name}: “{pii_type}” found"
                        )
                        triggered.add(pii_type)
    except Exception as e:
        logger.warning(f"⚠️ Could not scan for PII in {file_path}: {e}")

    return messages
