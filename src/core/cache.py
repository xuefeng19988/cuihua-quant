"""
Phase 28: Query Cache System
Multi-level caching for database queries.
"""

import os
import sys
import hashlib
import time
import json
import pickle
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from functools import wraps

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class QueryCache:
    """
    Multi-level query cache system.
    L1: Memory cache (fast, small)
    L2: File cache (slower, larger)
    """
    
    def __init__(self, cache_dir: str = None, max_memory_items: int = 1000, default_ttl: int = 300):
        if cache_dir is None:
            cache_dir = os.path.join(project_root, 'data', 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        self.cache_dir = cache_dir
        self.max_memory_items = max_memory_items
        self.default_ttl = default_ttl
        
        # L1: Memory cache
        self._memory_cache: Dict[str, Dict] = {}
        self._cache_order = []
        
    def _generate_key(self, query: str, params: Dict = None) -> str:
        """Generate cache key from query and params."""
        key_data = f"{query}:{json.dumps(params or {})}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def _get_file_path(self, key: str) -> str:
        """Get file path for cache key."""
        return os.path.join(self.cache_dir, f"{key}.cache")
        
    def get(self, query: str, params: Dict = None, ttl: int = None) -> Optional[Any]:
        """
        Get cached result.
        
        Args:
            query: Query identifier
            params: Query parameters
            ttl: Time to live in seconds
            
        Returns:
            Cached result or None
        """
        if ttl is None:
            ttl = self.default_ttl
            
        key = self._generate_key(query, params)
        
        # L1: Memory cache
        if key in self._memory_cache:
            item = self._memory_cache[key]
            if time.time() < item['expires']:
                return item['value']
            else:
                del self._memory_cache[key]
                
        # L2: File cache
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    item = pickle.load(f)
                if time.time() < item['expires']:
                    # Promote to L1
                    self._set_memory(key, item['value'], ttl)
                    return item['value']
                else:
                    os.remove(file_path)
            except:
                pass
                
        return None
        
    def set(self, query: str, value: Any, params: Dict = None, ttl: int = None) -> bool:
        """
        Cache a result.
        
        Args:
            query: Query identifier
            value: Value to cache
            params: Query parameters
            ttl: Time to live in seconds
            
        Returns:
            True if cached successfully
        """
        if ttl is None:
            ttl = self.default_ttl
            
        key = self._generate_key(query, params)
        item = {
            'value': value,
            'expires': time.time() + ttl,
            'created': time.time()
        }
        
        # L1: Memory cache
        self._set_memory(key, value, ttl)
        
        # L2: File cache
        try:
            file_path = self._get_file_path(key)
            with open(file_path, 'wb') as f:
                pickle.dump(item, f)
            return True
        except:
            return False
            
    def _set_memory(self, key: str, value: Any, ttl: int) -> None:
        """Set memory cache with eviction."""
        # Evict if too many items
        if len(self._memory_cache) >= self.max_memory_items:
            oldest_key = self._cache_order.pop(0)
            if oldest_key in self._memory_cache:
                del self._memory_cache[oldest_key]
                
        self._memory_cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
        self._cache_order.append(key)
        
    def invalidate(self, query: str, params: Dict = None) -> bool:
        """Invalidate cached query."""
        key = self._generate_key(query, params)
        
        # Remove from memory
        if key in self._memory_cache:
            del self._memory_cache[key]
            if key in self._cache_order:
                self._cache_order.remove(key)
                
        # Remove from file
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except:
                pass
        return False
        
    def clear(self) -> int:
        """Clear all cache."""
        count = 0
        
        # Clear memory
        count = len(self._memory_cache)
        self._memory_cache.clear()
        self._cache_order.clear()
        
        # Clear files
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    try:
                        os.remove(os.path.join(self.cache_dir, filename))
                        count += 1
                    except:
                        pass
                        
        return count
        
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        memory_size = len(self._memory_cache)
        
        file_count = 0
        file_size = 0
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_count += 1
                    file_size += os.path.getsize(os.path.join(self.cache_dir, filename))
                    
        return {
            'memory_items': memory_size,
            'memory_max': self.max_memory_items,
            'file_items': file_count,
            'file_size_mb': file_size / 1024 / 1024,
            'default_ttl': self.default_ttl
        }
        
    def generate_report(self) -> str:
        """Generate cache status report."""
        stats = self.get_stats()
        
        lines = []
        lines.append("=" * 50)
        lines.append("💾 查询缓存状态")
        lines.append("=" * 50)
        lines.append(f"\n📊 L1 内存缓存")
        lines.append(f"  项目数: {stats['memory_items']}/{stats['memory_max']}")
        lines.append(f"\n📁 L2 文件缓存")
        lines.append(f"  项目数: {stats['file_items']}")
        lines.append(f"  大小: {stats['file_size_mb']:.2f} MB")
        lines.append(f"\n⏱️ 默认 TTL: {stats['default_ttl']} 秒")
        
        return "\n".join(lines)


# Global cache instance
query_cache = QueryCache()

def cache_query(ttl: int = None):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate query key from function name and args
            key_data = f"{func.__name__}:{args}:{kwargs}"
            
            # Try cache
            cached = query_cache.get(key_data, ttl=ttl)
            if cached is not None:
                return cached
                
            # Execute and cache
            result = func(*args, **kwargs)
            query_cache.set(key_data, result, ttl=ttl)
            return result
        return wrapper
    return decorator
