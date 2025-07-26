import importlib
import os

handler_map = {}

def load_handlers():
    handler_dir = os.path.dirname(__file__)
    for filename in os.listdir(handler_dir):
        if filename.endswith("_handler.py") and filename != "__init__.py":
            module_name = f"handlers.{filename[:-3]}"
            module = importlib.import_module(module_name)
            scrub_fn = getattr(module, "scrub", None)
            extra_msgs_fn = getattr(module, "get_additional_messages", None)
            supported = getattr(module, "SUPPORTED_EXTENSIONS", [])

            for ext in supported:
                handler_map[ext] = {
                    "scrub": scrub_fn,
                    "get_additional_messages": extra_msgs_fn
                }

load_handlers()
