import os
import logging
from pathlib import Path
from .system import get_available_memory_mb

logger = logging.getLogger(__name__)

def is_supported_file(file_path):
    """
    Dummy check for supported file types.
    Replace with your actual logic.
    """
    supported_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".txt", ".csv", ".docx", ".xlsx"}
    return Path(file_path).suffix.lower() in supported_extensions

def audit_files(file_paths, min_memory_mb):
    """
    Audit files for size and type before chunking.
    Returns: (supported, too_large, skipped)
    """
    supported = []
    too_large = []
    skipped = []

    for f in file_paths:
        if not os.path.exists(f):
            skipped.append((f, "Missing"))
            continue

        size_mb = os.path.getsize(f) / (1024 * 1024)
        if size_mb > min_memory_mb:
            too_large.append((f, size_mb))
            continue

        if not is_supported_file(f):
            skipped.append((f, "Unsupported"))
            continue

        supported.append(f)

    return supported, too_large, skipped

def chunk_files_by_size(file_paths, chunk_mb):
    """
    Group files into chunks based on total size.
    Returns: List of file path lists.
    """
    chunks = []
    current_chunk = []
    current_size = 0

    for f in file_paths:
        size_mb = os.path.getsize(f) / (1024 * 1024)
        if current_size + size_mb > chunk_mb:
            chunks.append(current_chunk)
            current_chunk = []
            current_size = 0
        current_chunk.append(f)
        current_size += size_mb

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def process_chunks(chunks, min_memory_mb, processor=None):
    """
    Process each chunk if memory is sufficient.
    `processor` is a callable that takes a list of file paths.
    """
    for chunk in chunks:
        available = get_available_memory_mb()
        if available < min_memory_mb:
            logger.warning(f"🧠 Skipping chunk due to low memory ({available:.1f}MB available)")
            continue

        try:
            if processor:
                processor(chunk)
            else:
                logger.info(f"📦 Processing chunk: {[os.path.basename(f) for f in chunk]}")
                # Replace with your actual processing logic
        except Exception as e:
            logger.error(f"❌ Error processing chunk: {e}")

def estimate_required_memory(file_paths):
    """
    Estimate total memory needed based on file sizes.
    """
    total_size = sum(os.path.getsize(f) for f in file_paths if os.path.exists(f))
    return max(500, total_size // (1024 * 1024))  # At least 500MB or size in MB