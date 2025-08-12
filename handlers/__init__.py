# handlers/__init__.py

import importlib
import os
import logging
import inspect

logger = logging.getLogger(__name__)
handler_map = {}

def load_handlers():
    handler_dir = os.path.dirname(__file__)
    for filename in os.listdir(handler_dir):
        if filename.endswith("_handler.py") and filename != "__init__.py":
            module_name = f"handlers.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                scrub_fn = getattr(module, "scrub", None)
                extra_msgs_fn = getattr(module, "get_additional_messages", None)
                supported = getattr(module, "SUPPORTED_EXTENSIONS", [])
                pii_flag = getattr(module, "PII_DETECT", False)

                # Properly detect if functions are async using inspect
                scrub_is_async = scrub_fn and inspect.iscoroutinefunction(scrub_fn)
                msgs_is_async = extra_msgs_fn and inspect.iscoroutinefunction(extra_msgs_fn)

                for ext in supported:
                    handler_map[ext.lower()] = {
                        "scrub": scrub_fn,
                        "get_additional_messages": extra_msgs_fn,
                        "is_async": scrub_is_async,
                        "msgs_is_async": msgs_is_async,  # Track separately
                        "pii_detect": pii_flag
                    }
                logger.info(f"✅ Loaded handler: {module_name} for extensions: {supported}")
                logger.debug(f"   Scrub async: {scrub_is_async}, Messages async: {msgs_is_async}")
            except Exception as e:
                logger.error(f"❌ Failed to load handler {module_name}: {e}")

load_handlers()

def get_handler_for_extension(ext: str):
    return handler_map.get(ext.lower())