import subprocess
import tempfile
import shutil
import os

def encrypt_with_gpg(file_path, public_key_path):
    if not os.path.exists(public_key_path):
        raise FileNotFoundError("Public GPG key not found.")

    # Use a temporary isolated keyring
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

        # Extract recipient fingerprint or email from key
        list_keys = subprocess.run([
            "gpg", "--homedir", gpg_home, "--list-keys", "--with-colons"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for line in list_keys.stdout.decode().splitlines():
            if line.startswith("uid:"):
                recipient = line.split(":")[9]  # user ID string
                break
        else:
            raise RuntimeError("No recipient found in GPG key.")

        # Encrypt the file
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
        shutil.rmtree(gpg_home, ignore_errors=True)
