"""
Sentiment Analysis Module
Analyzes news and social media sentiment for stocks.
"""

import os
import re
import yaml
import jieba
import pandas as pd
from datetime import datetime
from collections import Counter
from typing import List, Dict, Tuple

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class StockSentimentAnalyzer:
    """
    Analyzes sentiment of news articles related to specific stocks.
    Uses a dictionary-based approach with keyword matching.
    """
    
    def __init__(self):
        # Sentiment dictionary (Positive/Negative keywords)
        self.positive_words = [
            '上涨', '突破', '利好', '增长', '盈利', '创新高', '涨停', 
            '牛市', '大涨', '飙升', '爆发', '超预期', '强势', '领涨',
            '复苏', '回暖', '利好', '放量', '资金流入', '机构看好',
            '突破', '新高', '盈利', '增长', '改善', '强劲', '乐观'
        ]
        
        self.negative_words = [
            '下跌', '暴跌', '利空', '亏损', '跳水', '跌停', '熊市',
            '大跌', '崩盘', '下滑', '恶化', '疲软', '资金流出',
            '机构看空', '破位', '新低', '亏损', '下滑', '恶化',
            '监管', '处罚', '违规', '诉讼', '退市', '减持', '清仓'
        ]
        
        # Stock name to code mapping (Common names)
        self.stock_keywords = {
            '茅台': 'SH.600519',
            '五粮液': 'SZ.000858',
            '比亚迪': 'SZ.002594',
            '宁德时代': 'SZ.300750',
            '腾讯': 'HK.00700',
            '阿里巴巴': 'HK.09988',
            '美团': 'HK.03690',
            '小米': 'HK.01810',
            '平安': 'SH.601318',
            '招商': 'SH.600036',
            '东方财富': 'SZ.300059',
            '海康威视': 'SZ.002415',
            '格力': 'SZ.000651',
            '美的': 'SZ.000333',
            '中免': 'SH.601888',
            '科大讯飞': 'SZ.002230',
            '隆基': 'SH.601012',
            '亿纬锂能': 'SZ.300014',
            '京东': 'HK.09618',
            '快手': 'HK.01024',
            '百度': 'HK.09888',
            '泡泡玛特': 'HK.09992',
            '名创优品': 'HK.09896',
            '海底捞': 'HK.06862',
        }
        
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text.
        
        Returns:
            Dict with 'score' (-1 to 1), 'label' (positive/negative/neutral), 'details'
        """
        # Tokenize
        words = jieba.lcut(text)
        
        # Count positive/negative words
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        
        # Calculate score
        total = pos_count + neg_count
        if total == 0:
            score = 0.0
            label = 'neutral'
        else:
            score = (pos_count - neg_count) / total
            if score > 0.2:
                label = 'positive'
            elif score < -0.2:
                label = 'negative'
            else:
                label = 'neutral'
                
        return {
            'score': score,
            'label': label,
            'pos_count': pos_count,
            'neg_count': neg_count,
            'total_keywords': total
        }
        
    def analyze_news_for_stocks(self, news_items: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Analyze a list of news items and map sentiment to stocks.
        
        Args:
            news_items: List of dicts with 'title', 'content', 'url'
            
        Returns:
            Dict mapping stock_code to list of sentiment results
        """
        stock_sentiments = {}
        
        for item in news_items:
            title = item.get('title', '')
            content = item.get('content', '')
            full_text = title + ' ' + content
            
            # Find mentioned stocks
            mentioned_stocks = self._find_mentioned_stocks(full_text)
            
            # Analyze sentiment
            sentiment = self.analyze_text(full_text)
            
            # Map to stocks
            for code in mentioned_stocks:
                if code not in stock_sentiments:
                    stock_sentiments[code] = []
                    
                stock_sentiments[code].append({
                    'title': title,
                    'sentiment': sentiment,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
                
        return stock_sentiments
        
    def _find_mentioned_stocks(self, text: str) -> List[str]:
        """Find which stocks are mentioned in text."""
        mentioned = []
        for keyword, code in self.stock_keywords.items():
            if keyword in text:
                mentioned.append(code)
        return mentioned
        
    def get_aggregate_sentiment(self, stock_sentiments: Dict[str, List[Dict]]) -> pd.DataFrame:
        """
        Calculate aggregate sentiment score per stock.
        
        Returns:
            DataFrame with code, avg_score, count, label
        """
        rows = []
        for code, sentiments in stock_sentiments.items():
            scores = [s['sentiment']['score'] for s in sentiments]
            avg_score = sum(scores) / len(scores) if scores else 0.0
            
            if avg_score > 0.2:
                label = 'positive'
            elif avg_score < -0.2:
                label = 'negative'
            else:
                label = 'neutral'
                
            rows.append({
                'code': code,
                'avg_score': avg_score,
                'news_count': len(sentiments),
                'label': label,
                'date': datetime.now().strftime('%Y-%m-%d')
            })
            
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values('avg_score', ascending=False).reset_index(drop=True)
            
        return df
