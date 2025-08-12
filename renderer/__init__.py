# renderer/__init__.py

from .flask_renderer import FlaskRenderer

def get_wsgi_app(self):
    return self.app

def load_renderer(config):
    """
    Load and return the appropriate renderer based on config.
    Currently only supports Flask, but could be extended for CLI/headless modes.
    """
    renderer_type = config.get("RENDERER_TYPE", "flask").lower()
    
    if renderer_type == "flask":
        return FlaskRenderer(config)
    else:
        raise ValueError(f"Unsupported renderer type: {renderer_type}")

# Export for Gunicorn/WSGI
def create_wsgi_app():
    """
    Create WSGI app for production deployment.
    This is called by Gunicorn via: gunicorn 'renderer:create_wsgi_app()'
    """
    from config import load_config
    config = load_config()
    renderer = load_renderer(config)
    return renderer.get_wsgi_app()

# For backwards compatibility
app = None

def get_app():
    """Get the Flask app instance - lazy loaded"""
    global app
    if app is None:
        from config import load_config
        config = load_config()
        renderer = load_renderer(config)
        app = renderer.get_wsgi_app()
    return app