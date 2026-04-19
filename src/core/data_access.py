"""
Phase 32: Unified Data Access Layer
Standardized data access with caching, error handling, and query optimization.
"""

import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

from src.core.cache import query_cache
from src.core.error_handler import retry, RetryConfig

class DataAccessLayer:
    """
    Unified data access layer with built-in caching and error handling.
    """
    
    def __init__(self, engine=None):
        self.engine = engine
        if engine is None:
            try:
                from src.data.database import get_db_engine
                self.engine = get_db_engine()
            except Exception as e:
                pass
                
    @retry(RetryConfig(max_attempts=2, delay=0.5))
    def get_stock_data(self, code: str, start_date: str = None, 
                       end_date: str = None, limit: int = None) -> pd.DataFrame:
        """
        Get stock data with caching.
        
        Args:
            code: Stock code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Max rows to return
            
        Returns:
            DataFrame with stock data
        """
        if self.engine is None:
            return pd.DataFrame()
            
        # Try cache first
        cache_key = f"stock_data:{code}:{start_date}:{end_date}:{limit}"
        cached = query_cache.get(cache_key)
        if cached is not None:
            return cached
            
        # Build query
        query = text("SELECT * FROM stock_daily WHERE code=:code")
        if start_date:
            query += f" AND date >= '{start_date}'"
        if end_date:
            query += f" AND date <= '{end_date}'"
        query += " ORDER BY date DESC"
        if limit:
            query += f" LIMIT {limit}"
            
        df = pd.read_sql(query, self.engine)
        
        # Cache result
        query_cache.set(cache_key, df, ttl=300)
        
        return df
        
    def get_latest_prices(self, codes: List[str]) -> pd.DataFrame:
        """
        Get latest prices for multiple stocks.
        
        Args:
            codes: List of stock codes
            
        Returns:
            DataFrame with latest prices
        """
        if self.engine is None or not codes:
            return pd.DataFrame()
            
        # Try cache
        cache_key = f"latest_prices:{','.join(sorted(codes))}"
        cached = query_cache.get(cache_key)
        if cached is not None:
            return cached
            
        # Get latest date
        date_query = "SELECT MAX(date) as max_date FROM stock_daily"
        date_df = pd.read_sql(date_query, self.engine)
        if date_df.empty:
            return pd.DataFrame()
            
        max_date = date_df.iloc[0]['max_date']
        codes_str = ','.join([f"'{c}'" for c in codes])
        
        query = f"""
            SELECT code, close_price, date, change_pct, volume 
            FROM stock_daily 
            WHERE date = '{max_date}' AND code IN ({codes_str})
        """
        df = pd.read_sql(query, self.engine)
        
        # Cache for 60 seconds (prices change during trading)
        query_cache.set(cache_key, df, ttl=60)
        
        return df
        
    def get_stock_list(self, pool_name: str = 'watchlist') -> List[str]:
        """Get stock list from configuration."""
        import yaml
        config_path = os.path.join(project_root, 'config', 'stocks.yaml')
        if not os.path.exists(config_path):
            return []
            
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
            
        return cfg.get('pools', {}).get(pool_name, {}).get('stocks', [])
        
    def invalidate_cache(self, code: str = None):
        """Invalidate cache for specific stock or all."""
        if code:
            # Invalidate all cache keys containing this code
            query_cache.invalidate(f"stock_data:{code}")
            query_cache.invalidate(f"latest_prices:")
        else:
            # Clear all cache
            query_cache.clear()
            
    def generate_report(self) -> str:
        """Generate data access layer report."""
        lines = []
        lines.append("=" * 50)
        lines.append("💾 数据访问层报告")
        lines.append("=" * 50)
        
        lines.append(f"\n📊 数据库连接: {'✅' if self.engine else '❌'}")
        
        cache_stats = query_cache.get_stats()
        lines.append(f"\n💾 缓存状态")
        lines.append(f"  内存项: {cache_stats['memory_items']}")
        lines.append(f"  文件项: {cache_stats['file_items']}")
        lines.append(f"  文件大小: {cache_stats['file_size_mb']:.2f} MB")
        
        return "\n".join(lines)


# Global data access layer instance
dal = DataAccessLayer()
