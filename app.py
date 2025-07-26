import os, tempfile, threading, logging, shutil, time
from flask import Flask, request, render_template, send_from_directory
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load config
load_dotenv()
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 600))
FLASK_PORT = int(os.getenv("FLASK_PORT", 8574))
ENABLE_GPG = os.getenv("ENABLE_GPG", "false").lower() == "true"

# Initialize app and logger
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
SESSIONS_ROOT = "/tmp/rMeta"
os.makedirs(SESSIONS_ROOT, exist_ok=True)

# Imports
from handlers import handler_map
from postprocessors import gpg_encryptor, import_hashlib

# Background cleanup thread
def schedule_cleanup(folder, delay=SESSION_TIMEOUT):
    def delayed_delete():
        try: shutil.rmtree(folder)
        except Exception as e: app.logger.warning(f"Session cleanup failed: {e}")
    threading.Timer(delay, delayed_delete).start()

# File processing route
@app.route("/", methods=["GET", "POST"])
def upload_file():
    messages, cleaned_files = [], []
    session_id, processing_time = None, None

    if request.method == "POST":
        start_time = time.time()
        session_dir = tempfile.mkdtemp(prefix="session_", dir=SESSIONS_ROOT)
        session_id = os.path.basename(session_dir)

        files = request.files.getlist("file")
        gpg_file = request.files.get("gpg_key")
        gpg_path = None

        # If encryption requested
        if request.form.get("encrypt_file") and gpg_file and ENABLE_GPG:
            gpg_path = os.path.join(session_dir, secure_filename(gpg_file.filename))
            gpg_file.save(gpg_path)

        for f in files:
            if not f: continue
            filename = secure_filename(f.filename)
            ext = filename.rsplit(".", 1)[-1].lower()

            if ext not in handler_map:
                messages.append(f"❌ Unsupported file: {filename}")
                continue

            save_path = os.path.join(session_dir, filename)
            f.save(save_path)

            handler_entry = handler_map[ext]

            try:
                handler_entry["scrub"](save_path)
                messages.append(f"✅ Scrubbed: {filename}")
                cleaned_files.append(filename)

                if handler_entry.get("get_additional_messages"):
                    try:
                        extra_msgs = handler_entry["get_additional_messages"](save_path)
                        messages.extend(extra_msgs)
                    except Exception as extra:
                        app.logger.warning(f"Supplemental message error for {filename}: {extra}")

            except Exception as e:
                messages.append(f"❌ Handler error: {filename} – {str(e)}")
                continue

            if request.form.get("generate_hash"):
                try:
                    hash_file = import_hashlib.generate_hash(save_path)
                    cleaned_files.append(hash_file)
                    messages.append(f"🔍 Hash created: {hash_file}")
                except Exception as e:
                    messages.append(f"❌ Hash failed for {filename}: {str(e)}")

            if request.form.get("encrypt_file") and gpg_path and ENABLE_GPG:
                try:
                    encrypted = gpg_encryptor.encrypt_with_gpg(save_path, gpg_path)
                    cleaned_files.append(encrypted)
                    messages.append(f"🔐 Encrypted: {encrypted}")
                except Exception as e:
                    messages.append(f"❌ Encryption failed: {filename} – {str(e)}")

        processing_time = round(time.time() - start_time, 2)
        messages.append(f"⏱️ Processed in {processing_time} seconds")

        schedule_cleanup(session_dir)

    accept_list = ",".join(f".{ext}" for ext in handler_map.keys())
    return render_template(
        "index.html",
        messages=messages,
        files=cleaned_files,
        session=session_id,
        accept=accept_list,
        enable_gpg=ENABLE_GPG,
        processing_time=processing_time,
    )

# File download
@app.route("/download/<session>/<filename>")
def download_file(session, filename):
    safe_dir = os.path.join(SESSIONS_ROOT, secure_filename(session))
    return send_from_directory(safe_dir, filename, as_attachment=True)

# Launch
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_PORT)
