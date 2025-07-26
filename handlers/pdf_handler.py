"""
PDF Metadata Scrubber for rMeta

Uses PyMuPDF (fitz) to strip all embedded metadata from PDF files.
Rewrites the file in-place with no backups or artifacts.
"""

import logging
import os
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    raise ImportError("PyMuPDF (fitz) is required. Install with: pip install PyMuPDF")

logger = logging.getLogger(__name__)
__all__ = ["scrub"]

SUPPORTED_EXTENSIONS = {"pdf"}

def scrub(file_path: str) -> None:
    """
    Scrubs metadata from a PDF file in place.

    Args:
        file_path (str): Path to the input PDF file.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
        ValueError: If the extension is unsupported.
        RuntimeError: If scrubbing or output confirmation fails.
    """
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    if not os.access(file_path, os.R_OK | os.W_OK):
        raise PermissionError(f"Cannot access PDF file: {file_path}")
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Only 'pdf' is supported.")

    try:
        doc = fitz.open(str(path))
        doc.set_metadata({key: "" for key in doc.metadata})
        temp_path = path.with_suffix(".tmp.pdf")
        doc.save(temp_path, garbage=4)
        doc.close()
        os.replace(temp_path, path)
        logger.info(f"📄 PDF scrubbed: {file_path}")
    except Exception as e:
        logger.error(f"❌ Error scrubbing PDF: {file_path} – {e}")
        raise RuntimeError(f"Failed to scrub PDF metadata: {e}")

    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Scrubbed PDF file missing or empty: {file_path}")
