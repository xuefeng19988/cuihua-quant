"""
News Sentiment Integration
Fetches news from TrendRadar and generates sentiment scores for stocks.
"""

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.analysis.sentiment import StockSentimentAnalyzer

class NewsSentimentFetcher:
    """
    Fetches news from TrendRadar database and analyzes sentiment for stocks.
    """
    
    def __init__(self, trendradar_dir: str = None):
        if trendradar_dir is None:
            trendradar_dir = os.path.join(project_root, '../TrendRadar/rss/news')
        self.trendradar_dir = trendradar_dir
        self.analyzer = StockSentimentAnalyzer()
        
    def get_latest_db(self) -> str:
        """Find latest TrendRadar DB."""
        for days in range(3):
            date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            db_path = os.path.join(self.trendradar_dir, f'{date}.db')
            if os.path.exists(db_path):
                return db_path
        return None
        
    def fetch_news(self, limit: int = 100) -> List[Dict]:
        """Fetch news items from TrendRadar DB."""
        db_path = self.get_latest_db()
        if not db_path:
            return []
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if not tables:
                conn.close()
                return []
                
            table = tables[0][0]
            cursor.execute(f"SELECT * FROM {table} LIMIT {limit}")
            rows = cursor.fetchall()
            if not rows:
                conn.close()
                return []
                
            cols = [d[0] for d in cursor.description]
            news = []
            for row in rows:
                item = dict(zip(cols, row))
                news.append({
                    'title': item.get('title', ''),
                    'content': item.get('content', item.get('summary', '')),
                    'url': item.get('url', item.get('link', '')),
                    'date': item.get('date', item.get('created_at', ''))
                })
            conn.close()
            return news
        except Exception as e:
            print(f"⚠️ News fetch error: {e}")
            return []
            
    def analyze_and_score(self, codes: List[str]) -> Dict[str, float]:
        """Analyze news sentiment for stocks."""
        news_items = self.fetch_news()
        if not news_items:
            return {}
            
        stock_sentiments = self.analyzer.analyze_news_for_stocks(news_items)
        agg = self.analyzer.get_aggregate_sentiment(stock_sentiments)
        
        if agg.empty:
            return {}
            
        return dict(zip(agg['code'], agg['avg_score']))
