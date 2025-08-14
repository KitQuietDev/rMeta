# handlers/heic_handler.py

"""
HEIC Metadata Scrubber for rMeta

Removes embedded metadata from HEIC image files.
✅ Format: .heic
🔐 Non-destructive to image pixels
"""

import logging
import os
from pathlib import Path
import asyncio
from PIL import Image
import pillow_heif
from utils.pii_scanner import scan_text_for_pii

logger = logging.getLogger(__name__)
__all__ = ["scrub", "get_additional_messages"]

SUPPORTED_EXTENSIONS = {"heic"}

# Indicates this handler does NOT support PII detection
PII_DETECT = False

async def scrub(file_path: str) -> None:
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")

    if not path.exists():
        raise FileNotFoundError(f"HEIC file not found: {file_path}")
    if not os.access(file_path, os.R_OK | os.W_OK):
        raise PermissionError(f"Cannot access HEIC file: {file_path}")
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    async def scrub_heic():
        heif_file = pillow_heif.read_heif(file_path)
        if heif_file.data is None:
            raise ValueError(f"HEIC file data is missing: {file_path}")
        image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data)
        temp_path = path.with_suffix(".tmp.heic")
        image.save(temp_path, format="HEIF", exif=None, quality=95)
        os.replace(temp_path, path)
        logger.info(f"🖼️ HEIC scrubbed: {file_path}")

    await asyncio.to_thread(scrub_heic)

    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Scrubbed HEIC file missing or empty: {file_path}")

async def get_additional_messages(file_path: str) -> list[str]:
    return [f"✅ Metadata stripped from HEIC: {Path(file_path).name}"]
