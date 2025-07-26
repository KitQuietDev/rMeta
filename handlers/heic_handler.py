"""
HEIC Metadata Scrubber for rMeta

Strips EXIF and location data from HEIC image files.
Uses pyheif to decode and Pillow to re-save the image stripped of metadata.

✅ Format: .heic only
🔐 Converts to JPEG during scrub; original format is not preserved
"""

import logging
import os
from pathlib import Path

try:
    import pyheif
    from PIL import Image
except ImportError:
    raise ImportError("Requires pyheif and Pillow. Install with: pip install pyheif Pillow")

logger = logging.getLogger(__name__)
__all__ = ["scrub", "get_additional_messages"]

SUPPORTED_EXTENSIONS = {"heic"}

def scrub(file_path: str) -> None:
    """
    Scrubs metadata from a HEIC file in place.

    Converts HEIC image to a Pillow object and re-saves it,
    omitting any EXIF or embedded location data.

    Args:
        file_path (str): Path to the input HEIC file.

    Raises:
        FileNotFoundError, PermissionError, ValueError, RuntimeError
    """
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")

    if not path.exists():
        raise FileNotFoundError(f"HEIC file not found: {file_path}")
    if not os.access(file_path, os.R_OK | os.W_OK):
        raise PermissionError(f"Cannot access HEIC file: {file_path}")
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Only 'heic' is supported.")

    try:
        heif = pyheif.read(path)
        img = Image.frombytes(heif.mode, heif.size, heif.data, "raw")

        temp_path = path.with_suffix(".tmp.jpg")  # Use JPEG suffix
        img.save(temp_path, format="JPEG")

        os.replace(temp_path, path)
        logger.info(f"🖼️ HEIC scrubbed and converted to JPEG: {file_path}")
    except Exception as e:
        logger.error(f"❌ Error scrubbing HEIC: {file_path} – {e}")
        raise RuntimeError(f"HEIC scrub failed: {e}")

    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Scrubbed file missing or empty: {file_path}")

def get_additional_messages(file_path: str) -> list[str]:
    """
    Returns user-facing format warnings for HEIC scrubbing.

    Args:
        file_path (str): Path to the original file.

    Returns:
        list[str]: Messages to display after processing.
    """
    return [f"⚠️ HEIC file '{Path(file_path).name}' was converted to JPEG format during metadata scrub."]
