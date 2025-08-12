# renderer/flask_renderer.py

import os
import secrets
from flask import Flask, render_template
from utils.cleanup import mark_session_active

class FlaskRenderer:
    def __init__(self, config):
        if not config:
            raise ValueError("Configuration must be provided for FlaskRenderer")

        base_dir = os.path.abspath(os.path.dirname(__file__))
        root_dir = os.path.abspath(os.path.join(base_dir, ".."))

        self.app = Flask(
            __name__,
            template_folder=os.path.join(root_dir, "templates"),
            static_folder=os.path.join(root_dir, "static")
        )

        secret_key = config.get("SECRET_KEY")
        self.app.secret_key = secret_key or secrets.token_urlsafe(32)

        self.config = config
        self.port = config.get("FLASK_PORT", 8574)

        # Apply config to Flask app
        for key, value in config.items():
            self.app.config[key] = value

        # Set up the index route
        @self.app.route("/")
        def index():
            session_id = getattr(self.app, "session_id", None)
            session_dir = None
            if session_id:
                session_dir = os.path.join(config.get("SESSIONS_ROOT", "uploads"), f"session_{session_id}")
                if os.path.exists(session_dir):
                    mark_session_active(session_dir)

            files = getattr(self.app, "processing_results", [])
            
            # Get flash messages properly
            from flask import get_flashed_messages
            messages = get_flashed_messages()

            return render_template("index.html", session=session_id, files=files, messages=messages)
    def get_wsgi_app(self):
        return self.app
    def run(self):
        self.app.run(host="0.0.0.0", port=self.port, debug=True)