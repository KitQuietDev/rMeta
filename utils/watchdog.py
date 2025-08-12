from concurrent.futures import ThreadPoolExecutor, TimeoutError

def run_with_timeout(fn, args=(), timeout=10):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn, *args)
        try:
            return future.result(timeout=timeout), None
        except TimeoutError:
            return None, f"🕓 Timeout exceeded ({timeout}s)"
