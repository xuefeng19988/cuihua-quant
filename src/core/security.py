"""
Phase 73: Security Enhancements
Advanced security features for production deployment.
"""

import os
import sys
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List
from functools import wraps

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class RateLimiter:
    """
    Rate limiter to prevent API abuse.
    """
    def __init__(self, max_requests: int = 100, window: int = 3600):
        self.max_requests = max_requests
        self.window = window
        self._requests: Dict[str, List[float]] = {}
        
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        
        if client_id not in self._requests:
            self._requests[client_id] = []
            
        # Remove old requests
        self._requests[client_id] = [
            t for t in self._requests[client_id]
            if now - t < self.window
        ]
        
        if len(self._requests[client_id]) >= self.max_requests:
            return False
            
        self._requests[client_id].append(now)
        return True
        
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests."""
        now = time.time()
        if client_id not in self._requests:
            return self.max_requests
            
        current = len([t for t in self._requests[client_id] if now - t < self.window])
        return max(0, self.max_requests - current)


class InputValidator:
    """
    Validate and sanitize user inputs.
    """
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            return ""
        value = value.strip()[:max_length]
        # Remove potential XSS
        value = value.replace('<', '&lt;').replace('>', '&gt;')
        return value
        
    @staticmethod
    def validate_stock_code(code: str) -> bool:
        """Validate stock code format."""
        import re
        return bool(re.match(r'^(SH|SZ|HK|US|CRYPTO)\.\w+$', code))
        
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format."""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except Exception as e:
            return False
            
    @staticmethod
    def validate_number(value, min_val: float = None, max_val: float = None) -> bool:
        """Validate number range."""
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                return False
            if max_val is not None and num > max_val:
                return False
            return True
        except Exception as e:
            return False


class APISecurity:
    """
    API security utilities.
    """
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key."""
        return secrets.token_urlsafe(32)
        
    @staticmethod
    def hash_api_key(key: str) -> str:
        """Hash API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()
        
    @staticmethod
    def verify_api_key(key: str, hashed: str) -> bool:
        """Verify API key."""
        return hashlib.sha256(key.encode()).hexdigest() == hashed
        
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token."""
        return secrets.token_hex(32)
        
    @staticmethod
    def verify_csrf_token(token: str, session_token: str) -> bool:
        """Verify CSRF token."""
        return secrets.compare_digest(token, session_token)


def require_auth(auth_func: callable):
    """
    Decorator to require authentication.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not auth_func():
                return {'error': 'Authentication required'}, 401
            return func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit(limiter: RateLimiter):
    """
    Decorator to apply rate limiting.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_id = kwargs.get('client_id', 'unknown')
            if not limiter.is_allowed(client_id):
                return {'error': 'Rate limit exceeded'}, 429
            return func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    print("✅ Security Enhancements loaded")
    
    # Test rate limiter
    limiter = RateLimiter(max_requests=5, window=10)
    
    for i in range(7):
        allowed = limiter.is_allowed('test_client')
        print(f"  Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'}")
        
    # Test input validation
    validator = InputValidator()
    print(f"\n🔍 Input Validation:")
    print(f"  Stock code 'SH.600519': {validator.validate_stock_code('SH.600519')}")
    print(f"  Stock code 'INVALID': {validator.validate_stock_code('INVALID')}")
    print(f"  Date '2026-04-17': {validator.validate_date('2026-04-17')}")
    print(f"  Date 'invalid': {validator.validate_date('invalid')}")
