"""
Phase 32: Unified Error Handler
Centralized error handling with recovery strategies.
"""

import os
import sys
import logging
import traceback
from typing import Any, Callable, Dict, Optional, Type
from functools import wraps
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class RetryConfig:
    """Retry configuration."""
    def __init__(self, max_attempts: int = 3, delay: float = 1.0, 
                 backoff: float = 2.0, exceptions: tuple = (Exception,)):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions

def retry(config: RetryConfig = None):
    """
    Retry decorator with exponential backoff.
    
    Usage:
        @retry(RetryConfig(max_attempts=3, delay=1.0))
        def my_function():
            ...
    """
    if config is None:
        config = RetryConfig()
        
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = config.delay
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except config.exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed for {func.__name__}: {e}"
                    )
                    if attempt < config.max_attempts:
                        import time
                        time.sleep(delay)
                        delay *= config.backoff
                        
            raise last_exception
        return wrapper
    return decorator

class ErrorHandler:
    """
    Centralized error handler with recovery strategies.
    """
    
    def __init__(self):
        self._handlers: Dict[Type[Exception], Callable] = {}
        self._error_log: list = []
        
    def register_handler(self, exception_type: Type[Exception], handler: Callable):
        """Register error handler for specific exception type."""
        self._handlers[exception_type] = handler
        
    def handle(self, exception: Exception, context: Dict = None) -> Optional[Any]:
        """
        Handle an exception using registered handlers.
        
        Args:
            exception: The exception to handle
            context: Additional context information
            
        Returns:
            Recovery result or None
        """
        # Log error
        error_info = {
            'type': type(exception).__name__,
            'message': str(exception),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        self._error_log.append(error_info)
        
        logger.error(f"Error: {error_info['type']} - {error_info['message']}")
        
        # Try registered handlers
        for exc_type, handler in self._handlers.items():
            if isinstance(exception, exc_type):
                try:
                    return handler(exception, context)
                except Exception as handler_error:
                    logger.error(f"Error handler failed: {handler_error}")
                    
        return None
        
    def get_error_log(self, limit: int = 50) -> list:
        """Get recent error log."""
        return self._error_log[-limit:]
        
    def clear_error_log(self):
        """Clear error log."""
        self._error_log.clear()
        
    def generate_report(self) -> str:
        """Generate error handling report."""
        lines = []
        lines.append("=" * 50)
        lines.append("🔧 错误处理报告")
        lines.append("=" * 50)
        lines.append(f"\n📊 已注册处理器: {len(self._handlers)}")
        
        for exc_type in self._handlers:
            lines.append(f"  ✅ {exc_type.__name__}")
            
        lines.append(f"\n📋 错误日志: {len(self._error_log)} 条")
        if self._error_log:
            lines.append(f"\n最近 5 条错误:")
            for error in self._error_log[-5:]:
                lines.append(f"  - {error['timestamp'][:19]} | {error['type']}: {error['message'][:50]}")
                
        return "\n".join(lines)

# Global error handler
error_handler = ErrorHandler()
