import hashlib
import os

def generate_hash(file_path, algo="sha256"):
    h = hashlib.new(algo)
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)

    hash_hex = h.hexdigest()
    hash_path = f"{file_path}.{algo}.txt"

    with open(hash_path, "w") as out:
        out.write(f"{os.path.basename(file_path)}: {hash_hex}\n")

    return os.path.basename(hash_path)
