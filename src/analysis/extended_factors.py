"""
Phase 64: Extended Alpha Factors
Advanced factors: Price Action, Market Microstructure, Behavioral Finance
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class ExtendedAlphaFactors:
    """
    Extended alpha factor library with advanced factors.
    """
    
    @staticmethod
    def price_action_factor(df: pd.DataFrame) -> pd.Series:
        """
        Price action factor: Candlestick patterns and price structure.
        """
        # Candle body size
        body = abs(df['close'] - df['open'])
        # Candle range
        candle_range = df['high'] - df['low']
        # Body to range ratio
        body_ratio = body / (candle_range + 1e-10)
        
        # Upper/lower shadow
        upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
        lower_shadow = df[['open', 'close']].min(axis=1) - df['low']
        
        # Price structure: Higher highs, higher lows
        hh = df['high'].rolling(20).max()
        ll = df['low'].rolling(20).min()
        structure = (df['close'] - ll) / (hh - ll + 1e-10)
        
        # Combine
        factor = 0.3 * body_ratio + 0.4 * structure + 0.3 * (lower_shadow - upper_shadow) / (candle_range + 1e-10)
        
        return factor
        
    @staticmethod
    def order_flow_imbalance(df: pd.DataFrame) -> pd.Series:
        """
        Order flow imbalance factor (proxy using price/volume relationship).
        """
        # Price change per unit volume
        returns = df['close'].pct_change()
        volume = df['volume']
        
        # Volume-weighted price impact
        vwp = (returns * volume).rolling(10).sum() / volume.rolling(10).sum()
        
        # Order flow imbalance
        ofi = np.sign(returns) * volume
        ofi_ma = ofi.rolling(20).mean()
        ofi_std = ofi.rolling(20).std()
        ofi_z = (ofi_ma - ofi_ma.shift(1)) / (ofi_std + 1e-10)
        
        return ofi_z
        
    @staticmethod
    def herding_behavior(df: pd.DataFrame) -> pd.Series:
        """
        Herding behavior factor: Cross-sectional dispersion proxy.
        """
        # Using intraday volatility vs interday volatility ratio
        intraday_vol = (df['high'] - df['low']) / df['close']
        interday_vol = df['close'].pct_change().abs()
        
        # Herding: Low intraday, high interday
        ratio = intraday_vol / (interday_vol + 1e-10)
        herding = 1 / (1 + ratio.rolling(20).mean())
        
        return herding
        
    @staticmethod
    def attention_factor(df: pd.DataFrame) -> pd.Series:
        """
        Investor attention factor: Volume and volatility spikes.
        """
        # Volume abnormality
        vol_ma = df['volume'].rolling(20).mean()
        vol_abnormal = df['volume'] / vol_ma
        
        # Volatility spike
        vol_5 = df['close'].pct_change().rolling(5).std()
        vol_20 = df['close'].pct_change().rolling(20).std()
        vol_spike = vol_5 / (vol_20 + 1e-10)
        
        # Attention = high volume + high volatility
        attention = 0.5 * vol_abnormal + 0.5 * vol_spike
        
        return attention
        
    @staticmethod
    def trend_strength_factor(df: pd.DataFrame) -> pd.Series:
        """
        Trend strength factor using ADX proxy.
        """
        # Directional movement
        high_diff = df['high'].diff()
        low_diff = -df['low'].diff()
        
        plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0)
        minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0)
        
        # Smoothed averages
        atr = (df['high'] - df['low']).rolling(14).mean()
        plus_di = pd.Series(plus_dm, index=df.index).rolling(14).mean() / (atr + 1e-10)
        minus_di = pd.Series(minus_dm, index=df.index).rolling(14).mean() / (atr + 1e-10)
        
        # ADX proxy
        dx = abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
        adx = dx.rolling(14).mean()
        
        return adx
        
    @staticmethod
    def market_timing_factor(df: pd.DataFrame) -> pd.Series:
        """
        Market timing factor using moving average convergence.
        """
        # Multiple MA alignment
        ma_5 = df['close'].rolling(5).mean()
        ma_10 = df['close'].rolling(10).mean()
        ma_20 = df['close'].rolling(20).mean()
        ma_60 = df['close'].rolling(60).mean()
        
        # Alignment score
        alignment = 0
        alignment += (ma_5 > ma_10).astype(int)
        alignment += (ma_10 > ma_20).astype(int)
        alignment += (ma_20 > ma_60).astype(int)
        
        # Normalize
        timing = alignment / 3.0
        
        return timing
        
    @staticmethod
    def reversal_potential(df: pd.DataFrame) -> pd.Series:
        """
        Reversal potential factor: Overbought/oversold conditions.
        """
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        # Distance from MA
        ma_20 = df['close'].rolling(20).mean()
        distance = (df['close'] - ma_20) / ma_20
        
        # Reversal potential (high when extreme)
        reversal = np.where(rsi > 70, -1, np.where(rsi < 30, 1, 0))
        reversal += np.where(distance > 0.1, -1, np.where(distance < -0.1, 1, 0))
        
        return pd.Series(reversal, index=df.index)
        
    @staticmethod
    def composite_advanced(df: pd.DataFrame, weights: Dict = None) -> pd.Series:
        """
        Composite advanced factor combining multiple factors.
        """
        if weights is None:
            weights = {
                'price_action': 0.15,
                'order_flow': 0.20,
                'trend_strength': 0.20,
                'market_timing': 0.15,
                'reversal': 0.15,
                'attention': 0.15
            }
            
        factors = {
            'price_action': ExtendedAlphaFactors.price_action_factor(df),
            'order_flow': ExtendedAlphaFactors.order_flow_imbalance(df),
            'trend_strength': ExtendedAlphaFactors.trend_strength_factor(df),
            'market_timing': ExtendedAlphaFactors.market_timing_factor(df),
            'reversal': ExtendedAlphaFactors.reversal_potential(df),
            'attention': ExtendedAlphaFactors.attention_factor(df)
        }
        
        composite = pd.Series(0, index=df.index)
        for name, weight in weights.items():
            if name in factors:
                composite += weight * factors[name]
                
        return composite
        
    @staticmethod
    def generate_factor_report(df: pd.DataFrame) -> str:
        """Generate comprehensive factor report."""
        factors = {
            'price_action': ExtendedAlphaFactors.price_action_factor(df),
            'order_flow': ExtendedAlphaFactors.order_flow_imbalance(df),
            'herding': ExtendedAlphaFactors.herding_behavior(df),
            'attention': ExtendedAlphaFactors.attention_factor(df),
            'trend_strength': ExtendedAlphaFactors.trend_strength_factor(df),
            'market_timing': ExtendedAlphaFactors.market_timing_factor(df),
            'reversal': ExtendedAlphaFactors.reversal_potential(df),
            'composite': ExtendedAlphaFactors.composite_advanced(df)
        }
        
        lines = []
        lines.append("=" * 60)
        lines.append("📊 扩展 Alpha 因子报告")
        lines.append("=" * 60)
        
        for name, values in factors.items():
            lines.append(f"\n🔬 {name} 因子")
            lines.append(f"  当前值: {values.iloc[-1]:.4f}")
            lines.append(f"  均值: {values.mean():.4f}")
            lines.append(f"  标准差: {values.std():.4f}")
            lines.append(f"  分位数: 25%={values.quantile(0.25):.4f}, 75%={values.quantile(0.75):.4f}")
            
        return "\n".join(lines)


if __name__ == "__main__":
    # Test extended factors
    np.random.seed(42)
    dates = pd.bdate_range('2024-01-01', periods=200)
    df = pd.DataFrame({
        'date': dates,
        'open': np.random.uniform(100, 110, 200),
        'high': np.random.uniform(110, 120, 200),
        'low': np.random.uniform(90, 100, 200),
        'close': np.cumprod(1 + np.random.normal(0.0005, 0.015, 200)) * 100,
        'volume': np.random.uniform(1e6, 1e8, 200)
    })
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    
    print(ExtendedAlphaFactors.generate_factor_report(df))
