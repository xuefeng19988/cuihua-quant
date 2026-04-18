"""
数据库模块测试
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data.database import get_db_engine, Notes, init_db
from sqlalchemy import inspect


class TestDatabase:
    """数据库连接测试"""
    
    def test_db_connection(self):
        """测试数据库连接"""
        engine = get_db_engine()
        assert engine is not None, "数据库连接失败"
    
    def test_tables_exist(self):
        """测试表是否存在"""
        engine = get_db_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert 'notes' in tables, "notes 表不存在"
        assert 'stock_daily' in tables, "stock_daily 表不存在"
    
    def test_notes_columns(self):
        """测试notes表字段"""
        engine = get_db_engine()
        inspector = inspect(engine)
        cols = [c['name'] for c in inspector.get_columns('notes')]
        expected = ['id', 'title', 'source', 'content', 'tags', 'created_at', 'updated_at']
        for col in expected:
            assert col in cols, f"notes 表缺少字段: {col}"
    
    def test_stock_daily_columns(self):
        """测试stock_daily表字段"""
        engine = get_db_engine()
        inspector = inspect(engine)
        cols = [c['name'] for c in inspector.get_columns('stock_daily')]
        expected = ['code', 'date', 'open_price', 'high_price', 'low_price', 
                    'close_price', 'volume', 'turnover', 'change_pct', 
                    'pe_ratio', 'turnover_rate', 'updated_at']
        for col in expected:
            assert col in cols, f"stock_daily 表缺少字段: {col}"


class TestNotesModel:
    """笔记模型测试"""
    
    def test_notes_tablename(self):
        """测试表名"""
        assert Notes.__tablename__ == 'notes'
    
    def test_notes_columns_exist(self):
        """测试列存在"""
        assert hasattr(Notes, 'id')
        assert hasattr(Notes, 'title')
        assert hasattr(Notes, 'content')
        assert hasattr(Notes, 'tags')
