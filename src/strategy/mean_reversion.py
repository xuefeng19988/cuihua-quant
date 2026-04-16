"""
Mean Reversion Strategy
Buys oversold stocks, sells overbought stocks.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from src.strategy.base import BaseStrategy, Signal

class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy based on:
    - RSI oversold/overbought levels
    - Bollinger Band breakouts
    - Distance from Moving Average
    """
    
    def __init__(self, params: Dict = None):
        super().__init__("MeanReversion", params)
        
        # Parameters
        self.rsi_oversold = self.params.get('rsi_oversold', 30)
        self.rsi_overbought = self.params.get('rsi_overbought', 70)
        self.bb_deviation = self.params.get('bb_deviation', 2.0)  # Standard deviations
        self.ma_period = self.params.get('ma_period', 20)
        self.ma_threshold = self.params.get('ma_threshold', 0.05)  # 5% from MA
        
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """Generate mean reversion signals."""
        signals = []
        
        for code, df in data.items():
            if df.empty or len(df) < self.ma_period + 5:
                continue
                
            try:
                close = df['close'].iloc[-1]
                signal_score = 0.0
                reasons = []
                
                # 1. RSI Signal
                if 'rsi' in df.columns:
                    rsi = df['rsi'].iloc[-1]
                    if rsi < self.rsi_oversold:
                        # Oversold - potential bounce
                        signal_score += 0.5
                        reasons.append(f"RSI Oversold ({rsi:.1f})")
                    elif rsi > self.rsi_overbought:
                        # Overbought - potential pullback
                        signal_score -= 0.5
                        reasons.append(f"RSI Overbought ({rsi:.1f})")
                        
                # 2. Bollinger Band Signal
                if 'bb_lower' in df.columns and 'bb_upper' in df.columns:
                    bb_lower = df['bb_lower'].iloc[-1]
                    bb_upper = df['bb_upper'].iloc[-1]
                    
                    if close < bb_lower:
                        # Below lower band - oversold
                        signal_score += 0.5
                        reasons.append("BB Lower Breakout")
                    elif close > bb_upper:
                        # Above upper band - overbought
                        signal_score -= 0.5
                        reasons.append("BB Upper Breakout")
                        
                # 3. Distance from MA
                ma = df['close'].rolling(self.ma_period).mean().iloc[-1]
                ma_dist = (close - ma) / ma
                
                if ma_dist < -self.ma_threshold:
                    # Significantly below MA - potential bounce
                    signal_score += 0.3
                    reasons.append(f"Below MA ({ma_dist:.1%})")
                elif ma_dist > self.ma_threshold:
                    # Significantly above MA - potential pullback
                    signal_score -= 0.3
                    reasons.append(f"Above MA ({ma_dist:.1%})")
                    
                # Determine action
                if signal_score > 0.3:
                    direction = 'BUY'
                    strength = min(signal_score, 1.0)
                elif signal_score < -0.3:
                    direction = 'SELL'
                    strength = min(abs(signal_score), 1.0)
                else:
                    direction = 'HOLD'
                    strength = 0.0
                    
                signal = Signal(
                    code=code,
                    direction=direction,
                    strength=strength,
                    reason=', '.join(reasons) if reasons else 'Neutral'
                )
                signal.score = signal_score
                signals.append(signal)
                
            except Exception as e:
                print(f"⚠️ Error analyzing {code}: {e}")
                continue
                
        # Sort by score descending
        signals.sort(key=lambda x: x.score, reverse=True)
        return signals
