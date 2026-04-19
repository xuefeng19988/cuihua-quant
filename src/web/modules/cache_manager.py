"""
Phase 268: 高级缓存管理器
- 智能缓存键生成 (考虑 request args)
- 缓存预热/失效机制
- 分层 TTL 策略
- ETag 支持
- 统计追踪
"""
import time
import hashlib
import json
import functools
from threading import Lock, RLock
from collections import OrderedDict


class CacheStats:
    """缓存统计"""
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.invalidations = 0
        self.evictions = 0

    @property
    def hit_rate(self):
        total = self.hits + self.misses
        return round(self.hits / total * 100, 2) if total > 0 else 0

    @property
    def total(self):
        return self.hits + self.misses

    def to_dict(self):
        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'invalidations': self.invalidations,
            'evictions': self.evictions,
            'hit_rate': f"{self.hit_rate}%",
            'total_requests': self.total
        }

    def reset(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.invalidations = 0
        self.evictions = 0


class LRUCacheEntry:
    """LRU 缓存条目"""
    __slots__ = ['value', 'expire', 'last_access', 'size_bytes']

    def __init__(self, value, expire, size_bytes=0):
        self.value = value
        self.expire = expire
        self.last_access = time.time()
        self.size_bytes = size_bytes


class AdvancedCache:
    """高级 LRU + TTL 缓存"""

    # TTL 常量 (秒)
    TTL_STOCK_LIST = 300       # 股票列表 5分钟
    TTL_QUOTE = 30             # 实时行情 30秒
    TL_SCORE = 120             # 评分 2分钟
    TL_RANKING = 180           # 排行 3分钟
    TTL_CHART = 300            # 图表 5分钟
    TTL_STATIC = 3600          # 静态数据 1小时
    TL_DEFAULT = 300           # 默认 5分钟

    def __init__(self, max_items=5000, max_memory_mb=256):
        self._cache = OrderedDict()
        self._lock = RLock()
        self._max_items = max_items
        self._max_memory_bytes = max_memory_mb * 1024 * 1024
        self._current_memory = 0
        self.stats = CacheStats()
        self._prefix_groups = {}  # prefix -> set of keys

    def get(self, key):
        """获取缓存，命中则更新 LRU 位置"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() < entry.expire:
                    entry.last_access = time.time()
                    self._cache.move_to_end(key)
                    self.stats.hits += 1
                    return entry.value
                else:
                    self._remove(key)
            self.stats.misses += 1
            return None

    def set(self, key, value, ttl=None, prefix=''):
        """设置缓存"""
        if ttl is None:
            ttl = self.TTL_DEFAULT
        with self._lock:
            now = time.time()
            # 检查是否已存在，先移除旧值
            if key in self._cache:
                self._remove(key)

            # 内存检查
            value_str = json.dumps(value) if not isinstance(value, (str, bytes)) else value
            size = len(value_str.encode('utf-8')) if isinstance(value_str, str) else len(value_str)

            while self._current_memory + size > self._max_memory_bytes and self._cache:
                self._evict_lru()

            # 容量检查
            while len(self._cache) >= self._max_items and self._cache:
                self._evict_lru()

            self._cache[key] = LRUCacheEntry(value, now + ttl, size)
            self._cache.move_to_end(key)
            self._current_memory += size
            self.stats.sets += 1

            # 注册前缀索引
            if prefix:
                if prefix not in self._prefix_groups:
                    self._prefix_groups[prefix] = set()
                self._prefix_groups[prefix].add(key)

            return True

    def delete(self, key):
        """删除单个缓存"""
        with self._lock:
            self._remove(key)
            self.stats.invalidations += 1

    def invalidate_prefix(self, prefix):
        """批量失效：按前缀清除"""
        with self._lock:
            keys = self._prefix_groups.pop(prefix, set())
            for key in keys:
                self._remove(key)
            self.stats.invalidations += len(keys)
            return len(keys)

    def invalidate_pattern(self, pattern):
        """模式匹配失效 (简单包含匹配)"""
        with self._lock:
            to_remove = [k for k in self._cache if pattern in k]
            for key in to_remove:
                self._remove(key)
            self.stats.invalidations += len(to_remove)
            return len(to_remove)

    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._prefix_groups.clear()
            self._current_memory = 0
            self.stats.reset()

    def warm_up(self, keys_and_values):
        """预热缓存: [(key, value, ttl), ...]"""
        with self._lock:
            for key, value, ttl in keys_and_values:
                if key not in self._cache:
                    self.set(key, value, ttl)

    def get_etag(self, key):
        """生成 ETag"""
        entry = self.get(key)
        if entry is None:
            return None
        content = json.dumps(entry) if not isinstance(entry, str) else entry
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def to_dict(self):
        return {
            'size': len(self._cache),
            'max_items': self._max_items,
            'memory_mb': round(self._current_memory / (1024 * 1024), 2),
            'max_memory_mb': self._max_memory_bytes / (1024 * 1024),
            'stats': self.stats.to_dict(),
            'prefix_groups': len(self._prefix_groups)
        }

    def _remove(self, key):
        """内部移除 (需持有锁)"""
        if key in self._cache:
            entry = self._cache.pop(key)
            self._current_memory -= entry.size_bytes
            # 从所有前缀组中移除
            for keys in self._prefix_groups.values():
                keys.discard(key)

    def _evict_lru(self):
        """驱逐最近最少使用 (需持有锁)"""
        if self._cache:
            key, entry = self._cache.popitem(last=False)
            self._current_memory -= entry.size_bytes
            self.stats.evictions += 1
            for keys in self._prefix_groups.values():
                keys.discard(key)


def make_cache_key(prefix, *args, **kwargs):
    """智能缓存键生成"""
    # 排序 kwargs 保证一致性
    parts = [prefix]
    parts.extend(str(a) for a in args)
    for k in sorted(kwargs.keys()):
        parts.append(f"{k}={kwargs[k]}")
    raw = '|'.join(parts)
    # 短键用原文，长键用 hash
    if len(raw) < 120:
        return f"cache:{raw}"
    return f"cache:{prefix}:{hashlib.md5(raw.encode()).hexdigest()[:12]}"


# 全局实例
advanced_cache = AdvancedCache(max_items=5000, max_memory_mb=256)


def api_cached(ttl=None, prefix='api', key_func=None):
    """API 缓存装饰器 (Flask aware)"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取 Flask request 参数
            try:
                from flask import request
                req_args = dict(request.args)
                req_data = {}
                if request.is_json and request.json:
                    req_data = request.json
                # 合并参数生成键
                all_params = {}
                all_params.update(req_args)
                all_params.update(req_data)
                if key_func:
                    cache_key = key_func(prefix, func.__name__, all_params)
                else:
                    sorted_params = sorted(all_params.items(), key=lambda x: x[0])
                    cache_key = make_cache_key(prefix, func.__name__, *sorted_params)
            except RuntimeError:
                # 不在 Flask 请求上下文中
                cache_key = make_cache_key(prefix, func.__name__, *args)

            result = advanced_cache.get(cache_key)
            if result is not None:
                return result

            result = func(*args, **kwargs)

            # 只缓存成功的响应
            try:
                if hasattr(result, 'get_json'):
                    json_data = result.get_json()
                    if json_data and json_data.get('code') == 200:
                        advanced_cache.set(cache_key, result, ttl, prefix=prefix)
                elif isinstance(result, dict) and result.get('code') == 200:
                    advanced_cache.set(cache_key, result, ttl, prefix=prefix)
            except Exception:
                pass  # 不缓存异常结果

            return result
        return wrapper
    return decorator


def invalidate_api_cache(prefix):
    """失效指定前缀的所有缓存"""
    return advanced_cache.invalidate_prefix(prefix)
