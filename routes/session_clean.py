# routes/session_clean.py

from flask import Blueprint, current_app, render_template, jsonify, request
from utils.cleanup import purge_uploads, check_uploads_dir
import time

session_clean_bp = Blueprint("session_clean", __name__)

@session_clean_bp.route("/clean", methods=["POST"], endpoint="clean_memory")
def clean_memory():
    """Manual cleanup triggered by user button"""
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    
    # Purge all files from the uploads directory
    files_removed = purge_uploads(upload_folder)
    
    # Update app config to reflect clean state
    current_app.config["HAS_DIRTY_DATA"] = False
    
    # Log the action
    if files_removed:
        current_app.logger.info("🧼 Manual cleanup: files removed")
    else:
        current_app.logger.info("🧼 Manual cleanup: already clean")
    
    # Render redirect page with 2-second delay
    return render_template("cleanup_redirect.html")

@session_clean_bp.route("/status", methods=["GET"], endpoint="check_status")
def check_status():
    """AJAX endpoint to check if uploads directory has files"""
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    has_files = check_uploads_dir(upload_folder)
    
    # Update the app config
    current_app.config["HAS_DIRTY_DATA"] = has_files
    
    return jsonify({
        "has_dirty_data": has_files,
        "timestamp": int(time.time())
    })

def register_session_clean_routes(app):
    """Register session cleaning routes"""
    app.register_blueprint(session_clean_bp)