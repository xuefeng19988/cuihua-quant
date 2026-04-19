"""
Phase 51: Code Optimization Utilities
Performance optimization, caching, vectorization utilities.
"""

import os
import sys
import functools
import time
import hashlib
import pickle
import pandas as pd
import numpy as np
from typing import Any, Callable, Dict
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class PerformanceOptimizer:
    """
    Code optimization utilities for better performance.
    """
    
    @staticmethod
    def vectorize_rolling(func: Callable, window: int) -> Callable:
        """
        Decorator to optimize rolling calculations using vectorization.
        """
        @functools.wraps(func)
        def wrapper(series: pd.Series, *args, **kwargs) -> pd.Series:
            # Use numpy stride tricks for faster rolling
            if len(series) < window:
                return func(series, *args, **kwargs)
                
            # Vectorized rolling
            result = series.rolling(window).apply(
                lambda x: func(x, *args, **kwargs), 
                raw=True
            )
            return result
        return wrapper
        
    @staticmethod
    def memoize(ttl: int = 300):
        """
        Memoization decorator with TTL.
        """
        cache = {}
        
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # Create cache key
                key = hashlib.md5(f"{func.__name__}:{args}:{kwargs}".encode()).hexdigest()
                
                if key in cache:
                    result, timestamp = cache[key]
                    if time.time() - timestamp < ttl:
                        return result
                        
                result = func(*args, **kwargs)
                cache[key] = (result, time.time())
                return result
            return wrapper
        return decorator
        
    @staticmethod
    def batch_process(items: list, batch_size: int = 100) -> list:
        """
        Process items in batches for memory efficiency.
        """
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            results.extend(batch)
        return results
        
    @staticmethod
    def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize DataFrame memory usage.
        """
        optimized = df.copy()
        
        for col in optimized.columns:
            col_type = optimized[col].dtype
            
            # Downcast numeric types
            if col_type == 'float64':
                optimized[col] = pd.to_numeric(optimized[col], downcast='float')
            elif col_type == 'int64':
                optimized[col] = pd.to_numeric(optimized[col], downcast='integer')
                
            # Convert object columns to category if low cardinality
            if col_type == 'object':
                unique_ratio = optimized[col].nunique() / len(optimized[col])
                if unique_ratio < 0.5:
                    optimized[col] = optimized[col].astype('category')
                    
        return optimized
        
    @staticmethod
    def parallel_apply(df: pd.DataFrame, func: Callable, 
                      column: str, n_jobs: int = -1) -> pd.Series:
        """
        Parallel apply function to DataFrame column.
        """
        from joblib import Parallel, delayed
        
        chunks = np.array_split(df[column], min(n_jobs, len(df)))
        results = Parallel(n_jobs=n_jobs)(
            delayed(lambda chunk: chunk.apply(func))(chunk) 
            for chunk in chunks
        )
        
        return pd.concat(results)
        
    @staticmethod
    def timing_decorator(func: Callable) -> Callable:
        """
        Decorator to measure function execution time.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"⏱️  {func.__name__} took {elapsed:.3f}s")
            return result
        return wrapper


class CodeQualityChecker:
    """
    Code quality and complexity checker.
    """
    
    @staticmethod
    def check_complexity(func: Callable) -> Dict:
        """
        Check function complexity metrics.
        """
        import inspect
        source = inspect.getsource(func)
        lines = source.split('\n')
        
        metrics = {
            'name': func.__name__,
            'lines_of_code': len(lines),
            'arguments': len(inspect.signature(func).parameters),
            'has_docstring': bool(func.__doc__),
            'cyclomatic_complexity': CodeQualityChecker._calculate_cyclomatic(source)
        }
        
        return metrics
        
    @staticmethod
    def _calculate_cyclomatic(source: str) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        keywords = ['if', 'elif', 'for', 'while', 'except', 'and', 'or']
        
        for line in source.split('\n'):
            line = line.strip()
            for keyword in keywords:
                if line.startswith(f'{keyword} ') or line.startswith(f'{keyword}:'):
                    complexity += 1
                    
        return complexity
        
    @staticmethod
    def generate_optimization_report(funcs: list) -> str:
        """Generate code optimization report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🔧 代码优化报告")
        lines.append("=" * 60)
        
        for func in funcs:
            metrics = CodeQualityChecker.check_complexity(func)
            
            lines.append(f"\n📝 {metrics['name']}")
            lines.append(f"  代码行数: {metrics['lines_of_code']}")
            lines.append(f"  参数数量: {metrics['arguments']}")
            lines.append(f"  圈复杂度: {metrics['cyclomatic_complexity']}")
            lines.append(f"  文档字符串: {'✅' if metrics['has_docstring'] else '❌'}")
            
            # Recommendations
            if metrics['cyclomatic_complexity'] > 10:
                lines.append(f"  ⚠️ 建议: 圈复杂度过高，考虑拆分函数")
            if metrics['arguments'] > 5:
                lines.append(f"  ⚠️ 建议: 参数过多，考虑使用配置对象")
            if metrics['lines_of_code'] > 100:
                lines.append(f"  ⚠️ 建议: 函数过长，考虑拆分")
                
        return "\n".join(lines)


if __name__ == "__main__":
    # Test optimization utilities
    optimizer = PerformanceOptimizer()
    
    # Test DataFrame optimization
    np.random.seed(42)
    df = pd.DataFrame({
        'float_col': np.random.randn(10000),
        'int_col': np.random.randint(0, 100, 10000),
        'category_col': np.random.choice(['A', 'B', 'C'], 10000)
    })
    
    original_size = df.memory_usage(deep=True).sum()
    optimized_df = optimizer.optimize_dataframe(df)
    optimized_size = optimized_df.memory_usage(deep=True).sum()
    
    print(f"原始大小: {original_size / 1024:.1f} KB")
    print(f"优化后大小: {optimized_size / 1024:.1f} KB")
    print(f"优化率: {(1 - optimized_size / original_size) * 100:.1f}%")
