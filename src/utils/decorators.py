import time
import random
import threading
from functools import wraps

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.timestamps = []
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            now = time.time()
            # Remove timestamps older than the period
            self.timestamps = [t for t in self.timestamps if now - t < self.period]
            
            if len(self.timestamps) >= self.max_calls:
                # Wait until the oldest timestamp expires
                sleep_time = self.period - (now - self.timestamps[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Update now because we slept
                    now = time.time()
                    # Clean again to ensure state is consistent
                    self.timestamps = [t for t in self.timestamps if now - t < self.period]
            
            self.timestamps.append(now)

def rate_limit(max_calls: int, period: float):
    """
    Fixed window rate limiter decorator.
    Ensures the decorated function is called at most `max_calls` times within `period` seconds.
    Shared across all calls to the decorated function (even across instances).
    """
    limiter = RateLimiter(max_calls, period)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter.wait()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def random_delay(min_seconds: float, max_seconds: float):
    """
    Decorator to add a random delay before function execution.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            time.sleep(random.uniform(min_seconds, max_seconds))
            return func(*args, **kwargs)
        return wrapper
    return decorator
