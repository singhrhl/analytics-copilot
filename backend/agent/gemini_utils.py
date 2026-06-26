# agent/gemini_utils.py
import time

def call_with_backoff(fn, *args, max_retries: int = 3, **kwargs):
    """Calls fn(*args, **kwargs), retrying with exponential backoff on failure.
    Used for Gemini API calls (chat completions, embeddings), which occasionally
    fail with transient 503 'high demand' errors that are infrastructure-level,
    not code bugs — see project handoff notes."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"Gemini call failed (attempt {attempt+1}/{max_retries}): {e}. Retrying in {wait}s...")
                time.sleep(wait)
    raise RuntimeError(f"Gemini API failed after {max_retries} attempts: {last_error}")