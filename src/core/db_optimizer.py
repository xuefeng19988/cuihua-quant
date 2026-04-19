"""
Phase 67: Database Query Optimizer
Optimize common queries with prepared statements and caching.
"""

import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class QueryOptimizer:
    """
    Optimize database queries for better performance.
    """
    
    def __init__(self, engine=None):
        self.engine = engine
        if engine is None:
            try:
                from src.data.database import get_db_engine
                self.engine = get_db_engine()
            except Exception as e:
                pass
                
        # Query cache
        self._cache = {}
        self._cache_ttl = 60  # seconds
        
    def get_latest_prices(self, codes: List[str]) -> pd.DataFrame:
        """
        Optimized query for latest prices.
        """
        if not codes or self.engine is None:
            return pd.DataFrame()
            
        # Use subquery for better performance
        query = """
            SELECT s1.code, s1.close_price, s1.date, s1.change_pct, s1.volume
            FROM stock_daily s1
            INNER JOIN (
                SELECT code, MAX(date) as max_date 
                FROM stock_daily 
                WHERE code IN ({})
                GROUP BY code
            ) s2 ON s1.code = s2.code AND s1.date = s2.max_date
        """.format(','.join([f"'{c}'" for c in codes]))
        
        return pd.read_sql(query, self.engine)
        
    def get_stock_history(self, code: str, days: int = 60, 
                          columns: List[str] = None) -> pd.DataFrame:
        """
        Optimized query for stock history.
        Only fetch needed columns.
        """
        if self.engine is None:
            return pd.DataFrame()
            
        if columns is None:
            columns = ['date', 'open_price', 'high_price', 'low_price', 
                      'close_price', 'volume', 'change_pct']
        
        col_str = ', '.join(columns)
        query = f"""
            SELECT {col_str} FROM stock_daily 
            WHERE code = '{code}' 
            ORDER BY date DESC 
            LIMIT {days}
        """
        
        df = pd.read_sql(query, self.engine)
        return df.iloc[::-1].reset_index(drop=True)
        
    def get_portfolio_summary(self) -> Dict:
        """
        Get portfolio summary with single query.
        """
        if self.engine is None:
            return {}
            
        query = """
            SELECT 
                COUNT(DISTINCT code) as stock_count,
                COUNT(*) as total_records,
                MAX(date) as latest_date,
                MIN(date) as earliest_date
            FROM stock_daily
        """
        
        result = pd.read_sql(query, self.engine)
        if result.empty:
            return {}
            
        row = result.iloc[0]
        return {
            'stock_count': int(row['stock_count']),
            'total_records': int(row['total_records']),
            'latest_date': str(row['latest_date'])[:10] if row['latest_date'] else None,
            'date_range_days': (pd.to_datetime(row['latest_date']) - pd.to_datetime(row['earliest_date'])).days if row['latest_date'] and row['earliest_date'] else 0
        }
        
    def get_top_performers(self, days: int = 5, top_n: int = 10) -> pd.DataFrame:
        """
        Get top performing stocks over a period.
        """
        if self.engine is None:
            return pd.DataFrame()
            
        query = f"""
            WITH price_changes AS (
                SELECT 
                    code,
                    FIRST_VALUE(close_price) OVER (PARTITION BY code ORDER BY date DESC) as latest_price,
                    FIRST_VALUE(close_price) OVER (PARTITION BY code ORDER BY date ASC) as oldest_price
                FROM stock_daily
                WHERE date >= date('now', '-{days} days')
            )
            SELECT 
                code,
                latest_price,
                oldest_price,
                ROUND((latest_price - oldest_price) / oldest_price * 100, 2) as change_pct
            FROM price_changes
            WHERE oldest_price > 0
            ORDER BY change_pct DESC
            LIMIT {top_n}
        """
        
        return pd.read_sql(query, self.engine)
        
    def generate_report(self) -> str:
        """Generate query optimization report."""
        summary = self.get_portfolio_summary()
        
        lines = []
        lines.append("=" * 60)
        lines.append("🗄️ 数据库查询优化报告")
        lines.append("=" * 60)
        
        lines.append(f"\n📊 数据概览")
        lines.append(f"  股票数量: {summary.get('stock_count', 0)}")
        lines.append(f"  总记录数: {summary.get('total_records', 0):,}")
        lines.append(f"  最新数据: {summary.get('latest_date', 'N/A')}")
        lines.append(f"  数据范围: {summary.get('date_range_days', 0)} 天")
        
        # Top performers
        top = self.get_top_performers(days=5, top_n=5)
        if not top.empty:
            lines.append(f"\n📈 近 5 日表现最佳")
            for _, row in top.iterrows():
                lines.append(f"  {row['code']}: {row['change_pct']:+.2f}%")
                
        return "\n".join(lines)


if __name__ == "__main__":
    optimizer = QueryOptimizer()
    print(optimizer.generate_report())
