import os
import shutil
import tempfile
import threading
import logging
from flask import Flask, request, send_from_directory, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from handlers import handler_map
from postprocessors import import_hashlib, gpg_encryptor

# Load environment variables from .env file
load_dotenv()

# Session cleanup delay (in seconds)
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 600))
# Port to run the Flask app on
FLASK_PORT = int(os.getenv("FLASK_PORT", 8574))
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
# Flag to allow GPG encryption (must also be toggled in the UI)
ENABLE_GPG_ENCRYPTION = os.getenv("ENABLE_GPG", "false").lower() == "true"

# Initialize Flask app
app = Flask(__name__)

# Configure logging for app-wide use
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s"
)
app.logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# Root directory for per-upload temporary folders
SESSIONS_ROOT = "/tmp/rMeta"
os.makedirs(SESSIONS_ROOT, exist_ok=True)

# Schedule a background thread to delete a session folder after timeout
# This helps prevent lingering sensitive files in the tmp directory
def schedule_cleanup(folder, delay=SESSION_TIMEOUT):
    def delete_later():
        try:
            shutil.rmtree(folder)
            app.logger.debug(f"✅ Deleted session folder: {folder}")
        except Exception as e:
            app.logger.exception(f"⚠️ Cleanup failed for {folder}: {e}")
    threading.Timer(delay, delete_later).start()

# Route: Main landing page + file handler logic
@app.route("/", methods=["GET", "POST"])
def upload_file():
    messages = []
    cleaned_files = []
    session_id = None

    if request.method == "POST":
        files = request.files.getlist("file")
        session_dir = tempfile.mkdtemp(prefix="session_", dir=SESSIONS_ROOT)
        session_id = os.path.basename(session_dir)

        # If a GPG key is uploaded and encryption is requested
        gpg_key_file = request.files.get("gpg_key")
        gpg_key_path = None

        if request.form.get("encrypt_file") and gpg_key_file and ENABLE_GPG_ENCRYPTION:
            gpg_key_filename = secure_filename(gpg_key_file.filename)
            gpg_key_path = os.path.join(session_dir, gpg_key_filename)
            gpg_key_file.save(gpg_key_path)

        for f in files:
            if not f:
                continue

            filename = secure_filename(f.filename)
            ext = filename.rsplit(".", 1)[-1].lower()
            if ext not in handler_map:
                messages.append(f"⚠️ Unsupported file type: {filename}")
                continue

            save_path = os.path.join(session_dir, filename)
            f.save(save_path)

            try:
                handler_map[ext].scrub(save_path)
                messages.append(f"✅ Cleaned: {filename}")
                cleaned_files.append(filename)
            except Exception as e:
                messages.append(f"❌ Error cleaning {filename}: {e}")
                continue

            # Postprocessing: Optional SHA256 hash
            if request.form.get("generate_hash"):
                try:
                    hash_filename = import_hashlib.generate_hash(save_path)
                    cleaned_files.append(hash_filename)
                    messages.append(f"🧮 Hash generated: {hash_filename}")
                except Exception as e:
                    messages.append(f"❌ Error generating hash for {filename}: {e}")

            # Postprocessing: Optional GPG encryption
            if request.form.get("encrypt_file") and gpg_key_path and ENABLE_GPG_ENCRYPTION:
                try:
                    gpg_filename = gpg_encryptor.encrypt_with_gpg(
                        save_path,
                        public_key_path=gpg_key_path
                    )
                    cleaned_files.append(gpg_filename)
                    messages.append(f"🔐 Encrypted: {gpg_filename}")
                except Exception as e:
                    messages.append(f"❌ GPG encryption failed for {filename}: {e}")

        # Start background cleanup for this session folder
        schedule_cleanup(session_dir)

    # Filetype accept list for HTML file input
    accept_list = ",".join(f".{ext}" for ext in handler_map.keys())
    return render_template(
        "index.html",
        messages=messages,
        files=cleaned_files,
        session=session_id,
        accept=accept_list,
        enable_gpg=ENABLE_GPG_ENCRYPTION,
    )

# Route: Serve individual download links
@app.route("/download/<session>/<filename>")
def download_file(session, filename):
    session_dir = os.path.join(SESSIONS_ROOT, secure_filename(session))
    return send_from_directory(session_dir, filename, as_attachment=True)

# Entrypoint: launch Flask app if run directly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_PORT)
