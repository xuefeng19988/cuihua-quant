"""
请求限流模块 - Phase 229
防止API滥用和DDoS攻击
"""
import time
from functools import wraps
from flask import request, jsonify
from threading import Lock

class RateLimiter:
    """滑动窗口限流器"""
    def __init__(self):
        self._requests = {}
        self._lock = Lock()
    
    def is_allowed(self, key, max_requests=100, window=60):
        with self._lock:
            now = time.time()
            if key not in self._requests:
                self._requests[key] = []
            
            self._requests[key] = [t for t in self._requests[key] if now - t < window]
            
            if len(self._requests[key]) >= max_requests:
                return False
            
            self._requests[key].append(now)
            return True

limiter = RateLimiter()

def rate_limit(max_requests=100, window=60):
    """限流装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            key = f"{client_ip}:{f.__name__}"
            
            if not limiter.is_allowed(key, max_requests, window):
                return jsonify({
                    'code': 429,
                    'message': '请求过于频繁，请稍后再试',
                    'retry_after': window
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
