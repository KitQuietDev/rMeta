# routes/session_clean.py

from flask import Blueprint, current_app, render_template, jsonify, request, session as flask_session, redirect, url_for
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
    
    # Clear the app-level attributes that store file results
    flask_session.pop('processing_results', None)
    flask_session.pop('session_id', None)
    flask_session.pop('_flashes', None)
    
    # Also clear any flash messages
    flask_session.pop('_flashes', None)
    
    # Log the action
    if files_removed:
        current_app.logger.info("🧼 Manual cleanup: files removed")
    else:
        current_app.logger.info("🧼 Manual cleanup: already clean")
    
    # Redirect back to main page to show clean state
    return redirect(url_for('upload.index'))

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