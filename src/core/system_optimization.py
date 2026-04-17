"""
Phase 65: System Optimization
Performance improvements, code cleanup, and feature enhancements.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Callable
from functools import lru_cache

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class SignalOptimizer:
    """
    Optimize signal generation with caching and vectorization.
    """
    
    @staticmethod
    @lru_cache(maxsize=128)
    def cached_rsi(closes_tuple: tuple, period: int = 14) -> np.ndarray:
        """Cached RSI calculation."""
        closes = np.array(closes_tuple)
        delta = np.diff(closes)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        avg_gain = np.convolve(gain, np.ones(period)/period, mode='valid')
        avg_loss = np.convolve(loss, np.ones(period)/period, mode='valid')
        
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        # Pad to match original length
        return np.concatenate([np.full(period, 50), rsi])
        
    @staticmethod
    def vectorized_macd(closes: np.ndarray, fast: int = 12, 
                       slow: int = 26, signal: int = 9) -> tuple:
        """Vectorized MACD calculation."""
        ema_fast = pd.Series(closes).ewm(span=fast, adjust=False).mean().values
        ema_slow = pd.Series(closes).ewm(span=slow, adjust=False).mean().values
        macd = ema_fast - ema_slow
        signal_line = pd.Series(macd).ewm(span=signal, adjust=False).mean().values
        histogram = macd - signal_line
        
        return macd, signal_line, histogram
        
    @staticmethod
    def batch_calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators in batch for better performance."""
        result = df.copy()
        
        # Vectorized calculations
        closes = df['close'].values
        
        # Moving averages
        for period in [5, 10, 20, 60]:
            result[f'ma_{period}'] = pd.Series(closes).rolling(period).mean().values
            
        # RSI (cached)
        result['rsi_14'] = SignalOptimizer.cached_rsi(tuple(closes), 14)
        
        # MACD (vectorized)
        macd, signal, hist = SignalOptimizer.vectorized_macd(closes)
        result['macd'] = macd
        result['macd_signal'] = signal
        result['macd_hist'] = hist
        
        # Bollinger Bands
        ma20 = result['ma_20']
        std20 = pd.Series(closes).rolling(20).std().values
        result['bb_upper'] = ma20 + 2 * std20
        result['bb_lower'] = ma20 - 2 * std20
        
        return result


class MemoryOptimizer:
    """
    Optimize memory usage for large datasets.
    """
    
    @staticmethod
    def downcast_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Downcast numeric columns to save memory."""
        optimized = df.copy()
        
        for col in optimized.columns:
            dtype = optimized[col].dtype
            
            if dtype == 'float64':
                optimized[col] = pd.to_numeric(optimized[col], downcast='float')
            elif dtype == 'int64':
                optimized[col] = pd.to_numeric(optimized[col], downcast='integer')
            elif dtype == 'object':
                nunique = optimized[col].nunique()
                if nunique / len(optimized[col]) < 0.5:
                    optimized[col] = optimized[col].astype('category')
                    
        return optimized
        
    @staticmethod
    def chunked_processing(items: list, chunk_size: int = 1000, 
                          processor: Callable = None) -> list:
        """Process items in chunks to save memory."""
        results = []
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i+chunk_size]
            if processor:
                results.extend(processor(chunk))
            else:
                results.extend(chunk)
        return results


class FeatureCache:
    """
    Cache for computed features to avoid recalculation.
    """
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        
    def get(self, key: str) -> Optional[pd.DataFrame]:
        """Get cached features."""
        if key in self.cache:
            self.cache[key]['last_access'] = datetime.now()
            return self.cache[key]['data']
        return None
        
    def set(self, key: str, data: pd.DataFrame, ttl: int = 3600):
        """Cache features with TTL."""
        if len(self.cache) >= self.max_size:
            # Remove oldest
            oldest = min(self.cache.items(), key=lambda x: x[1]['last_access'])
            del self.cache[oldest[0]]
            
        self.cache[key] = {
            'data': data,
            'created': datetime.now(),
            'last_access': datetime.now(),
            'ttl': ttl
        }
        
    def clean_expired(self):
        """Remove expired cache entries."""
        now = datetime.now()
        expired = [k for k, v in self.cache.items() 
                  if (now - v['created']).total_seconds() > v['ttl']]
        for k in expired:
            del self.cache[k]
            
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': 'N/A'
        }


if __name__ == "__main__":
    print("✅ Phase 65: System Optimization modules loaded")
    
    # Test memory optimization
    np.random.seed(42)
    df = pd.DataFrame({
        'float64_col': np.random.randn(10000),
        'int64_col': np.random.randint(0, 100, 10000),
        'category_col': np.random.choice(['A', 'B', 'C'], 10000)
    })
    
    optimizer = MemoryOptimizer()
    original_size = df.memory_usage(deep=True).sum()
    optimized_df = optimizer.downcast_dataframe(df)
    optimized_size = optimized_df.memory_usage(deep=True).sum()
    
    print(f"\n💾 内存优化")
    print(f"  原始大小: {original_size / 1024:.1f} KB")
    print(f"  优化后大小: {optimized_size / 1024:.1f} KB")
    print(f"  节省: {(1 - optimized_size / original_size) * 100:.1f}%")
