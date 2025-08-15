import os
import uuid
import asyncio
import logging
from flask import Blueprint, request, redirect, url_for, flash, current_app, render_template
from werkzeug.utils import secure_filename
from handlers import get_handler_for_extension
from utils.cleanup import (
    mark_session_active,
    schedule_cleanup,
    purge_uploads,
    check_uploads_dir
)
from postprocessors.import_hashlib import generate_hash
from postprocessors.gpg_encryptor import encrypt_with_gpg
from utils.chunking import audit_files, chunk_files_by_size, process_chunks
from utils.system import get_available_memory_mb

logger = logging.getLogger(__name__)

upload_bp = Blueprint("upload", __name__)

def uploads_are_dirty():
    upload_path = current_app.config.get("UPLOAD_FOLDER", "uploads")
    try:
        return any(os.scandir(upload_path))  # True if anything exists
    except Exception:
        return 

def register_upload_routes(app):
    app.register_blueprint(upload_bp)

@upload_bp.route("/", methods=["POST"], endpoint="upload_file")
def upload_file():
    files = request.files.getlist("file")
    if not files:
        flash("No files uploaded.")
        return redirect(url_for("upload.index"))

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")

    # Detect new session - purge uploads if files are being uploaded
    if request.files:  # If files are being uploaded
        purge_uploads(upload_folder)  # Clean slate for new session
        current_app.config["HAS_DIRTY_DATA"] = False

    # Create new session folder
    session_id = str(uuid.uuid4())[:8]
    session_dir = os.path.join(upload_folder, f"session_{session_id}")
    os.makedirs(session_dir, exist_ok=True)

    timeout = current_app.config.get("SESSION_TIMEOUT", 600)
    mark_session_active(session_dir)
    schedule_cleanup(session_dir, timeout)

    processed_files = []
    saved_paths = []

    # Save uploaded files
    for file in files:
        if not file or not file.filename:
            flash("Skipped unnamed file.")
            continue

        filename = secure_filename(file.filename)
        if not filename.strip():
            flash("Skipped file with invalid name.")
            continue

        filepath = os.path.join(session_dir, filename)
        file.save(filepath)
        logger.info(f"📥 Uploaded: {filepath}")
        saved_paths.append(filepath)

    # Audit files for memory and support
    available_mem = get_available_memory_mb()
    supported, too_large, skipped = audit_files(saved_paths, min_memory_mb=available_mem)

    for f, reason in skipped:
        flash(f"⚠️ Skipped {os.path.basename(f)}: {reason}")
    for f, size in too_large:
        flash(f"🚫 Too large to process now: {os.path.basename(f)} ({size:.1f}MB)")

    # Chunk supported files
    chunks = chunk_files_by_size(supported, chunk_mb=200)

    # Define processing logic
    def process_files(file_list):
        for filepath in file_list:
            filename = os.path.basename(filepath)
            ext = os.path.splitext(filename)[1].lower().lstrip(".")
            handler_entry = get_handler_for_extension(ext)

            if not handler_entry:
                flash(f"❌ Unsupported file type: {filename}")
                continue

            file_result = {
                "filename": filename,
                "warnings": [],
                "metadata_msg": f"Metadata stripped from {ext.upper()}: {filename}",
                "hash_file": None,
                "encrypted": False
            }

            try:
                scrub_fn = handler_entry.get("scrub")
                get_additional_messages_fn = handler_entry.get("get_additional_messages")
                is_async = handler_entry.get("is_async", False)
                msgs_is_async = handler_entry.get("msgs_is_async", False)

                # Step 1: Scrub metadata
                if scrub_fn:
                    if is_async:
                        asyncio.run(scrub_fn(filepath))
                    else:
                        scrub_fn(filepath)
                    logger.info(f"✅ Scrubbed metadata from: {filename}")

                # Step 2: Get additional messages
                if get_additional_messages_fn:
                    if msgs_is_async:
                        additional_messages = asyncio.run(get_additional_messages_fn(filepath))
                    else:
                        additional_messages = get_additional_messages_fn(filepath)
                    file_result["warnings"].extend(additional_messages)

                # Step 3: Optional post-processing
                if request.form.get("generate_hash"):
                    try:
                        hash_filename = generate_hash(filepath)
                        file_result["hash_file"] = hash_filename
                        logger.info(f"🧮 Hash generated: {hash_filename}")
                    except Exception as e:
                        file_result["warnings"].append(f"❌ Hash generation failed: {str(e)}")

                if request.form.get("encrypt_file"):
                    gpg_key_file = request.files.get("gpg_key")
                    if gpg_key_file and gpg_key_file.filename:
                        try:
                            gpg_key_path = os.path.join(session_dir, secure_filename(gpg_key_file.filename))
                            gpg_key_file.save(gpg_key_path)
                            encrypted_filename = encrypt_with_gpg(filepath, gpg_key_path)
                            file_result["filename"] = encrypted_filename
                            file_result["encrypted"] = True
                            os.remove(gpg_key_path)
                            logger.info(f"🔐 File encrypted: {encrypted_filename}")
                        except Exception as e:
                            file_result["warnings"].append(f"❌ GPG encryption failed: {str(e)}")
                    else:
                        file_result["warnings"].append(f"❌ GPG encryption requested but no key provided.")

                processed_files.append(file_result)

            except Exception as e:
                logger.exception(f"❌ Failed processing {filename}: {e}")
                file_result["warnings"].append(f"❌ Error processing file: {str(e)}")
                processed_files.append(file_result)

    # Process chunks
    process_chunks(chunks, min_memory_mb=500, processor=process_files)

    current_app.processing_results = processed_files  # type: ignore
    current_app.session_id = session_id  # type: ignore

    flash(f"✅ Processed {len(processed_files)} files in {len(chunks)} chunks.")
    return redirect(url_for("upload.index"))

@upload_bp.route("/", methods=["GET"], endpoint="index")
def index():
    session_id = getattr(current_app, "session_id", None)
    files = getattr(current_app, "processing_results", [])
    messages = list(getattr(current_app, "_flashes", []))

    has_dirty_data = uploads_are_dirty()

    return render_template(
        "index.html",
        session=session_id,
        files=files,
        messages=[msg for _, msg in messages],
        has_dirty_data=has_dirty_data
    )
