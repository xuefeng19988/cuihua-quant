# Caching Layer
# Provides Redis-based caching for performance optimization.

import os
import sys
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

class CacheManager:
    """
    Caching layer for performance optimization.
    Supports: Memory cache (default) and Redis (optional).
    """
    
    def __init__(self, use_redis: bool = False, redis_url: str = None):
        self.use_redis = use_redis
        self.memory_cache: dict = {}
        
        if use_redis:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url or 'redis://localhost:6379/0')
                self.redis_client.ping()
                print("✅ Redis cache connected")
            except Exception as e:
                print(f"⚠️ Redis connection failed, falling back to memory cache: {e}")
                self.use_redis = False
                
    def _get_key(self, key: str) -> str:
        """Generate cache key."""
        return f"cuihua_quant:{key}"
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        cache_key = self._get_key(key)
        
        if self.use_redis:
            try:
                data = self.redis_client.get(cache_key)
                if data:
                    return json.loads(data)
            except:
                pass
                
        # Memory cache fallback
        if cache_key in self.memory_cache:
            item = self.memory_cache[cache_key]
            if item['expires'] > datetime.now():
                return item['value']
            else:
                del self.memory_cache[cache_key]
                
        return default
        
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Set value in cache with TTL."""
        cache_key = self._get_key(key)
        
        if self.use_redis:
            try:
                self.redis_client.setex(
                    cache_key,
                    ttl_seconds,
                    json.dumps(value, default=str)
                )
                return True
            except:
                pass
                
        # Memory cache fallback
        self.memory_cache[cache_key] = {
            'value': value,
            'expires': datetime.now() + timedelta(seconds=ttl_seconds)
        }
        return True
        
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        cache_key = self._get_key(key)
        
        if self.use_redis:
            try:
                self.redis_client.delete(cache_key)
                return True
            except:
                pass
                
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
            return True
        return False
        
    def clear(self) -> bool:
        """Clear all cache."""
        if self.use_redis:
            try:
                self.redis_client.flushdb()
                return True
            except:
                pass
                
        self.memory_cache.clear()
        return True
        
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            'type': 'redis' if self.use_redis else 'memory',
            'memory_keys': len(self.memory_cache),
            'memory_size_mb': sys.getsizeof(json.dumps(self.memory_cache)) / 1024 / 1024
        }
        
    def cache_query(self, key_prefix: str, ttl: int = 300):
        """
        Decorator to cache function results.
        Usage:
            @cache.cache_query('stock_data', ttl=600)
            def get_stock_data(code):
                ...
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Generate cache key from function name + args
                key_data = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
                
                # Try cache
                cached = self.get(cache_key)
                if cached is not None:
                    return cached
                    
                # Execute and cache
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator
