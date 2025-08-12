"""
GPG Encryptor Postprocessor for rMeta

Encrypts a file using a provided GPG public key.
Uses an isolated temporary keyring to avoid contaminating the system keyring or requiring persistent key storage.
"""

import subprocess
import tempfile
import shutil
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = ["encrypt_with_gpg"]

def encrypt_with_gpg(file_path: str, public_key_path: str) -> str:
    """
    Encrypts a file using GPG with the specified public key.

    Args:
        file_path (str): Path to the file to encrypt.
        public_key_path (str): Path to the GPG public key file.

    Returns:
        str: Filename of the resulting encrypted .gpg file (not full path).

    Raises:
        FileNotFoundError: If file or public key is missing.
        PermissionError: If file cannot be accessed.
        RuntimeError: If GPG import or encryption fails.
    """
    input_path = Path(file_path)
    key_path = Path(public_key_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read input file: {file_path}")
    if not key_path.exists():
        raise FileNotFoundError("Public GPG key not found.")
    if not os.access(public_key_path, os.R_OK):
        raise PermissionError("Cannot read public GPG key.")

    # Isolated keyring for security
    gpg_home = tempfile.mkdtemp(prefix="gpg_tmp_")

    try:
        # Import public key
        import_cmd = [
            "gpg", "--batch", "--yes", "--homedir", gpg_home, "--import", str(key_path)
        ]
        import_result = subprocess.run(import_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if import_result.returncode != 0:
            raise RuntimeError(f"GPG key import failed: {import_result.stderr.decode().strip()}")
        logger.info(f"🔑 GPG key imported successfully from: {public_key_path}")

        # Extract recipient from key
        list_cmd = ["gpg", "--homedir", gpg_home, "--list-keys", "--with-colons"]
        list_result = subprocess.run(list_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        recipient = None
        for line in list_result.stdout.decode().splitlines():
            if line.startswith("uid:"):
                parts = line.split(":")
                if len(parts) > 9 and parts[9]:
                    recipient = parts[9]
                    break
        if not recipient:
            for line in list_result.stdout.decode().splitlines():
                if line.startswith("pub:"):
                    parts = line.split(":")
                    if len(parts) > 4:
                        recipient = parts[4]
                        break
        if not recipient:
            raise RuntimeError("No recipient found in GPG key.")

        # Encrypt the file
        output_path = f"{file_path}.gpg"
        encrypt_cmd = [
            "gpg", "--batch", "--yes", "--homedir", gpg_home,
            "--trust-model", "always", "--output", output_path,
            "--encrypt", "--recipient", recipient, str(input_path)
        ]
        encrypt_result = subprocess.run(encrypt_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if encrypt_result.returncode != 0:
            raise RuntimeError(f"GPG encryption failed: {encrypt_result.stderr.decode().strip()}")

        # Confirm output integrity
        final = Path(output_path)
        if not final.exists() or final.stat().st_size == 0:
            raise RuntimeError(f"Encrypted output missing or empty: {output_path}")
        logger.info(f"🔐 File encrypted: {output_path}")
        return final.name

    except Exception as e:
        logger.error(f"❌ Encryption error for {file_path}: {e}")
        raise

    finally:
        try:
            shutil.rmtree(gpg_home)
            logger.debug(f"🧹 Temporary GPG home deleted: {gpg_home}")
        except Exception as cleanup_error:
            logger.warning(f"⚠️ Cleanup failed for {gpg_home}: {cleanup_error}")
