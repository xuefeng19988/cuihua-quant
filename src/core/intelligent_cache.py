"""
Phase 70: Intelligent Cache System
Smart caching with predictive preloading and auto-eviction.
"""

import os
import sys
import time
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from collections import OrderedDict
import threading

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class CacheEntry:
    """Cache entry with metadata."""
    def __init__(self, key: str, value: Any, ttl: int = 300, 
                 priority: int = 1, tags: List[str] = None):
        self.key = key
        self.value = value
        self.ttl = ttl
        self.priority = priority
        self.tags = tags or []
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
        
    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl
        
    @property
    def size_bytes(self) -> int:
        try:
            return len(pickle.dumps(self.value))
        except:
            return 0


class IntelligentCache:
    """
    Intelligent cache with LRU eviction, priority, and predictive preloading.
    """
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.Lock()
        self._access_history: Dict[str, List[float]] = {}
        self._hit_count = 0
        self._miss_count = 0
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                self._miss_count += 1
                return None
                
            entry = self._cache[key]
            
            if entry.is_expired:
                del self._cache[key]
                self._miss_count += 1
                return None
                
            # Update access info
            entry.last_accessed = time.time()
            entry.access_count += 1
            self._cache.move_to_end(key)
            self._hit_count += 1
            
            # Track access pattern
            if key not in self._access_history:
                self._access_history[key] = []
            self._access_history[key].append(time.time())
            
            return entry.value
            
    def set(self, key: str, value: Any, ttl: int = 300, 
            priority: int = 1, tags: List[str] = None) -> bool:
        """Set value in cache."""
        with self._lock:
            # Evict if needed
            self._evict_if_needed()
            
            entry = CacheEntry(key, value, ttl, priority, tags)
            self._cache[key] = entry
            self._cache.move_to_end(key)
            return True
            
    def _evict_if_needed(self):
        """Evict entries if cache is full."""
        while len(self._cache) >= self.max_size or self._current_size > self.max_memory_bytes:
            if not self._cache:
                break
                
            # LRU eviction with priority consideration
            for key in list(self._cache.keys()):
                entry = self._cache[key]
                if entry.priority <= 1 or entry.is_expired:
                    del self._cache[key]
                    break
            else:
                # If all high priority, remove LRU
                self._cache.popitem(last=False)
                
    @property
    def _current_size(self) -> int:
        """Calculate current cache size in bytes."""
        return sum(entry.size_bytes for entry in self._cache.values())
        
    def invalidate(self, key: str) -> bool:
        """Invalidate a cache entry."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
            
    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all entries with a specific tag."""
        count = 0
        with self._lock:
            keys_to_remove = [
                key for key, entry in self._cache.items()
                if tag in entry.tags
            ]
            for key in keys_to_remove:
                del self._cache[key]
                count += 1
        return count
        
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total = self._hit_count + self._miss_count
        hit_rate = self._hit_count / total if total > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'memory_mb': self._current_size / 1024 / 1024,
            'max_memory_mb': self.max_memory_bytes / 1024 / 1024,
            'hits': self._hit_count,
            'misses': self._miss_count,
            'hit_rate': hit_rate,
            'avg_access_count': sum(e.access_count for e in self._cache.values()) / max(len(self._cache), 1)
        }
        
    def predict_preload(self, func: Callable, keys: List[str], 
                       threshold: float = 0.7) -> List[str]:
        """
        Predict which keys are likely to be accessed soon.
        
        Returns:
            List of keys to preload
        """
        keys_to_preload = []
        
        for key in keys:
            history = self._access_history.get(key, [])
            if len(history) >= 3:
                # Check access pattern
                intervals = [history[i+1] - history[i] for i in range(len(history)-1)]
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    time_since_last = time.time() - history[-1]
                    
                    # If next access is likely soon
                    if time_since_last > avg_interval * threshold:
                        keys_to_preload.append(key)
                        
        return keys_to_preload
        
    def generate_report(self) -> str:
        """Generate cache report."""
        stats = self.get_stats()
        
        lines = []
        lines.append("=" * 60)
        lines.append("💾 智能缓存报告")
        lines.append("=" * 60)
        
        lines.append(f"\n📊 缓存状态")
        lines.append(f"  当前大小: {stats['size']}/{stats['max_size']} 项")
        lines.append(f"  内存使用: {stats['memory_mb']:.2f}/{stats['max_memory_mb']:.0f} MB")
        
        lines.append(f"\n📈 命中率统计")
        lines.append(f"  命中: {stats['hits']}")
        lines.append(f"  未命中: {stats['misses']}")
        lines.append(f"  命中率: {stats['hit_rate']:.1%}")
        lines.append(f"  平均访问次数: {stats['avg_access_count']:.1f}")
        
        # Top accessed keys
        if self._cache:
            top_keys = sorted(self._cache.items(), 
                            key=lambda x: x[1].access_count, 
                            reverse=True)[:5]
            lines.append(f"\n🔥 最常访问")
            for key, entry in top_keys:
                lines.append(f"  {key}: {entry.access_count} 次")
                
        return "\n".join(lines)


class CacheDecorator:
    """
    Decorator for caching function results.
    """
    def __init__(self, cache: IntelligentCache, ttl: int = 300, 
                 key_prefix: str = '', tags: List[str] = None):
        self.cache = cache
        self.ttl = ttl
        self.key_prefix = key_prefix
        self.tags = tags or []
        
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{self.key_prefix}{func.__name__}:{args}:{kwargs}"
            key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try cache
            result = self.cache.get(key)
            if result is not None:
                return result
                
            # Execute and cache
            result = func(*args, **kwargs)
            self.cache.set(key, result, self.ttl, tags=self.tags)
            return result
            
        wrapper.cache_clear = lambda: self.cache.invalidate(key_data)
        return wrapper


if __name__ == "__main__":
    print("✅ Intelligent Cache System loaded")
    
    # Test cache
    cache = IntelligentCache(max_size=100, max_memory_mb=10)
    
    # Set some values
    for i in range(50):
        cache.set(f"key_{i}", f"value_{i}", ttl=60, priority=1)
        
    # Get some values
    for i in range(30):
        cache.get(f"key_{i}")
        
    # Print report
    print(cache.generate_report())
