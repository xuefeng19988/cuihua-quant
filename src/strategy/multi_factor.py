"""
Multi-Factor Strategy
Combines multiple alpha factors into a unified trading signal.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime

from src.strategy.base import BaseStrategy, Signal

class MultiFactorStrategy(BaseStrategy):
    """
    Multi-Factor Strategy combining:
    1. Momentum (RSI, Rate of Change)
    2. Value (PE Ratio, PB Ratio)
    3. Technical (MACD, MA Trend)
    4. Volatility (Bollinger Bands, ATR)
    """
    
    def __init__(self, params: Dict = None):
        super().__init__("MultiFactor", params)
        
        # Factor weights
        self.weights = self.params.get('weights', {
            'momentum': 0.30,
            'value': 0.20,
            'technical': 0.30,
            'volatility': 0.20
        })
        
        # Thresholds
        self.buy_threshold = self.params.get('buy_threshold', 0.5)
        self.sell_threshold = self.params.get('sell_threshold', -0.3)
        
    def calculate_momentum_score(self, df: pd.DataFrame) -> float:
        """
        Momentum factor: RSI + Rate of Change (5-day, 20-day)
        Returns normalized score [-1, 1]
        """
        score = 0.0
        
        # RSI component
        rsi = df['rsi'].iloc[-1]
        if rsi < 30:
            score += 1.0  # Oversold - bullish reversal potential
        elif rsi > 70:
            score -= 1.0  # Overbought - bearish reversal potential
        else:
            score += (50 - rsi) / 50.0  # Linear scale around 50
            
        # Rate of Change (5-day)
        if len(df) >= 5:
            roc_5 = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5]
            score += np.clip(roc_5 * 5, -0.5, 0.5)  # Normalize
            
        # Rate of Change (20-day)
        if len(df) >= 20:
            roc_20 = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]
            score += np.clip(roc_20 * 3, -0.5, 0.5)
            
        return np.clip(score, -1.0, 1.0)
        
    def calculate_value_score(self, df: pd.DataFrame) -> float:
        """
        Value factor: PE Ratio, PB Ratio (if available)
        Lower PE = Better value (for stable companies)
        """
        score = 0.0
        
        pe = df.get('pe_ratio')
        if pe is not None and not pd.isna(pe.iloc[-1]):
            pe_val = pe.iloc[-1]
            if 0 < pe_val < 15:
                score = 0.8  # Undervalued
            elif 15 <= pe_val < 25:
                score = 0.3  # Fair value
            elif 25 <= pe_val < 40:
                score = -0.2  # Slightly overvalued
            else:
                score = -0.5  # Overvalued
                
        return np.clip(score, -1.0, 1.0)
        
    def calculate_technical_score(self, df: pd.DataFrame) -> float:
        """
        Technical factor: MACD, MA alignment, Volume trend
        """
        score = 0.0
        
        # MACD component
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            macd = df['macd'].iloc[-1]
            macd_sig = df['macd_signal'].iloc[-1]
            
            if macd > macd_sig:
                score += 0.5  # Bullish MACD
            else:
                score -= 0.5  # Bearish MACD
                
            # MACD histogram trend
            if len(df) >= 2:
                hist_now = macd - macd_sig
                hist_prev = df['macd'].iloc[-2] - df['macd_signal'].iloc[-2]
                if hist_now > hist_prev:
                    score += 0.3  # Improving momentum
                else:
                    score -= 0.3
                    
        # MA Trend component
        if 'ma5' in df.columns and 'ma20' in df.columns:
            ma5 = df['ma5'].iloc[-1]
            ma20 = df['ma20'].iloc[-1]
            close = df['close'].iloc[-1]
            
            if close > ma5 > ma20:
                score += 0.5  # Strong uptrend
            elif close < ma5 < ma20:
                score -= 0.5  # Strong downtrend
            elif ma5 > ma20:
                score += 0.2  # Mild bullish
                
        return np.clip(score, -1.0, 1.0)
        
    def calculate_volatility_score(self, df: pd.DataFrame) -> float:
        """
        Volatility factor: Bollinger Bands position, ATR
        """
        score = 0.0
        
        # Bollinger Bands position
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            close = df['close'].iloc[-1]
            bb_upper = df['bb_upper'].iloc[-1]
            bb_lower = df['bb_lower'].iloc[-1]
            bb_mid = (bb_upper + bb_lower) / 2.0
            
            bb_range = bb_upper - bb_lower
            if bb_range > 0:
                # Position in BB range (0 = lower band, 1 = upper band)
                bb_position = (close - bb_lower) / bb_range
                
                if bb_position < 0.2:
                    score = 0.7  # Near lower band - potential bounce
                elif bb_position > 0.8:
                    score = -0.7  # Near upper band - potential pullback
                else:
                    score = (0.5 - bb_position)  # Linear scale
                    
        return np.clip(score, -1.0, 1.0)
        
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """
        Generate trading signals for all stocks in data.
        
        Args:
            data: Dict mapping stock code to OHLCV DataFrame with indicators
            
        Returns:
            List of Signal objects
        """
        signals = []
        
        for code, df in data.items():
            if df.empty or len(df) < 20:
                continue  # Need at least 20 days for indicators
                
            try:
                # Calculate factor scores
                momentum = self.calculate_momentum_score(df)
                value = self.calculate_value_score(df)
                technical = self.calculate_technical_score(df)
                volatility = self.calculate_volatility_score(df)
                
                # Weighted combination
                total_score = (
                    momentum * self.weights['momentum'] +
                    value * self.weights['value'] +
                    technical * self.weights['technical'] +
                    volatility * self.weights['volatility']
                )
                
                # Determine action
                if total_score >= self.buy_threshold:
                    direction = 'BUY'
                    strength = min(total_score, 1.0)
                elif total_score <= self.sell_threshold:
                    direction = 'SELL'
                    strength = min(abs(total_score), 1.0)
                else:
                    direction = 'HOLD'
                    strength = 0.0
                    
                # Reason
                reasons = []
                if momentum > 0.5: reasons.append('Strong Momentum')
                if technical > 0.5: reasons.append('Bullish Technicals')
                if volatility > 0.5: reasons.append('Oversold (BB)')
                
                signal = Signal(
                    code=code,
                    direction=direction,
                    strength=strength,
                    reason=', '.join(reasons) if reasons else 'Neutral'
                )
                signal.score = total_score
                
                signals.append(signal)
                
            except Exception as e:
                print(f"⚠️ Error analyzing {code}: {e}")
                continue
                
        # Sort by score descending
        signals.sort(key=lambda x: x.score, reverse=True)
        
        return signals
