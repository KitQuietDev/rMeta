# app.py

import logging
import signal
import sys
import atexit
from config import load_config
from renderer import load_renderer
from routes.upload import register_upload_routes
from routes.download import register_download_routes
from routes.session_clean import register_session_clean_routes
from rmeta_core.utils.chunking import audit_files, chunk_files_by_size, process_chunks
from rmeta_core.utils.system import get_available_memory_mb
from rmeta_core.utils.cleanup import purge_uploads, check_uploads_dir, start_auto_cleanup, stop_all_cleanup

def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"Received shutdown signal ({signum}). Cleaning up...")
    stop_all_cleanup()
    purge_uploads("uploads")
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, handle_shutdown)   # Ctrl+C
signal.signal(signal.SIGTERM, handle_shutdown)  # Docker/Gunicorn

# Also register atexit for other shutdown scenarios
atexit.register(lambda: (stop_all_cleanup(), purge_uploads("uploads")))

def create_app():
    """Build and configure the Flask app: load config, purge stale uploads,
    start the cleanup timer, then wire up routes."""
    config = load_config()
    if config is None:
        raise RuntimeError("Configuration could not be loaded!")

    upload_folder = config.get("UPLOAD_FOLDER", "uploads")
    session_timeout = config.get("SESSION_TIMEOUT", 600)

    startup_cleanup = purge_uploads(upload_folder)
    if startup_cleanup:
        print("Startup cleanup completed")

    start_auto_cleanup(upload_folder, session_timeout)

    renderer = load_renderer(config)
    app = renderer.app

    has_dirty_data = check_uploads_dir(upload_folder)
    app.config["HAS_DIRTY_DATA"] = has_dirty_data

    secret_key = config.get("SECRET_KEY")
    if secret_key:
        app.secret_key = secret_key

    for key, value in config.items():
        app.config[key] = value

    @app.context_processor
    def inject_dirty_state():
        """Inject current dirty state into all templates"""
        has_dirty = check_uploads_dir(app.config.get("UPLOAD_FOLDER", "uploads"))
        app.config["HAS_DIRTY_DATA"] = has_dirty
        return {"has_dirty_data": has_dirty}

    register_upload_routes(app)
    register_download_routes(app, config)
    register_session_clean_routes(app)

    setattr(app, "renderer", renderer)
    setattr(app, "custom_config", config)

    return app

def main():
    """Entry point: build the app, configure logging, and run it."""
    app = create_app()

    log_level = app.config.get("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint} -> {rule.rule}")

    try:
        app.renderer.run()  # type: ignore
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt")
        handle_shutdown(signal.SIGINT, None)

if __name__ == "__main__":
    main()