"""
Momentum Strategy
Captures trends by buying stocks with strong recent performance.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from src.strategy.base import BaseStrategy, Signal

class MomentumStrategy(BaseStrategy):
    """
    Momentum Strategy based on:
    - Price Rate of Change (ROC)
    - Moving Average alignment
    - Volume confirmation
    """
    
    def __init__(self, params: Dict = None):
        super().__init__("Momentum", params)
        
        # Parameters
        self.roc_period = self.params.get('roc_period', 20)  # 20-day ROC
        self.ma_fast = self.params.get('ma_fast', 5)
        self.ma_slow = self.params.get('ma_slow', 20)
        self.min_volume_ratio = self.params.get('min_volume_ratio', 1.2)  # Volume > 20-day avg
        self.momentum_threshold = self.params.get('momentum_threshold', 0.05)  # 5% ROC
        
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """Generate momentum-based signals."""
        signals = []
        
        for code, df in data.items():
            if df.empty or len(df) < self.roc_period:
                continue
                
            try:
                # 1. Calculate Rate of Change (ROC)
                close_now = df['close'].iloc[-1]
                close_prev = df['close'].iloc[-self.roc_period]
                roc = (close_now - close_prev) / close_prev
                
                # 2. Moving Average Alignment
                ma_fast = df['close'].rolling(self.ma_fast).mean().iloc[-1]
                ma_slow = df['close'].rolling(self.ma_slow).mean().iloc[-1]
                ma_bullish = ma_fast > ma_slow
                
                # 3. Volume Confirmation
                vol_now = df['volume'].iloc[-1]
                vol_avg = df['volume'].rolling(20).mean().iloc[-1]
                vol_ratio = vol_now / vol_avg if vol_avg > 0 else 0
                
                # Signal Logic
                if roc > self.momentum_threshold and ma_bullish and vol_ratio > self.min_volume_ratio:
                    # Strong momentum - BUY
                    strength = min(roc / 0.20, 1.0)  # Normalize to 0-1
                    signal = Signal(
                        code=code,
                        direction='BUY',
                        strength=strength,
                        reason=f"Momentum {roc:.1%} | Vol {vol_ratio:.1f}x"
                    )
                    signal.score = strength
                    signals.append(signal)
                    
                elif roc < -self.momentum_threshold:
                    # Negative momentum - SELL/HOLD
                    strength = min(abs(roc) / 0.20, 1.0)
                    signal = Signal(
                        code=code,
                        direction='SELL',
                        strength=strength,
                        reason=f"Negative Momentum {roc:.1%}"
                    )
                    signal.score = -strength
                    signals.append(signal)
                    
            except Exception as e:
                print(f"⚠️ Error analyzing {code}: {e}")
                continue
                
        # Sort by score descending
        signals.sort(key=lambda x: x.score, reverse=True)
        return signals
