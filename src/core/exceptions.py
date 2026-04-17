"""
Core exceptions for Cuihua Quant System.
"""

class CuihuaQuantError(Exception):
    """Base exception for all cuihua-quant errors."""
    def __init__(self, message: str, code: str = "UNKNOWN", details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class DataError(CuihuaQuantError):
    """Data fetching or processing error."""
    def __init__(self, message: str, source: str = "", details: dict | None = None):
        super().__init__(message, code="DATA_ERROR", details={"source": source, **(details or {})})

class ConfigError(CuihuaQuantError):
    """Configuration error."""
    def __init__(self, message: str, key: str = "", details: dict | None = None):
        super().__init__(message, code="CONFIG_ERROR", details={"key": key, **(details or {})})

class StrategyError(CuihuaQuantError):
    """Strategy execution error."""
    def __init__(self, message: str, strategy: str = "", details: dict | None = None):
        super().__init__(message, code="STRATEGY_ERROR", details={"strategy": strategy, **(details or {})})

class TradingError(CuihuaQuantError):
    """Trading execution error."""
    def __init__(self, message: str, order_id: str = "", details: dict | None = None):
        super().__init__(message, code="TRADING_ERROR", details={"order_id": order_id, **(details or {})})

class ValidationError(CuihuaQuantError):
    """Data validation error."""
    def __init__(self, message: str, field: str = "", details: dict | None = None):
        super().__init__(message, code="VALIDATION_ERROR", details={"field": field, **(details or {})})

class APIError(CuihuaQuantError):
    """External API error."""
    def __init__(self, message: str, endpoint: str = "", status_code: int = 0, details: dict | None = None):
        super().__init__(message, code="API_ERROR", details={"endpoint": endpoint, "status_code": status_code, **(details or {})})

class CacheError(CuihuaQuantError):
    """Cache operation error."""
    def __init__(self, message: str, key: str = "", details: dict | None = None):
        super().__init__(message, code="CACHE_ERROR", details={"key": key, **(details or {})})
