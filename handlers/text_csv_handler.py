"""
Text/CSV Metadata Scanner for rMeta

Inspects .txt and .csv files for metadata-like headers or document structure.
Does not alter file content. Designed to log and optionally warn about known PII patterns.

✅ Formats: .txt, .csv
🔍 Scans for metadata-like signals only
🛡️ Content is preserved exactly as-is
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)
__all__ = ["scrub", "SUPPORTED_EXTENSIONS", "get_additional_messages"]

SUPPORTED_EXTENSIONS = {"txt", "csv"}

# Define suspicious keywords that resemble metadata fields or PII headers
SUSPICIOUS_HEADERS = {
    "author", "creator", "date", "location", "email", "user", "ssn", "fullname", "dob"
}

def scrub(file_path: str) -> None:
    """
    No-op scrub — intentionally preserves file contents.

    Args:
        file_path (str): Path to the text or CSV file.
    """
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")

    if not path.exists():
        raise FileNotFoundError(f"{ext.upper()} file not found: {file_path}")
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    logger.info(f"🛡️ Preserved {ext.upper()} file: {file_path} (no scrub applied)")

def get_additional_messages(file_path: str):
    """
    Warn if suspicious headers or metadata-like signals are detected.

    Args:
        file_path (str): Path to file.

    Returns:
        list: Message strings for UI display.
    """
    messages = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        if not lines:
            messages.append(f"⚠️ {Path(file_path).name} is empty — skipping metadata scan.")
            return messages

        scanned_lines = lines[:10]  # Only scan first few lines
        for line in scanned_lines:
            for keyword in SUSPICIOUS_HEADERS:
                if keyword in line.lower():
                    messages.append(f"🕵️ Possible PII signal in {Path(file_path).name}: “{keyword}” found")

        return messages
    except Exception as e:
        logger.warning(f"Metadata scan failed for {file_path}: {e}")
        return []
