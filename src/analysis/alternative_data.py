"""
Phase 14.3: Alternative Data Integration
Integrates alternative data sources: news sentiment, social media, supply chain.
"""

import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.analysis.sentiment import StockSentimentAnalyzer

class AlternativeDataSource:
    """
    Integrates alternative data for enhanced factor generation.
    Sources:
    - News sentiment
    - Social media (微博, 雪球)
    - Supply chain relationships
    - Insider trading
    - Analyst ratings
    """
    
    def __init__(self):
        self.analyzer = StockSentimentAnalyzer()
        self.trendradar_dir = os.path.join(project_root, '../TrendRadar/rss/news')
        
    def get_news_sentiment_score(self, codes: List[str], days: int = 7) -> pd.DataFrame:
        """Get news sentiment scores for stocks."""
        import sqlite3
        
        results = []
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
                        text = item.get('title', '') + ' ' + item.get('content', '')
                        
                        # Find mentioned stocks
                        mentioned = self.analyzer._find_mentioned_stocks(text)
                        sentiment = self.analyzer.analyze_text(text)
                        
                        for code in mentioned:
                            if code in codes:
                                results.append({
                                    'date': date,
                                    'code': code,
                                    'sentiment_score': sentiment['score'],
                                    'sentiment_label': sentiment['label'],
                                    'news_count': 1
                                })
                conn.close()
            except Exception as e:
                print(f"⚠️ Error reading {db_path}: {e}")
                
        if results:
            df = pd.DataFrame(results)
            # Aggregate by code and date
            agg = df.groupby(['code', 'date']).agg({
                'sentiment_score': 'mean',
                'news_count': 'sum'
            }).reset_index()
            return agg
            
        return pd.DataFrame()
        
    def get_social_media_sentiment(self, codes: List[str]) -> Dict[str, float]:
        """
        Get social media sentiment from 微博/雪球.
        (Placeholder - would need API integration)
        """
        # In production, this would:
        # 1. Scrape or API fetch from 微博/雪球
        # 2. Perform sentiment analysis
        # 3. Return sentiment scores per stock
        
        return {code: 0.0 for code in codes}  # Placeholder
        
    def get_insider_trading_signal(self, codes: List[str]) -> Dict[str, float]:
        """
        Get insider trading signals.
        (Placeholder - would need data source)
        """
        # In production:
        # 1. Fetch insider trading data
        # 2. Calculate net buy/sell ratio
        # 3. Return signal scores
        
        return {code: 0.0 for code in codes}  # Placeholder
        
    def get_analyst_ratings(self, codes: List[str]) -> Dict[str, Dict]:
        """
        Get analyst ratings and price targets.
        (Placeholder - would need data source)
        """
        # In production:
        # 1. Fetch analyst ratings
        # 2. Calculate consensus rating
        # 3. Return ratings and targets
        
        return {code: {'rating': 0.0, 'target': 0.0} for code in codes}  # Placeholder
        
    def generate_alt_data_factors(self, codes: List[str]) -> pd.DataFrame:
        """
        Generate alternative data factors.
        Returns DataFrame with alternative data features.
        """
        factors = pd.DataFrame()
        
        # News sentiment factor
        news_sentiment = self.get_news_sentiment_score(codes)
        if not news_sentiment.empty:
            factors = news_sentiment.pivot(
                index='date', columns='code', values='sentiment_score'
            )
            factors.columns = [f'news_sentiment_{c}' for c in factors.columns]
            
        # Social media factor (placeholder)
        social = self.get_social_media_sentiment(codes)
        for code, score in social.items():
            factors[f'social_sentiment_{code}'] = score
            
        # Insider trading factor (placeholder)
        insider = self.get_insider_trading_signal(codes)
        for code, score in insider.items():
            factors[f'insider_signal_{code}'] = score
            
        # Analyst ratings factor (placeholder)
        ratings = self.get_analyst_ratings(codes)
        for code, rating in ratings.items():
            factors[f'analyst_rating_{code}'] = rating['rating']
            factors[f'analyst_target_{code}'] = rating['target']
            
        return factors
        
    def generate_report(self, codes: List[str]) -> str:
        """Generate alternative data report."""
        lines = []
        lines.append("=" * 50)
        lines.append("📊 另类数据因子报告")
        lines.append("=" * 50)
        
        # News sentiment
        news = self.get_news_sentiment_score(codes)
        if not news.empty:
            lines.append(f"\n📰 新闻情绪")
            for code in codes:
                code_news = news[news['code'] == code]
                if not code_news.empty:
                    avg_score = code_news['sentiment_score'].mean()
                    count = code_news['news_count'].sum()
                    icon = "🔺" if avg_score > 0.2 else ("🔻" if avg_score < -0.2 else "➖")
                    lines.append(f"  {icon} {code}: Score {avg_score:.3f} ({count} 条新闻)")
                    
        lines.append(f"\n⚠️ 社交媒体、内部交易、分析师评级需要数据源接入")
        
        return "\n".join(lines)


if __name__ == "__main__":
    alt_data = AlternativeDataSource()
    codes = ['SH.600519', 'SZ.002594', 'HK.00700']
    print(alt_data.generate_report(codes))
