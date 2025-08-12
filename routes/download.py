# routes/download.py

from flask import send_from_directory, Blueprint
from werkzeug.utils import secure_filename
import os
from utils.cleanup import mark_session_active

def register_download_routes(app, config):
    SESSIONS_ROOT = config.get("SESSIONS_ROOT", "/tmp/rMeta")
    download_bp = Blueprint("download", __name__)

    @download_bp.route("/download/<session>/<filename>")
    def download_file(session, filename):
        safe_dir = os.path.join(SESSIONS_ROOT, secure_filename(session))
        mark_session_active(safe_dir)
        return send_from_directory(safe_dir, filename, as_attachment=True)

    app.register_blueprint(download_bp)
