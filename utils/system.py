import logging
import threading
import time

logger = logging.getLogger(__name__)

def check_memory(min_mb):
    """
    Check if at least `min_mb` of memory is available.
    """
    try:
        import psutil
        mem_available = psutil.virtual_memory().available / (1024 * 1024)
        return mem_available >= min_mb
    except ImportError:
        return False

def get_available_memory_mb():
    """
    Return available memory in MB.
    """
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 * 1024)
    except ImportError:
        return 0

def start_memory_watchdog(min_mb, sessions_root=None):
    """
    Background thread that monitors memory and optionally triggers cleanup.
    """
    from utils.cleanup import cleanup_orphaned_sessions

    def _watchdog():
        while True:
            try:
                import psutil
                mem_available = psutil.virtual_memory().available / (1024 * 1024)
                if mem_available < min_mb:
                    logger.warning(f"🧠 Memory low: {mem_available:.1f}MB available (threshold: {min_mb}MB)")
                    if sessions_root:
                        cleanup_orphaned_sessions(sessions_root, max_age_hours=1)
            except Exception as e:
                logger.error(f"Memory watchdog error: {e}")
            time.sleep(30)

    thread = threading.Thread(target=_watchdog, daemon=True, name="memory-watchdog")
    thread.start()
    logger.info(f"🚨 Memory watchdog started (threshold: {min_mb}MB)")
