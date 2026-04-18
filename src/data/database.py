"""
Database Module
Defines the ORM models and database connection.
"""

import os
import yaml
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Date, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load env vars
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

Base = declarative_base()

class Notes(Base):
    """
    Table: notes
    Stores user notes with rich text content.
    """
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="笔记ID")
    title = Column(String(200), nullable=False, comment="笔记标题")
    source = Column(String(100), default='', comment="来源")
    content = Column(Text, comment="笔记内容 (HTML)")
    tags = Column(String(500), default='', comment="标签 (逗号分隔)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class StockDaily(Base):
    """
    Table: stock_daily
    Stores daily OHLCV data.
    """
    __tablename__ = 'stock_daily'
    
    # Composite Key: Code + Date
    code = Column(String(16), primary_key=True, nullable=False, comment="Futu Code, e.g., HK.00700")
    date = Column(Date, primary_key=True, nullable=False, comment="Trading Date")
    
    # OHLCV
    open_price = Column(Float, comment="Open Price")
    high_price = Column(Float, comment="High Price")
    low_price = Column(Float, comment="Low Price")
    close_price = Column(Float, comment="Close Price")
    volume = Column(Float, comment="Volume (Shares)")
    turnover = Column(Float, comment="Turnover (Amount)")
    
    # Metrics
    change_pct = Column(Float, comment="Change Percentage (%)")
    pe_ratio = Column(Float, comment="PE Ratio")
    turnover_rate = Column(Float, comment="Turnover Rate (%)")
    
    # Meta
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

def get_db_engine():
    """Returns a SQLAlchemy engine based on config."""
    # Load config to get DB path
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'app.yaml')
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
        db_url = cfg.get('database', {}).get('url', 'sqlite:///data/cuihua_quant.db')
    else:
        db_url = 'sqlite:///data/cuihua_quant.db'
        
    # Ensure relative path is resolved correctly
    if db_url.startswith('sqlite:///') and not db_url.startswith('sqlite:////'):
        relative_path = db_url.replace('sqlite:///', '')
        # Resolve relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        absolute_path = os.path.join(project_root, relative_path)
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
        db_url = f'sqlite:///{absolute_path}'
        
    return create_engine(db_url, echo=False)

def init_db():
    """Create all tables."""
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    print("✅ 数据库表初始化成功 (包含 notes 表)")


class NoteArticles(Base):
    """
    Table: note_articles
    公众号风格笔记文章表 (Phase 218)
    """
    __tablename__ = 'note_articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="文章ID")
    title = Column(String(300), nullable=False, comment="文章标题")
    subtitle = Column(String(200), default='', comment="副标题/摘要")
    author = Column(String(100), default='', comment="作者")
    cover_url = Column(String(500), default='', comment="封面图URL")
    content = Column(Text, comment="文章内容 (HTML)")
    content_md = Column(Text, comment="文章内容 (Markdown)")
    tags = Column(String(500), default='', comment="标签 (逗号分隔)")
    category = Column(String(100), default='', comment="分类")
    status = Column(String(20), default='draft', comment="状态: draft/published/archived")
    views = Column(Integer, default=0, comment="浏览次数")
    likes = Column(Integer, default=0, comment="点赞数")
    is_top = Column(Integer, default=0, comment="是否置顶 0/1")
    published_at = Column(DateTime, nullable=True, comment="发布时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
