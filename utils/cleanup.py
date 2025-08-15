# utils/cleanup.py

import shutil
import threading
import time
import logging
import os
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Thread-safe session tracking
_session_lock = threading.RLock()
_session_state_file = "/tmp/rmeta_sessions.json"
_cleanup_threads = {}
_auto_cleanup_thread = None
_auto_cleanup_running = False

def purge_uploads(upload_path):
    """
    Deletes all contents of the uploads directory.
    Returns True if any files were removed, False if already clean.
    """
    try:
        if not os.path.exists(upload_path):
            logger.info(f"📁 Uploads directory doesn't exist: {upload_path}")
            return False
            
        contents = os.listdir(upload_path)
        if not contents:
            logger.info(f"✅ Uploads directory already clean: {upload_path}")
            return False
            
        # Remove all contents
        for item in contents:
            item_path = os.path.join(upload_path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                logger.error(f"❌ Failed to remove {item_path}: {e}")
                
        logger.info(f"🔥 Purged uploads directory: {upload_path} ({len(contents)} items removed)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to purge uploads directory: {e}")
        return True  # Assume dirty if purge failed

def check_uploads_dir(upload_path):
    """
    Checks if the uploads directory contains any files or folders.
    Returns True if dirty (has files), False if clean (empty).
    """
    try:
        if not os.path.exists(upload_path):
            return False
        return bool(os.listdir(upload_path))
    except Exception as e:
        logger.error(f"❌ Error checking uploads dir: {e}")
        return True  # Assume dirty if check fails

def start_auto_cleanup(upload_path, timeout_sec):
    """
    Start the automatic cleanup timer that runs every timeout_sec seconds
    """
    global _auto_cleanup_thread, _auto_cleanup_running
    
    if _auto_cleanup_running:
        logger.debug("Auto cleanup already running")
        return
        
    def _auto_cleanup_loop():
        global _auto_cleanup_running
        _auto_cleanup_running = True
        logger.info(f"🕒 Auto cleanup started (interval: {timeout_sec}s)")
        
        try:
            while _auto_cleanup_running:
                time.sleep(timeout_sec)
                if _auto_cleanup_running:  # Check again after sleep
                    if check_uploads_dir(upload_path):
                        logger.info("🕒 Auto cleanup triggered")
                        purge_uploads(upload_path)
                    else:
                        logger.debug("🕒 Auto cleanup check - directory already clean")
        except Exception as e:
            logger.error(f"❌ Auto cleanup error: {e}")
        finally:
            _auto_cleanup_running = False
            logger.info("🛑 Auto cleanup stopped")
    
    _auto_cleanup_thread = threading.Thread(target=_auto_cleanup_loop, daemon=True, name="auto-cleanup")
    _auto_cleanup_thread.start()

def stop_auto_cleanup():
    """Stop the automatic cleanup timer"""
    global _auto_cleanup_running
    _auto_cleanup_running = False
    logger.info("🛑 Auto cleanup stop requested")

def _load_session_state():
    """Load session state from disk - thread safe"""
    try:
        if os.path.exists(_session_state_file):
            with open(_session_state_file, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, IOError, OSError) as e:
        logger.warning(f"Could not load session state: {e}")
    return {}

def _save_session_state(sessions):
    """Save session state to disk - thread safe"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(_session_state_file), exist_ok=True)
        
        # Write atomically
        temp_file = _session_state_file + ".tmp"
        with open(temp_file, 'w') as f:
            json.dump(sessions, f)
        os.replace(temp_file, _session_state_file)
        
    except (IOError, OSError) as e:
        logger.error(f"Could not save session state: {e}")

def mark_session_active(session_path):
    """Mark session as active - thread safe"""
    if not session_path or not isinstance(session_path, str):
        logger.warning(f"Invalid session path: {session_path}")
        return
        
    with _session_lock:
        try:
            sessions = _load_session_state()
            sessions[session_path] = time.time()
            _save_session_state(sessions)
            logger.debug(f"📍 Session marked active: {session_path}")
        except Exception as e:
            logger.error(f"Failed to mark session active: {e}")

def schedule_cleanup(path, timeout_sec):
    """
    Start background cleanup monitor - prevents multiple monitors per path
    """
    if not path or not isinstance(path, str):
        logger.warning(f"Invalid cleanup path: {path}")
        return
        
    if timeout_sec <= 0:
        logger.warning(f"Invalid timeout: {timeout_sec}")
        return

    # Prevent multiple cleanup threads for same path
    with _session_lock:
        if path in _cleanup_threads:
            logger.debug(f"Cleanup already scheduled for: {path}")
            return

    def _cleanup_monitor():
        """Cleanup monitor thread function"""
        thread_id = threading.current_thread().ident
        logger.info(f"🧹 Cleanup monitor started for: {path} (timeout: {timeout_sec}s, thread: {thread_id})")
        
        try:
            # Mark as active initially
            mark_session_active(path)
            
            check_interval = min(30, max(10, timeout_sec // 10))  # 10-30 second intervals
            
            while True:
                try:
                    with _session_lock:
                        sessions = _load_session_state()
                        last_access = sessions.get(path, 0)
                        
                        if time.time() - last_access > timeout_sec:
                            logger.info(f"🕒 Session timeout reached: {path}")
                            
                            # Attempt cleanup
                            if os.path.exists(path):
                                try:
                                    # Check if directory is empty first
                                    if os.path.isdir(path):
                                        file_count = len(os.listdir(path))
                                        shutil.rmtree(path)
                                        logger.info(f"✅ Removed session folder: {path} ({file_count} files)")
                                    else:
                                        os.remove(path)
                                        logger.info(f"✅ Removed session file: {path}")
                                except (OSError, IOError) as cleanup_err:
                                    logger.error(f"❌ Cleanup failed for {path}: {cleanup_err}")
                                    time.sleep(check_interval)
                                    continue
                            else:
                                logger.info(f"📁 Session already gone: {path}")
                            
                            # Remove from tracking
                            if path in sessions:
                                del sessions[path]
                                _save_session_state(sessions)
                            
                            # Remove from active threads
                            _cleanup_threads.pop(path, None)
                            
                            logger.info(f"🏁 Cleanup completed: {path}")
                            break
                        
                        else:
                            remaining = timeout_sec - (time.time() - last_access)
                            logger.debug(f"⏱️ Session {path}: {remaining:.0f}s remaining")
                    
                    time.sleep(check_interval)
                    
                except Exception as monitor_err:
                    logger.error(f"❌ Monitor error for {path}: {monitor_err}")
                    time.sleep(check_interval)
                    
        except Exception as fatal_err:
            logger.error(f"❌ Fatal cleanup error for {path}: {fatal_err}")
        
        finally:
            # Ensure thread is removed from tracking
            with _session_lock:
                _cleanup_threads.pop(path, None)
            logger.debug(f"🧹 Cleanup monitor exited for: {path}")

    # Start cleanup thread
    try:
        cleanup_thread = threading.Thread(
            target=_cleanup_monitor, 
            daemon=True,
            name=f"cleanup-{os.path.basename(path)}"
        )
        
        with _session_lock:
            _cleanup_threads[path] = cleanup_thread
            
        cleanup_thread.start()
        logger.info(f"🚀 Cleanup scheduled for: {path}")
        
    except Exception as e:
        logger.error(f"❌ Failed to start cleanup thread for {path}: {e}")

def cleanup_orphaned_sessions(sessions_root, max_age_hours=24):
    """Emergency cleanup for orphaned sessions"""
    if not sessions_root or not isinstance(sessions_root, str):
        logger.warning(f"Invalid sessions root: {sessions_root}")
        return
        
    try:
        sessions_path = Path(sessions_root)
        if not sessions_path.exists():
            logger.info(f"📁 Sessions directory doesn't exist: {sessions_root}")
            return
        
        if not sessions_path.is_dir():
            logger.warning(f"Sessions root is not a directory: {sessions_root}")
            return

        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned = 0
        errors = 0

        for session_dir in sessions_path.iterdir():
            if session_dir.is_dir() and session_dir.name.startswith("session_"):
                try:
                    dir_mtime = session_dir.stat().st_mtime
                    if dir_mtime < cutoff_time:
                        file_count = len(list(session_dir.rglob("*"))) if session_dir.exists() else 0
                        shutil.rmtree(session_dir)
                        logger.info(f"🧹 Cleaned orphaned session: {session_dir} ({file_count} files)")
                        cleaned += 1
                except (OSError, IOError) as e:
                    logger.warning(f"⚠️ Could not clean {session_dir}: {e}")
                    errors += 1

        if cleaned > 0:
            logger.info(f"✅ Orphan cleanup: {cleaned} sessions removed, {errors} errors")
        else:
            logger.info(f"🧹 No orphaned sessions found in {sessions_root}")
            
    except Exception as e:
        logger.error(f"❌ Orphan cleanup failed: {e}")

def get_active_sessions():
    """Get active sessions for debugging"""
    with _session_lock:
        sessions = _load_session_state()
        current_time = time.time()
        
        active_sessions = {}
        for path, last_access in sessions.items():
            try:
                age_seconds = current_time - last_access
                active_sessions[path] = {
                    "last_active": last_access,
                    "age_seconds": age_seconds,
                    "exists": os.path.exists(path),
                    "cleanup_thread": path in _cleanup_threads
                }
            except Exception as e:
                logger.warning(f"Error processing session {path}: {e}")
                
        return active_sessions

def stop_all_cleanup():
    """Stop all cleanup threads - for testing/shutdown"""
    global _auto_cleanup_running
    
    # Stop auto cleanup
    _auto_cleanup_running = False
    
    with _session_lock:
        thread_count = len(_cleanup_threads)
        _cleanup_threads.clear()
        
    logger.info(f"🛑 Stopped {thread_count} cleanup threads + auto cleanup")