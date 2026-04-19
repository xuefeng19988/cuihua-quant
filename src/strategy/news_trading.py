"""
Phase 39: News Trading Strategy
Trade based on news sentiment and events.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class NewsTradingStrategy:
    """
    News-based trading strategy.
    """
    
    def __init__(self, sentiment_threshold: float = 0.3):
        self.sentiment_threshold = sentiment_threshold
        self.news_history: List[Dict] = []
        self.trades: List[Dict] = []
        
    def analyze_news_impact(self, news_items: List[Dict], 
                           stock_mapping: Dict[str, str]) -> Dict:
        """
        Analyze news impact on stocks.
        
        Args:
            news_items: List of news with sentiment
            stock_mapping: Dict mapping keywords to stock codes
            
        Returns:
            Stock sentiment scores
        """
        stock_sentiments = {}
        
        for news in news_items:
            sentiment = news.get('sentiment_score', 0)
            title = news.get('title', '').lower()
            content = news.get('content', '').lower()
            text = title + ' ' + content
            
            for keyword, code in stock_mapping.items():
                if keyword.lower() in text:
                    if code not in stock_sentiments:
                        stock_sentiments[code] = []
                    stock_sentiments[code].append(sentiment)
                    
        # Average sentiment per stock
        result = {}
        for code, sentiments in stock_sentiments.items():
            result[code] = {
                'avg_sentiment': np.mean(sentiments),
                'news_count': len(sentiments),
                'max_sentiment': max(sentiments),
                'min_sentiment': min(sentiments)
            }
            
        return result
        
    def generate_signals(self, sentiment_data: Dict, 
                        current_prices: Dict[str, float]) -> List[Dict]:
        """
        Generate trading signals from news sentiment.
        
        Args:
            sentiment_data: Dict of {code: sentiment_info}
            current_prices: Dict of {code: price}
            
        Returns:
            List of trading signals
        """
        signals = []
        
        for code, data in sentiment_data.items():
            avg_sentiment = data['avg_sentiment']
            news_count = data['news_count']
            
            # Strong positive sentiment
            if avg_sentiment > self.sentiment_threshold and news_count >= 2:
                signals.append({
                    'code': code,
                    'action': 'BUY',
                    'reason': f'正面新闻 (情绪: {avg_sentiment:.2f}, 新闻: {news_count}条)',
                    'strength': min(avg_sentiment, 1.0),
                    'price': current_prices.get(code, 0)
                })
                
            # Strong negative sentiment
            elif avg_sentiment < -self.sentiment_threshold and news_count >= 2:
                signals.append({
                    'code': code,
                    'action': 'SELL',
                    'reason': f'负面新闻 (情绪: {avg_sentiment:.2f}, 新闻: {news_count}条)',
                    'strength': min(abs(avg_sentiment), 1.0),
                    'price': current_prices.get(code, 0)
                })
                
        return sorted(signals, key=lambda x: x['strength'], reverse=True)
        
    def generate_report(self, sentiment_data: Dict, signals: List[Dict]) -> str:
        """Generate news trading report."""
        lines = []
        lines.append("=" * 60)
        lines.append("📰 新闻交易策略报告")
        lines.append("=" * 60)
        
        lines.append(f"\n📊 新闻情绪分析")
        for code, data in sentiment_data.items():
            icon = "🔺" if data['avg_sentiment'] > 0 else "🔻"
            lines.append(f"  {icon} {code}: {data['avg_sentiment']:+.3f} ({data['news_count']} 条)")
            
        if signals:
            lines.append(f"\n📈 交易信号 ({len(signals)} 个)")
            for signal in signals[:10]:
                icon = "🔺" if signal['action'] == 'BUY' else "🔻"
                lines.append(f"  {icon} {signal['code']}: {signal['action']} - {signal['reason']}")
                
        return "\n".join(lines)
