"""
Phase 71: WebUI Performance Optimization
Frontend and backend performance optimizations.
"""

import os
import sys
from typing import Dict, List, Callable
from functools import lru_cache
import time

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class ResponseOptimizer:
    """
    Optimize HTTP responses for better performance.
    """
    
    @staticmethod
    def compress_response(data: str, min_length: int = 1000) -> str:
        """
        Compress response by removing whitespace.
        """
        if len(data) < min_length:
            return data
            
        # Remove extra whitespace
        import re
        data = re.sub(r'\s+', ' ', data)
        data = re.sub(r'>\s+<', '><', data)
        
        return data
        
    @staticmethod
    def add_cache_headers(headers: Dict, ttl: int = 300) -> Dict:
        """
        Add caching headers to response.
        """
        headers['Cache-Control'] = f'public, max-age={ttl}'
        headers['ETag'] = f'"{hash(str(headers))}"'
        return headers
        
    @staticmethod
    def paginate_response(items: List, page: int = 1, 
                         per_page: int = 20) -> Dict:
        """
        Paginate response data.
        """
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'items': items[start:end],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page,
                'has_next': end < total,
                'has_prev': page > 1
            }
        }


class QueryPerformanceMonitor:
    """
    Monitor and optimize query performance.
    """
    def __init__(self):
        self.query_log: List[Dict] = []
        self.slow_query_threshold = 1.0  # seconds
        
    def monitor_query(self, func: Callable) -> Callable:
        """
        Decorator to monitor query performance.
        """
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            log_entry = {
                'function': func.__name__,
                'duration': duration,
                'timestamp': time.time(),
                'is_slow': duration > self.slow_query_threshold
            }
            self.query_log.append(log_entry)
            
            if log_entry['is_slow']:
                print(f"⚠️ Slow query: {func.__name__} took {duration:.3f}s")
                
            return result
            
        return wrapper
        
    def get_performance_report(self) -> Dict:
        """
        Get query performance report.
        """
        if not self.query_log:
            return {'total_queries': 0}
            
        durations = [q['duration'] for q in self.query_log]
        slow_queries = [q for q in self.query_log if q['is_slow']]
        
        return {
            'total_queries': len(self.query_log),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'slow_queries': len(slow_queries),
            'slow_query_rate': len(slow_queries) / len(self.query_log)
        }


class FrontendOptimizer:
    """
    Optimize frontend assets and loading.
    """
    
    @staticmethod
    def generate_service_worker() -> str:
        """
        Generate optimized service worker for caching.
        """
        return """
const CACHE_NAME = 'cuihua-quant-v1';
const STATIC_ASSETS = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/icons/icon-192.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) return response;
      return fetch(event.request).then((response) => {
        if (!response || response.status !== 200) return response;
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return response;
      });
    })
  );
});
"""
        
    @staticmethod
    def optimize_css(css: str) -> str:
        """
        Minify CSS.
        """
        import re
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        # Remove whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
        return css.strip()
        
    @staticmethod
    def optimize_js(js: str) -> str:
        """
        Minify JavaScript.
        """
        import re
        # Remove single-line comments
        js = re.sub(r'//.*$', '', js, flags=re.MULTILINE)
        # Remove multi-line comments
        js = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL)
        # Remove extra whitespace
        js = re.sub(r'\s+', ' ', js)
        return js.strip()


if __name__ == "__main__":
    print("✅ WebUI Performance Optimization modules loaded")
    
    # Test response optimizer
    optimizer = ResponseOptimizer()
    
    # Test pagination
    items = list(range(100))
    result = optimizer.paginate_response(items, page=2, per_page=10)
    print(f"\n📄 Pagination Test:")
    print(f"  Items: {len(result['items'])}")
    print(f"  Page: {result['pagination']['page']}")
    print(f"  Total pages: {result['pagination']['pages']}")
    
    # Test query monitor
    monitor = QueryPerformanceMonitor()
    
    @monitor.monitor_query
    def slow_function():
        time.sleep(0.5)
        return "done"
        
    slow_function()
    print(f"\n📊 Performance Report:")
    for k, v in monitor.get_performance_report().items():
        print(f"  {k}: {v}")
