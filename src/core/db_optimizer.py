"""
Phase 28: Database Index Optimizer
Create and manage database indexes for better query performance.
"""

import os
import sys
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class IndexOptimizer:
    """
    Optimize database indexes for better query performance.
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(project_root, 'data', 'cuihua_quant.db')
        self.db_path = db_path
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def create_indexes(self) -> List[str]:
        """
        Create optimized indexes.
        
        Returns:
            List of created index names
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        indexes = [
            # Stock daily indexes
            ("idx_stock_daily_code_date", "stock_daily", "code, date DESC"),
            ("idx_stock_daily_date", "stock_daily", "date DESC"),
            ("idx_stock_daily_code", "stock_daily", "code"),
            ("idx_stock_daily_close", "stock_daily", "code, close_price"),
            ("idx_stock_daily_volume", "stock_daily", "code, volume"),
            ("idx_stock_daily_change", "stock_daily", "code, change_pct"),
            
            # Composite indexes for common queries
            ("idx_stock_daily_code_date_close", "stock_daily", "code, date DESC, close_price"),
            ("idx_stock_daily_date_close", "stock_daily", "date DESC, close_price"),
        ]
        
        created = []
        for idx_name, table, columns in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({columns})")
                created.append(idx_name)
            except Exception as e:
                print(f"⚠️ Failed to create index {idx_name}: {e}")
                
        conn.commit()
        conn.close()
        
        return created
        
    def drop_indexes(self) -> List[str]:
        """Drop all custom indexes."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = [row['name'] for row in cursor.fetchall()]
        
        for idx_name in indexes:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {idx_name}")
            except:
                pass
                
        conn.commit()
        conn.close()
        
        return indexes
        
    def analyze_indexes(self) -> List[Dict]:
        """Analyze current indexes."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = []
        
        for row in cursor.fetchall():
            idx_name = row['name']
            
            # Get index info
            cursor.execute(f"PRAGMA index_info('{idx_name}')")
            columns = [col['name'] for col in cursor.fetchall()]
            
            cursor.execute(f"PRAGMA index_list('{idx_name.split('_')[2]}')")
            table = idx_name.split('_')[2] if len(idx_name.split('_')) > 2 else 'unknown'
            
            indexes.append({
                'name': idx_name,
                'table': table,
                'columns': ', '.join(columns),
                'is_custom': idx_name.startswith('idx_')
            })
            
        conn.close()
        return indexes
        
    def run_vacuum(self) -> bool:
        """Vacuum database to reclaim space."""
        try:
            conn = self._get_connection()
            conn.execute("VACUUM")
            conn.close()
            return True
        except:
            return False
            
    def run_analyze(self) -> bool:
        """Run ANALYZE to update statistics."""
        try:
            conn = self._get_connection()
            conn.execute("ANALYZE")
            conn.close()
            return True
        except:
            return False
            
    def get_db_size(self) -> Dict:
        """Get database size information."""
        if not os.path.exists(self.db_path):
            return {'exists': False}
            
        size_bytes = os.path.getsize(self.db_path)
        
        return {
            'exists': True,
            'size_bytes': size_bytes,
            'size_mb': size_bytes / 1024 / 1024,
            'path': self.db_path
        }
        
    def optimize(self) -> Dict:
        """Run full optimization."""
        result = {
            'indexes_created': [],
            'vacuum': False,
            'analyze': False,
            'db_size_before': self.get_db_size(),
        }
        
        # Create indexes
        result['indexes_created'] = self.create_indexes()
        
        # Vacuum
        result['vacuum'] = self.run_vacuum()
        
        # Analyze
        result['analyze'] = self.run_analyze()
        
        result['db_size_after'] = self.get_db_size()
        
        return result
        
    def generate_report(self) -> str:
        """Generate index optimization report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🗄️ 数据库索引优化报告")
        lines.append("=" * 60)
        
        # DB size
        size = self.get_db_size()
        lines.append(f"\n📊 数据库大小")
        if size.get('exists'):
            lines.append(f"  大小: {size['size_mb']:.2f} MB")
            lines.append(f"  路径: {size['path']}")
        else:
            lines.append(f"  数据库不存在")
            
        # Indexes
        indexes = self.analyze_indexes()
        custom_indexes = [idx for idx in indexes if idx['is_custom']]
        
        lines.append(f"\n📑 索引列表 ({len(indexes)} 个)")
        lines.append(f"  自定义: {len(custom_indexes)} 个")
        lines.append(f"  系统: {len(indexes) - len(custom_indexes)} 个")
        
        if custom_indexes:
            lines.append(f"\n🔑 自定义索引")
            for idx in custom_indexes:
                lines.append(f"  ✅ {idx['name']} ON {idx['table']} ({idx['columns']})")
                
        return "\n".join(lines)


if __name__ == "__main__":
    optimizer = IndexOptimizer()
    print(optimizer.generate_report())
