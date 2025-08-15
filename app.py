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
from utils.chunking import audit_files, chunk_files_by_size, process_chunks
from utils.system import get_available_memory_mb
from utils.cleanup import purge_uploads, check_uploads_dir, start_auto_cleanup, stop_all_cleanup

def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"🛑 Received shutdown signal ({signum}). Cleaning up...")
    
    # Stop all cleanup threads
    stop_all_cleanup()
    
    # Purge uploads directory
    purge_uploads("uploads")
    
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, handle_shutdown)   # Ctrl+C
signal.signal(signal.SIGTERM, handle_shutdown)  # Docker/Gunicorn

# Also register atexit for other shutdown scenarios
atexit.register(lambda: (stop_all_cleanup(), purge_uploads("uploads")))

def create_app():
    """
    Creates and configures the Flask app.
    1. Loads the configuration.
    2. Purges uploads directory if dirty.
    3. Starts auto cleanup timer.
    4. Loads the FlaskRenderer with the configuration.
    5. Configures secret key and other app settings.
    6. Registers routes (e.g., upload and download routes).
    
    Returns:
        Flask app instance
    """
    # Load configuration (from env, file, etc)
    config = load_config()
    if config is None:
        raise RuntimeError("Configuration could not be loaded!")
    
    upload_folder = config.get("UPLOAD_FOLDER", "uploads")
    session_timeout = config.get("SESSION_TIMEOUT", 600)
    
    # Purge uploads directory on startup
    startup_cleanup = purge_uploads(upload_folder)
    if startup_cleanup:
        print(f"🧹 Startup cleanup completed")
    
    # Start the auto cleanup timer
    start_auto_cleanup(upload_folder, session_timeout)
    
    # Load Flask app from renderer (which sets up templates/static)
    renderer = load_renderer(config)
    app = renderer.app
    
    # Check initial state and set dirty data flag
    has_dirty_data = check_uploads_dir(upload_folder)
    app.config["HAS_DIRTY_DATA"] = has_dirty_data
    
    # Set secret key for session management (config.py provides secure default)
    secret_key = config.get("SECRET_KEY")
    if secret_key:
        app.secret_key = secret_key
   
    # Apply any other config keys to app.config if needed
    for key, value in config.items():
        app.config[key] = value
    
    # Add a template context processor to always provide current dirty state
    @app.context_processor
    def inject_dirty_state():
        """Inject current dirty state into all templates"""
        has_dirty = check_uploads_dir(app.config.get("UPLOAD_FOLDER", "uploads"))
        app.config["HAS_DIRTY_DATA"] = has_dirty  # Update config too
        return {"has_dirty_data": has_dirty}
    
    # Register blueprints/routes
    register_upload_routes(app)
    register_download_routes(app, config)
    register_session_clean_routes(app)
    
    # Optional: attach renderer and config to app for internal access
    setattr(app, "renderer", renderer)
    setattr(app, "custom_config", config)
    
    return app

def main():
    """
    Entry point for running the Flask app.
    1. Creates the app using create_app().
    2. Configures logging.
    3. Prints registered routes for debugging.
    4. Runs the app using the renderer.
    """
    app = create_app()
    
    # Setup logging level and format
    log_level = app.config.get("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    
    # Optional: Print registered routes for debugging
    print("🔗 Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint} -> {rule.rule}")
    
    try:
        # Run the app using renderer's run method
        app.renderer.run() # type: ignore
    except KeyboardInterrupt:
        print("🛑 Received KeyboardInterrupt")
        handle_shutdown(signal.SIGINT, None)

if __name__ == "__main__":
    main()