"""
缓存管理模块 - Phase 228
Redis兼容的内存缓存实现
"""
import time
import functools
from threading import Lock

class SimpleCache:
    """简单内存缓存"""
    def __init__(self, max_size=1000):
        self._cache = {}
        self._ttl = {}
        self._lock = Lock()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        with self._lock:
            if key in self._cache and key in self._ttl:
                if time.time() < self._ttl[key]:
                    self.hits += 1
                    return self._cache[key]
                else:
                    self._cache.pop(key, None)
                    self._ttl.pop(key, None)
            self.misses += 1
            return None
    
    def set(self, key, value, ttl=300):
        with self._lock:
            if len(self._cache) >= self.max_size:
                self._evict_expired()
            if len(self._cache) < self.max_size:
                self._cache[key] = value
                self._ttl[key] = time.time() + ttl
                return True
            return False
    
    def delete(self, key):
        with self._lock:
            self._cache.pop(key, None)
            self._ttl.pop(key, None)
    
    def clear(self):
        with self._lock:
            self._cache.clear()
            self._ttl.clear()
    
    def _evict_expired(self):
        now = time.time()
        expired = [k for k, v in self._ttl.items() if now > v]
        for key in expired:
            self._cache.pop(key, None)
            self._ttl.pop(key, None)
    
    @property
    def stats(self):
        total = self.hits + self.misses
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(self.hits / total * 100, 2) if total > 0 else 0
        }

cache = SimpleCache(max_size=2000)

def cached(ttl=300, key_prefix=''):
    """缓存装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(kwargs)}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
