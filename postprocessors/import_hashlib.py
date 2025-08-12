"""
Hash Generator Postprocessor for rMeta

Generates a checksum file for a given file using a specified hashing algorithm.
Used to verify file integrity after scrubbing or encryption.
"""

import hashlib
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)
__all__ = ["generate_hash"]

def generate_hash(file_path: str, algo: str = "sha256") -> str:
    """
    Generate a hash of the given file and save it to a separate .txt file.

    Args:
        file_path (str): Path to the file to hash.
        algo (str): Hashing algorithm to use (e.g., 'sha256', 'md5', 'sha512').

    Returns:
        str: Filename of the generated hash file.

    Raises:
        FileNotFoundError: If the input file is missing.
        PermissionError: If the file cannot be read.
        ValueError: If the algorithm is unsupported.
        RuntimeError: If hash output fails.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read input file: {file_path}")

    try:
        h = hashlib.new(algo)
    except ValueError:
        raise ValueError(f"Unsupported hashing algorithm: {algo}")

    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
    except Exception as read_err:
        logger.error(f"❌ Failed to read file for hashing: {file_path}")
        raise IOError(f"Error reading file {file_path}: {read_err}")

    hash_hex = h.hexdigest()
    hash_path = Path(f"{file_path}.{algo}.txt")

    try:
        with open(hash_path, "w") as out:
            out.write(f"{path.name}: {hash_hex}\n")
    except Exception as write_err:
        logger.error(f"❌ Failed to write hash output: {hash_path}")
        raise RuntimeError(f"Error writing hash file {hash_path}: {write_err}")

    if not hash_path.exists() or hash_path.stat().st_size == 0:
        raise RuntimeError(f"Generated hash file is missing or empty: {hash_path}")

    logger.info(f"🧮 Hash generated: {hash_path.name}")
    return hash_path.name
