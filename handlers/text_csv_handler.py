# handlers/text_csv_handler.py

"""
Plaintext & CSV Metadata Scrubber for rMeta

Strips metadata by rewriting content to a clean file.
✅ Formats: .txt, .csv
🔐 Non-destructive to content
"""

import logging
import os
from pathlib import Path
import asyncio
from typing import List
from utils.pii_scanner import scan_text_for_pii

logger = logging.getLogger(__name__)
__all__ = ["scrub", "get_additional_messages"]

SUPPORTED_EXTENSIONS = {"txt", "csv"}

# Indicates this handler supports PII detection
PII_DETECT = True

async def scrub(file_path: str) -> None:
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")

    if not path.exists():
        raise FileNotFoundError(f"Text/CSV file not found: {file_path}")
    if not os.access(file_path, os.R_OK | os.W_OK):
        raise PermissionError(f"Cannot access file: {file_path}")
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    # Make the nested function sync since it's just file I/O
    def scrub_text_csv() -> None:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        temp_path = path.with_suffix(".tmp." + ext)
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)

        os.replace(temp_path, path)
        logger.info(f"📄 Text/CSV scrubbed: {file_path}")

    # Run the sync function in a thread pool
    await asyncio.to_thread(scrub_text_csv)

    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Scrubbed file missing or empty: {file_path}")

async def get_additional_messages(file_path: str) -> List[str]:
    messages: List[str] = [f"✅ Metadata stripped from {Path(file_path).name}"]

    def scan_file():
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    try:
        text = await asyncio.to_thread(scan_file)
        pii_found = scan_text_for_pii(text)
        for pii_type in pii_found:
            messages.append(f"⚠️ PII detected: {pii_type.title()} found in file")
    except Exception as e:
        logger.warning(f"⚠️ Could not scan file for PII: {e}")

    return messages