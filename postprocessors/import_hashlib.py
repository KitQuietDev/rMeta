"""
Hash Generator Postprocessor for rMeta

Generates a checksum file for a given file using a specified hashing algorithm.
Useful for verifying file integrity after scrubbing or encryption.
"""

import hashlib
import os

def generate_hash(file_path, algo="sha256"):
    """
    Generate a hash of the given file and save it to a separate .txt file.

    Args:
        file_path (str): Path to the file to hash.
        algo (str): Hashing algorithm to use (e.g., 'sha256', 'md5', 'sha512').

    Returns:
        str: Name of the resulting hash file (e.g., 'document.pdf.sha256.txt').

    Raises:
        ValueError: If the specified algorithm is not supported by hashlib.
        IOError: If the file cannot be read or written.
    """
    h = hashlib.new(algo)

    # Read the file in chunks to handle large files efficiently
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)

    hash_hex = h.hexdigest()
    hash_path = f"{file_path}.{algo}.txt"

    # Write the hash result to a .txt file
    with open(hash_path, "w") as out:
        out.write(f"{os.path.basename(file_path)}: {hash_hex}\n")

    return os.path.basename(hash_path)
