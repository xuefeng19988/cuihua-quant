"""
Signal Generation Engine
Combines technical and sentiment signals into a unified trading signal.
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime
from typing import List, Dict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine
from src.analysis.technical import calculate_indicators, analyze_latest
from src.analysis.sentiment import StockSentimentAnalyzer

from src.core.utils import load_stock_names  # 统一入口

class SignalGenerator:
    """
    Generates combined signals from multiple sources:
    1. Technical Analysis (Weight: 60%)
    2. Sentiment Analysis (Weight: 40%)
    """
    
    def __init__(self, config_path=None):
        self.engine = get_db_engine()
        self.sentiment_analyzer = StockSentimentAnalyzer()
        
        # Load weights from config if available
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                cfg = yaml.safe_load(f)
            self.tech_weight = cfg.get('weights', {}).get('technical', 0.6)
            self.sentiment_weight = cfg.get('weights', {}).get('sentiment', 0.4)
        else:
            self.tech_weight = 0.6
            self.sentiment_weight = 0.4
            
    def generate_combined_signal(self, codes: List[str], news_items: List[Dict] = None) -> pd.DataFrame:
        """
        Generate combined signal for a list of stocks.
        
        Args:
            codes: List of stock codes
            news_items: Optional list of news dicts for sentiment analysis
            
        Returns:
            DataFrame with combined scores and rankings
        """
        stock_names = _load_stock_names()
        results = []
        
        # 1. Technical Analysis
        tech_signals = self._analyze_technical(codes)
        
        # 2. Sentiment Analysis (if news provided)
        sentiment_scores = {}
        if news_items:
            stock_sentiments = self.sentiment_analyzer.analyze_news_for_stocks(news_items)
            agg_sentiment = self.sentiment_analyzer.get_aggregate_sentiment(stock_sentiments)
            if not agg_sentiment.empty:
                for _, row in agg_sentiment.iterrows():
                    sentiment_scores[row['code']] = row['avg_score']
        
        # 3. Combine Signals
        for code, tech in tech_signals.items():
            # Normalize technical score to -1 to 1 range
            # Assume max tech score is around 5.0
            tech_normalized = min(max(tech.get('score', 0) / 5.0, -1.0), 1.0)
            
            # Get sentiment score
            sent_score = sentiment_scores.get(code, 0.0)
            
            # Weighted combination
            combined_score = (tech_normalized * self.tech_weight) + (sent_score * self.sentiment_weight)
            
            results.append({
                'code': code,
                'name': stock_names.get(code, ''),
                'close': tech.get('close', 0),
                'tech_score': tech_normalized,
                'sentiment_score': sent_score,
                'combined_score': combined_score,
                'signals': tech.get('signals', []),
                'date': datetime.now().strftime('%Y-%m-%d')
            })
            
        # Convert to DataFrame and rank
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values('combined_score', ascending=False).reset_index(drop=True)
            df['rank'] = df.index + 1
            
        return df
        
    def _analyze_technical(self, codes: List[str]) -> Dict:
        """Run technical analysis on all codes."""
        results = {}
        
        for code in codes:
            query = f"""
                SELECT date, open_price as open, high_price as high, 
                       low_price as low, close_price as close, volume
                FROM stock_daily 
                WHERE code = '{code}' 
                ORDER BY date ASC
            """
            
            try:
                df = pd.read_sql(query, self.engine)
                if df.empty:
                    continue
                    
                df = calculate_indicators(df)
                sig = self._analyze_latest(code, df)
                if sig:
                    results[code] = sig
            except Exception:
                continue
                
        return results
        
    def _analyze_latest(self, code: str, df: pd.DataFrame) -> Dict:
        """Analyze latest row and return signal dict."""
        import numpy as np
        
        if df.empty:
            return None
            
        row = df.iloc[-1]
        prev_row = df.iloc[-2] if len(df) > 1 else row
        
        signal = {
            'code': code,
            'close': row['close'],
            'score': 0.0,
            'signals': []
        }
        
        # RSI Signal
        rsi = row.get('rsi')
        if rsi is not None and not np.isnan(rsi):
            if rsi < 30:
                signal['score'] += 2.0
                signal['signals'].append('RSI_OverSold')
            elif rsi > 70:
                signal['score'] -= 2.0
                signal['signals'].append('RSI_OverBought')
                
        # MACD Cross
        macd = row.get('macd')
        macd_sig = row.get('macd_signal')
        if macd is not None and macd_sig is not None and not np.isnan(macd) and not np.isnan(macd_sig):
            prev_macd = prev_row.get('macd', 0)
            prev_sig = prev_row.get('macd_signal', 0)
            if prev_macd < prev_sig and macd > macd_sig:
                signal['score'] += 3.0
                signal['signals'].append('MACD_GoldenCross')
            elif prev_macd > prev_sig and macd < macd_sig:
                signal['score'] -= 3.0
                signal['signals'].append('MACD_DeathCross')
                
        # MA20 Trend
        ma20 = row.get('ma20')
        if ma20 is not None and not np.isnan(ma20):
            if row['close'] > ma20:
                signal['score'] += 1.0
                signal['signals'].append('Above_MA20')
                
        return signal

    def get_top_picks(self, df: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        """Get top N stock picks based on combined score."""
        if df is None or df.empty:
            return []
            
        top = df.head(top_n)
        picks = []
        for _, row in top.iterrows():
            picks.append({
                'rank': row['rank'],
                'code': row['code'],
                'score': row['combined_score'],
                'close': row['close'],
                'signals': ', '.join(row['signals']) if row['signals'] else 'None'
            })
            
        return picks
