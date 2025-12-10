
import time
from functools import wraps
from flask import jsonify

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=10):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF-OPEN

    def call(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if self.state == 'OPEN':
                if now - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF-OPEN'
                else:
                    return jsonify({'error': 'Service unavailable (circuit open)'}), 503

            try:
                result = func(*args, **kwargs)
                if self.state == 'HALF-OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                return result
            except Exception:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                return jsonify({'error': 'Service unavailable (circuit triggered)'}), 503
        return wrapper
