import os
import importlib
import logging

logger = logging.getLogger(__name__)

# Supported file types and their corresponding handler modules
EXTENSION_MAP = {
    "jpg": "image_handler",
    "jpeg": "image_handler",
    "png": "image_handler",
    "heic": "heic_handler",
    "pdf": "pdf_handler",
    "docx": "docx_handler",
    "xlsx": "xlsx_handler",
    "csv": "text_csv_handler",
    "txt": "text_csv_handler",
}

def get_handler_for_extension(ext):
    """Return the processing function for the given file extension."""
    module_name = EXTENSION_MAP.get(ext.lower())
    if not module_name:
        logger.warning(f"No handler registered for .{ext}")
        return None

    try:
        mod = importlib.import_module(f"handlers.{module_name}")
        return getattr(mod, "process", None)
    except Exception as e:
        logger.error(f"Error loading handler for .{ext}: {e}")
        return None
