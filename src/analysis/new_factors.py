"""
Phase 50: New Alpha Factors
Advanced alpha factors: Quality, Value, Growth, Sentiment, Microstructure.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class AlphaFactors:
    """
    Extended alpha factor library.
    """
    
    @staticmethod
    def quality_factor(df: pd.DataFrame) -> pd.Series:
        """
        Quality factor: ROE stability + profitability + leverage.
        Higher is better.
        """
        # Proxy using price-based metrics
        # ROE proxy: consistent upward price movement
        returns = df['close'].pct_change()
        
        # Profitability proxy: positive return ratio
        profit_ratio = (returns > 0).rolling(60).mean()
        
        # Stability proxy: low volatility
        vol = returns.rolling(60).std()
        stability = 1 / (1 + vol)
        
        # Combine
        quality = 0.5 * profit_ratio + 0.5 * stability
        
        return quality
        
    @staticmethod
    def value_factor(df: pd.DataFrame) -> pd.Series:
        """
        Value factor: Price below moving average + low momentum.
        Lower price relative to history = more value.
        """
        # Mean reversion potential
        ma_200 = df['close'].rolling(200).mean()
        ma_50 = df['close'].rolling(50).mean()
        
        # Distance from long-term MA (negative = undervalued)
        distance_from_ma = (df['close'] - ma_200) / ma_200
        
        # Short-term momentum (negative momentum = potential value)
        momentum_50 = df['close'].pct_change(50)
        
        # Value score (lower is more undervalued)
        value = -0.6 * distance_from_ma - 0.4 * momentum_50
        
        return value
        
    @staticmethod
    def growth_factor(df: pd.DataFrame) -> pd.Series:
        """
        Growth factor: Accelerating returns + volume growth.
        """
        # Return acceleration
        mom_20 = df['close'].pct_change(20)
        mom_60 = df['close'].pct_change(60)
        acceleration = mom_20 - mom_60.shift(20)
        
        # Volume growth
        vol_20 = df['volume'].rolling(20).mean()
        vol_60 = df['volume'].rolling(60).mean()
        volume_growth = vol_20 / vol_60
        
        # Combine
        growth = 0.6 * acceleration + 0.4 * volume_growth
        
        return growth
        
    @staticmethod
    def sentiment_factor(news_scores: pd.Series) -> pd.Series:
        """
        Sentiment factor from news/social media.
        """
        # Exponential weighted sentiment
        ew_sentiment = news_scores.ewm(span=10).mean()
        
        # Sentiment momentum
        sent_momentum = ew_sentiment - ew_sentiment.shift(5)
        
        # Combine
        sentiment = 0.7 * ew_sentiment + 0.3 * sent_momentum
        
        return sentiment
        
    @staticmethod
    def microstructure_factor(df: pd.DataFrame) -> pd.Series:
        """
        Microstructure factor: Volume-price relationship.
        """
        # Volume-price correlation
        returns = df['close'].pct_change()
        volume_change = df['volume'].pct_change()
        
        rolling_corr = returns.rolling(20).corr(volume_change)
        
        # Price impact per unit volume
        price_impact = returns / (df['volume'] / df['volume'].rolling(20).mean() + 1e-10)
        price_impact_ma = price_impact.rolling(20).mean()
        
        # Combine
        micro = 0.5 * rolling_corr + 0.5 * price_impact_ma
        
        return micro
        
    @staticmethod
    def liquidity_factor(df: pd.DataFrame) -> pd.Series:
        """
        Liquidity factor: Amihud illiquidity measure.
        Lower illiquidity = better liquidity = lower expected return.
        """
        returns = df['close'].pct_change().abs()
        volume = df['volume']
        
        # Amihud illiquidity
        amihud = returns / (volume + 1e-10)
        amihud_ma = amihud.rolling(20).mean()
        
        # Invert: higher liquidity score = better
        liquidity = 1 / (1 + amihud_ma)
        
        return liquidity
        
    @staticmethod
    def momentum_reversal_factor(df: pd.DataFrame, 
                                 short_window: int = 5,
                                 long_window: int = 60) -> pd.Series:
        """
        Combined momentum and reversal factor.
        Short-term reversal + long-term momentum.
        """
        # Short-term reversal (negative)
        short_mom = df['close'].pct_change(short_window)
        
        # Long-term momentum (positive)
        long_mom = df['close'].pct_change(long_window)
        
        # Combine (negative short + positive long)
        combined = -0.3 * short_mom + 0.7 * long_mom
        
        return combined
        
    @staticmethod
    def volatility_risk_premium(df: pd.DataFrame) -> pd.Series:
        """
        Volatility risk premium factor.
        Realized vol vs implied vol proxy.
        """
        # Realized volatility
        realized_vol = df['close'].pct_change().rolling(20).std() * np.sqrt(252)
        
        # Volatility of volatility (uncertainty)
        vol_of_vol = realized_vol.rolling(40).std()
        
        # Volatility risk premium (high vol of vol = high premium expected)
        vrp = vol_of_vol
        
        return vrp
        
    @staticmethod
    def composite_alpha(df: pd.DataFrame, weights: Dict[str, float] = None) -> pd.Series:
        """
        Composite alpha factor combining multiple factors.
        """
        if weights is None:
            weights = {
                'quality': 0.20,
                'value': 0.15,
                'growth': 0.20,
                'momentum_reversal': 0.20,
                'microstructure': 0.10,
                'liquidity': 0.15
            }
            
        factors = {
            'quality': AlphaFactors.quality_factor(df),
            'value': AlphaFactors.value_factor(df),
            'growth': AlphaFactors.growth_factor(df),
            'momentum_reversal': AlphaFactors.momentum_reversal_factor(df),
            'microstructure': AlphaFactors.microstructure_factor(df),
            'liquidity': AlphaFactors.liquidity_factor(df)
        }
        
        composite = pd.Series(0, index=df.index)
        for name, weight in weights.items():
            if name in factors:
                composite += weight * factors[name]
                
        return composite
        
    @staticmethod
    def generate_factor_report(df: pd.DataFrame, factor_name: str = 'composite') -> str:
        """Generate factor analysis report."""
        factors = {
            'quality': AlphaFactors.quality_factor(df),
            'value': AlphaFactors.value_factor(df),
            'growth': AlphaFactors.growth_factor(df),
            'momentum_reversal': AlphaFactors.momentum_reversal_factor(df),
            'microstructure': AlphaFactors.microstructure_factor(df),
            'liquidity': AlphaFactors.liquidity_factor(df),
            'composite': AlphaFactors.composite_alpha(df)
        }
        
        lines = []
        lines.append("=" * 60)
        lines.append("📊 Alpha 因子报告")
        lines.append("=" * 60)
        
        for name, factor_values in factors.items():
            lines.append(f"\n🔬 {name} 因子")
            lines.append(f"  当前值: {factor_values.iloc[-1]:.4f}")
            lines.append(f"  均值: {factor_values.mean():.4f}")
            lines.append(f"  标准差: {factor_values.std():.4f}")
            lines.append(f"  最小值: {factor_values.min():.4f}")
            lines.append(f"  最大值: {factor_values.max():.4f}")
            
        return "\n".join(lines)


if __name__ == "__main__":
    # Test factors
    np.random.seed(42)
    dates = pd.bdate_range('2024-01-01', periods=200)
    df = pd.DataFrame({
        'date': dates,
        'close': np.cumprod(1 + np.random.normal(0.0005, 0.015, 200)) * 100,
        'volume': np.random.uniform(1e6, 1e8, 200)
    })
    
    print(AlphaFactors.generate_factor_report(df))
