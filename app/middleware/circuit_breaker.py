import time
from functools import wraps
from fastapi import HTTPException

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=10):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'

    def call(self, func):
        @wrap(func)
        async def wrapper(*args, **kwargs):
            now = time.time()

            if self.state == 'OPEN':
                if now - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF-OPEN'
                else:
                    raise HTTPException(status_code=503, detail="Service unavailable")
                
            try:
                result = await func(*args, **kwargs)
                if self.state == 'HALF-OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                return result
            except Exception:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                raise HTTPException(status_code=503, detail="Service unavailable")
        return wrapper
