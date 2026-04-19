"""
Extended Sentiment Analyzer
Extends basic sentiment with:
- TrendRadar news integration
- Platform-specific sentiment (微博, 知乎, 雪球)
- Stock-to-news mapping
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

class ExtendedSentimentAnalyzer:
    """
    Extended sentiment analysis with multiple data sources.
    """
    
    def __init__(self):
        self.analyzer = StockSentimentAnalyzer()
        
        # TrendRadar DB path
        self.trendradar_dir = os.path.join(project_root, '../TrendRadar/rss/news')
        
        # Stock keyword mapping (expanded)
        self.stock_keywords = {
            # A-shares
            '茅台': 'SH.600519',
            '五粮液': 'SZ.000858',
            '比亚迪': 'SZ.002594',
            '宁德时代': 'SZ.300750',
            '中国平安': 'SH.601318',
            '招商银行': 'SH.600036',
            '东方财富': 'SZ.300059',
            '海康威视': 'SZ.002415',
            '美的': 'SZ.000333',
            '格力': 'SZ.000651',
            '恒瑞': 'SH.600276',
            '中免': 'SH.601888',
            '科大讯飞': 'SZ.002230',
            '隆基': 'SH.601012',
            '亿纬锂能': 'SZ.300014',
            '长江电力': 'SH.600900',
            '中国核电': 'SH.601985',
            '华能国际': 'SH.600011',
            '中国神华': 'SH.601088',
            # HK-shares
            '小米': 'HK.01810',
            '阿里': 'HK.09988',
            '腾讯': 'HK.00700',
            '美团': 'HK.03690',
            '京东': 'HK.09618',
            '快手': 'HK.01024',
            '百度': 'HK.09888',
            '泡泡玛特': 'HK.09992',
            '名创': 'HK.09896',
            '海底捞': 'HK.06862',
            '蜜雪冰城': 'HK.02097',
            '中广核': 'HK.01816',
            '舜宇': 'HK.02382',
            '中芯': 'HK.00981',
            '网易': 'HK.09999',
        }
        
    def get_trendradar_news(self, days: int = 3) -> List[Dict]:
        """Fetch news from TrendRadar databases."""
        all_news = []
        
        for d in range(days):
            date = (datetime.now() - timedelta(days=d)).strftime('%Y-%m-%d')
            db_path = os.path.join(self.trendradar_dir, f'{date}.db')
            
            if not os.path.exists(db_path):
                continue
                
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                if tables:
                    table = tables[0][0]
                    cursor.execute(f"SELECT * FROM :table")
                    rows = cursor.fetchall()
                    cols = [desc[0] for desc in cursor.description]
                    
                    for row in rows:
                        item = dict(zip(cols, row))
                        all_news.append({
                            'title': item.get('title', ''),
                            'content': item.get('content', item.get('summary', '')),
                            'url': item.get('url', item.get('link', '')),
                            'date': item.get('date', date),
                            'source': item.get('source', 'TrendRadar')
                        })
                conn.close()
            except Exception as e:
                print(f"⚠️ Error reading {db_path}: {e}")
                
        return all_news
        
    def analyze_trendradar_sentiment(self, days: int = 3) -> pd.DataFrame:
        """
        Analyze sentiment from TrendRadar news.
        Returns DataFrame with per-stock sentiment scores.
        """
        news_items = self.get_trendradar_news(days)
        if not news_items:
            return pd.DataFrame()
            
        stock_sentiments = self.analyzer.analyze_news_for_stocks(news_items)
        agg = self.analyzer.get_aggregate_sentiment(stock_sentiments)
        
        return agg
        
    def get_stock_sentiment_report(self, codes: List[str] = None) -> str:
        """
        Generate sentiment report for specific stocks.
        """
        if codes is None:
            codes = list(self.stock_keywords.values())[:10]
            
        agg = self.analyze_trendradar_sentiment(days=3)
        
        lines = []
        lines.append("=" * 50)
        lines.append("📰 股票情绪分析报告")
        lines.append(f"📅 {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("=" * 50)
        
        if agg.empty:
            lines.append("\n⚠️ 无情绪数据")
            return "\n".join(lines)
            
        # Filter for requested codes
        agg_filtered = agg[agg['code'].isin(codes)]
        
        if agg_filtered.empty:
            lines.append("\n⚠️ 目标股票无情绪数据")
            return "\n".join(lines)
            
        for _, row in agg_filtered.iterrows():
            icon = "🔺" if row['label'] == 'positive' else ("🔻" if row['label'] == 'negative' else "➖")
            lines.append(f"  {icon} {row['code']}: Score {row['avg_score']:.3f} ({row['label']}) | 新闻: {row['news_count']}条")
            
        return "\n".join(lines)


if __name__ == "__main__":
    analyzer = ExtendedSentimentAnalyzer()
    print(analyzer.get_stock_sentiment_report())
