# <root>/safeguards.py

import os, time

_SESSION_FLAG = "/tmp/rmeta_session.lock"
_SESSION_TIMEOUT = 600  # seconds

def session_active():
    if not os.path.exists(_SESSION_FLAG):
        return False

    try:
        with open(_SESSION_FLAG, "r") as f:
            timestamp = float(f.readline().strip())
        if time.time() - timestamp > _SESSION_TIMEOUT:
            os.remove(_SESSION_FLAG)
            return False
    except Exception:
        os.remove(_SESSION_FLAG)
        return False

    return True

def mark_session_active(path=None):
    with open(_SESSION_FLAG, "w") as f:
        f.write(f"{time.time()}\n")
        if path:
            f.write(path)

def mark_session_idle():
    if os.path.exists(_SESSION_FLAG):
        os.remove(_SESSION_FLAG)

def check_memory(min_mb):
    try:
        import psutil
        mem_available = psutil.virtual_memory().available / (1024 * 1024)
        return mem_available >= min_mb
    except ImportError:
        return False
