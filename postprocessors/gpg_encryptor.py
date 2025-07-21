"""
GPG Encryptor Postprocessor for MetaScrub

Encrypts a file using a provided GPG public key.
This is done in an isolated temporary keyring to avoid contaminating
the system keyring or requiring key pre-import.
"""

import subprocess
import tempfile
import shutil
import os

def encrypt_with_gpg(file_path, public_key_path):
    """
    Encrypts a file using GPG with the specified public key.

    Args:
        file_path (str): Path to the file to encrypt.
        public_key_path (str): Path to a GPG public key file.

    Returns:
        str: Name of the resulting .gpg file (not full path).

    Raises:
        FileNotFoundError: If the public key is missing.
        RuntimeError: If GPG import or encryption fails.
    """
    if not os.path.exists(public_key_path):
        raise FileNotFoundError("Public GPG key not found.")

    # Use a temporary isolated keyring for security
    gpg_home = tempfile.mkdtemp(prefix="gpg_tmp_")

    try:
        # Import the public key into this keyring
        import_result = subprocess.run([
            "gpg", "--batch", "--yes",
            "--homedir", gpg_home,
            "--import", public_key_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if import_result.returncode != 0:
            raise RuntimeError(f"GPG key import failed: {import_result.stderr.decode()}")

        output_path = f"{file_path}.gpg"

        # Extract recipient UID (email or fingerprint) from imported key
        list_keys = subprocess.run([
            "gpg", "--homedir", gpg_home, "--list-keys", "--with-colons"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for line in list_keys.stdout.decode().splitlines():
            if line.startswith("uid:"):
                recipient = line.split(":")[9]  # Extract UID field
                break
        else:
            raise RuntimeError("No recipient found in GPG key.")

        # Encrypt the file using the imported key
        encrypt_result = subprocess.run([
            "gpg", "--batch", "--yes",
            "--homedir", gpg_home,
            "--trust-model", "always",
            "--output", output_path,
            "--encrypt", "--recipient", recipient,
            file_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if encrypt_result.returncode != 0:
            raise RuntimeError(f"GPG encryption failed: {encrypt_result.stderr.decode()}")

        return os.path.basename(output_path)

    finally:
        # Clean up the temporary GPG home directory
        shutil.rmtree(gpg_home, ignore_errors=True)
