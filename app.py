# app.py

import logging
from config import load_config
from renderer import load_renderer
from routes.upload import register_upload_routes
from routes.download import register_download_routes
from utils.chunking import audit_files, chunk_files_by_size, process_chunks
from utils.system import get_available_memory_mb

def create_app():
    """
    Creates and configures the Flask app.

    1. Loads the configuration.
    2. Loads the FlaskRenderer with the configuration.
    3. Configures secret key and other app settings.
    4. Registers routes (e.g., upload and download routes).

    Returns:
        Flask app instance
    """
    # Load configuration (from env, file, etc)
    config = load_config()

    if config is None:
        raise RuntimeError("Configuration could not be loaded!")

    # Load Flask app from renderer (which sets up templates/static)
    renderer = load_renderer(config)
    app = renderer.app

    # Set secret key for session management (config.py provides secure default)
    secret_key = config.get("SECRET_KEY")
    if secret_key:
        app.secret_key = secret_key
    
    # Apply any other config keys to app.config if needed
    for key, value in config.items():
        app.config[key] = value

    # Register blueprints/routes
    register_upload_routes(app, config)
    register_download_routes(app, config)

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
    for rule in app.url_map.iter_rules():
        print(f"[ROUTE] {rule.endpoint} -> {rule.rule}")

    # Run the app using renderer's run method
    app.renderer.run() # type: ignore

if __name__ == "__main__":
    main()