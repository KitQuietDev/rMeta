"""
Image Metadata Scrubber for rMeta

Removes metadata from image files using appropriate libraries.
Supports EXIF removal via piexif and pixel-level scrubbing for formats without EXIF.
"""

import logging
import os
from pathlib import Path

try:
    import piexif
except ImportError:
    raise ImportError("piexif library is required. Install with: pip install piexif")

try:
    from PIL import Image
except ImportError:
    raise ImportError("Pillow library is required for PNG handling. Install with: pip install Pillow")

logger = logging.getLogger(__name__)

__all__ = ["scrub"]

# Supported extensions by strategy
EXIF_EXTENSIONS = {"jpg", "jpeg"}
OTHER_EXTENSIONS = {"png"}
SUPPORTED_EXTENSIONS = EXIF_EXTENSIONS | OTHER_EXTENSIONS


def scrub(file_path: str) -> None:
    """
    Scrubs metadata from an image file in place.

    Args:
        file_path (str): Path to the image file (.jpg, .jpeg, .png).
    
    Raises:
        FileNotFoundError: If file is missing.
        PermissionError: If file cannot be accessed.
        ValueError: If file extension is unsupported.
        RuntimeError: If metadata removal or output confirmation fails.
    """
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")

    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")
    if not os.access(file_path, os.R_OK | os.W_OK):
        raise PermissionError(f"Cannot read/write image file: {file_path}")
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}")

    try:
        if ext in EXIF_EXTENSIONS:
            piexif.remove(str(path))
            logger.info(f"✅ EXIF metadata removed from: {file_path}")
        elif ext in OTHER_EXTENSIONS:
            with Image.open(path) as img:
                img_data = list(img.getdata())
                scrubbed = Image.new(img.mode, img.size)
                scrubbed.putdata(img_data)
                scrubbed.save(path)
                logger.info(f"✅ Metadata stripped from non-EXIF format: {file_path}")
        else:
            raise ValueError(f"No handler available for file extension: {ext}")
    except Exception as e:
        logger.error(f"❌ Error scrubbing metadata from {file_path}: {e}")
        raise RuntimeError(f"Scrubbing failed for {file_path}: {e}")

    # Confirm output file is intact
    if not path.exists() or path.stat().st_size == 0:
        logger.error(f"❌ Output file validation failed: {file_path}")
        raise RuntimeError(f"Scrubbed output missing or empty: {file_path}")
