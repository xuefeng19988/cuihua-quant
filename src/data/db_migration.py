"""
Phase 11.4: Database Migration Tool
Migrate from SQLite to PostgreSQL for production.
"""

import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

class DatabaseMigrator:
    """
    Handles database migration from SQLite to PostgreSQL.
    Supports: schema migration, data migration, validation.
    """
    
    def __init__(self, sqlite_path: str = None, postgres_url: str = None):
        if sqlite_path is None:
            sqlite_path = os.path.join(project_root, 'data', 'cuihua_quant.db')
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url or os.getenv('POSTGRES_URL', '')
        
    def validate_sqlite(self) -> Dict:
        """Validate SQLite database."""
        import sqlite3
        
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get row counts
            counts = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM :table")
                counts[table] = cursor.fetchone()[0]
                
            conn.close()
            
            return {
                'status': 'OK',
                'tables': tables,
                'row_counts': counts
            }
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
            
    def migrate_data(self, table: str = 'stock_daily', batch_size: int = 1000) -> Dict:
        """
        Migrate data from SQLite to PostgreSQL.
        
        Args:
            table: Table name to migrate
            batch_size: Number of rows per batch
            
        Returns:
            Migration result
        """
        if not self.postgres_url:
            return {'status': 'ERROR', 'message': 'PostgreSQL URL not configured'}
            
        try:
            from sqlalchemy import create_engine
            
            # Source (SQLite)
            sqlite_engine = create_engine(f'sqlite:///{self.sqlite_path}')
            
            # Destination (PostgreSQL)
            postgres_engine = create_engine(self.postgres_url)
            
            # Read from SQLite
            df = pd.read_sql(f"SELECT * FROM :table", sqlite_engine)
            
            if df.empty:
                return {'status': 'WARN', 'message': f'No data in {table}'}
                
            # Write to PostgreSQL in batches
            total_rows = len(df)
            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i+batch_size]
                batch.to_sql(table, postgres_engine, if_exists='append', index=False)
                print(f"  Migrated {min(i+batch_size, total_rows)}/{total_rows} rows")
                
            return {
                'status': 'OK',
                'table': table,
                'rows_migrated': total_rows
            }
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
            
    def validate_migration(self, table: str = 'stock_daily') -> Dict:
        """Validate migrated data."""
        if not self.postgres_url:
            return {'status': 'ERROR', 'message': 'PostgreSQL URL not configured'}
            
        try:
            from sqlalchemy import create_engine
            
            sqlite_engine = create_engine(f'sqlite:///{self.sqlite_path}')
            postgres_engine = create_engine(self.postgres_url)
            
            # Count rows
            sqlite_count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM :table", sqlite_engine).iloc[0]['cnt']
            postgres_count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM :table", postgres_engine).iloc[0]['cnt']
            
            match = sqlite_count == postgres_count
            
            return {
                'status': 'OK' if match else 'WARN',
                'table': table,
                'sqlite_count': sqlite_count,
                'postgres_count': postgres_count,
                'match': match
            }
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
            
    def generate_migration_report(self) -> str:
        """Generate migration report."""
        lines = []
        lines.append("=" * 50)
        lines.append("🗄️ 数据库迁移报告")
        lines.append("=" * 50)
        
        # Validate source
        sqlite_status = self.validate_sqlite()
        lines.append(f"\n📊 SQLite 状态")
        if sqlite_status['status'] == 'OK':
            lines.append(f"  表数: {len(sqlite_status['tables'])}")
            for table, count in sqlite_status['row_counts'].items():
                lines.append(f"  {table}: {count} 行")
        else:
            lines.append(f"  ❌ {sqlite_status.get('message', 'Error')}")
            
        # Validate destination
        if self.postgres_url:
            lines.append(f"\n📊 PostgreSQL 状态")
            validation = self.validate_migration()
            if validation['status'] == 'OK':
                lines.append(f"  ✅ 数据一致 ({validation['postgres_count']} 行)")
            else:
                lines.append(f"  ⚠️ {validation.get('message', 'Validation failed')}")
        else:
            lines.append(f"\n⚠️ PostgreSQL 未配置")
            
        return "\n".join(lines)


if __name__ == "__main__":
    migrator = DatabaseMigrator()
    print(migrator.validate_sqlite())
    print(migrator.generate_migration_report())
