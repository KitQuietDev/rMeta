import importlib
import os

handler_map = {}


def load_handlers():
    handler_dir = os.path.dirname(__file__)
    for filename in os.listdir(handler_dir):
        if filename.endswith("_handler.py") and filename != "__init__.py":
            module_name = f"handlers.{filename[:-3]}"
            module = importlib.import_module(module_name)
            for ext in getattr(module, "supported_extensions", []):
                handler_map[ext] = module


load_handlers()
