"""
Phase 49: New Trading Strategies
Advanced strategies: Pairs Trading, Statistical Arbitrage, Volatility Trading, etc.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from scipy import stats
from sklearn.linear_model import LinearRegression

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class PairsTradingStrategy:
    """
    Pairs trading strategy using cointegration.
    """
    
    def __init__(self, lookback: int = 60, entry_threshold: float = 2.0, 
                 exit_threshold: float = 0.5, stop_loss: float = 3.0):
        self.lookback = lookback
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.stop_loss = stop_loss
        
    def test_cointegration(self, series1: pd.Series, series2: pd.Series) -> Dict:
        """
        Test if two series are cointegrated.
        
        Returns:
            Dict with test results
        """
        # Engle-Granger two-step method
        model = LinearRegression().fit(series1.values.reshape(-1, 1), series2.values)
        residuals = series2.values - model.predict(series1.values.reshape(-1, 1))
        
        # ADF test on residuals
        from statsmodels.tsa.stattools import adfuller
        adf_result = adfuller(residuals)
        
        return {
            'cointegrated': adf_result[1] < 0.05,
            'adf_statistic': adf_result[0],
            'p_value': adf_result[1],
            'hedge_ratio': model.coef_[0],
            'intercept': model.intercept_,
            'residuals': pd.Series(residuals, index=series1.index)
        }
        
    def generate_signals(self, price1: pd.Series, price2: pd.Series) -> pd.DataFrame:
        """
        Generate pairs trading signals.
        
        Args:
            price1: Price series of stock 1
            price2: Price series of stock 2
            
        Returns:
            DataFrame with signals
        """
        # Calculate spread
        coint_result = self.test_cointegration(
            price1.iloc[-self.lookback:], 
            price2.iloc[-self.lookback:]
        )
        
        if not coint_result['cointegrated']:
            return pd.DataFrame()
            
        hedge_ratio = coint_result['hedge_ratio']
        spread = price2 - hedge_ratio * price1
        
        # Calculate z-score
        spread_mean = spread.rolling(self.lookback).mean()
        spread_std = spread.rolling(self.lookback).std()
        z_score = (spread - spread_mean) / spread_std
        
        # Generate signals
        signals = pd.DataFrame(index=price1.index)
        signals['spread'] = spread
        signals['z_score'] = z_score
        signals['signal'] = 0
        
        # Entry signals
        signals.loc[z_score > self.entry_threshold, 'signal'] = -1  # Short spread
        signals.loc[z_score < -self.entry_threshold, 'signal'] = 1   # Long spread
        
        # Exit signals
        signals.loc[abs(z_score) < self.exit_threshold, 'signal'] = 0
        
        # Stop loss
        signals.loc[z_score > self.stop_loss, 'signal'] = 0
        signals.loc[z_score < -self.stop_loss, 'signal'] = 0
        
        return signals.dropna()
        
    def generate_report(self, signals: pd.DataFrame) -> str:
        """Generate pairs trading report."""
        if signals.empty:
            return "⚠️ 无配对交易信号"
            
        lines = []
        lines.append("=" * 60)
        lines.append("📊 配对交易策略报告")
        lines.append("=" * 60)
        
        long_signals = signals[signals['signal'] == 1]
        short_signals = signals[signals['signal'] == -1]
        
        lines.append(f"\n📈 信号统计")
        lines.append(f"  做多信号: {len(long_signals)} 次")
        lines.append(f"  做空信号: {len(short_signals)} 次")
        lines.append(f"  当前 Z-Score: {signals['z_score'].iloc[-1]:.2f}")
        lines.append(f"  当前信号: {'做多价差' if signals['signal'].iloc[-1] == 1 else '做空价差' if signals['signal'].iloc[-1] == -1 else '无信号'}")
        
        return "\n".join(lines)


class VolatilityTradingStrategy:
    """
    Volatility-based trading strategy.
    """
    
    def __init__(self, vol_lookback: int = 20, vol_threshold_low: float = 0.15,
                 vol_threshold_high: float = 0.35, mean_reversion_window: int = 10):
        self.vol_lookback = vol_lookback
        self.vol_threshold_low = vol_threshold_low
        self.vol_threshold_high = vol_threshold_high
        self.mean_reversion_window = mean_reversion_window
        
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate volatility-based signals.
        
        Low vol → breakout expected → enter position
        High vol → mean reversion expected → exit/contrarian
        """
        signals = pd.DataFrame(index=df.index)
        
        # Calculate volatility
        returns = df['close'].pct_change()
        volatility = returns.rolling(self.vol_lookback).std() * np.sqrt(252)
        signals['volatility'] = volatility
        
        # Volatility regime
        signals['vol_regime'] = 'normal'
        signals.loc[volatility < self.vol_threshold_low, 'vol_regime'] = 'low'
        signals.loc[volatility > self.vol_threshold_high, 'vol_regime'] = 'high'
        
        # Mean reversion signal (for high vol)
        ma = df['close'].rolling(self.mean_reversion_window).mean()
        deviation = (df['close'] - ma) / ma
        
        # Generate trading signals
        signals['signal'] = 0
        
        # Low volatility → expect breakout → enter
        signals.loc[signals['vol_regime'] == 'low', 'signal'] = 1
        
        # High volatility + overbought → mean reversion → exit/short
        high_vol_overbought = (signals['vol_regime'] == 'high') & (deviation > 0.03)
        signals.loc[high_vol_overbought, 'signal'] = -1
        
        return signals.dropna()


class StatisticalArbitrageStrategy:
    """
    Statistical arbitrage using PCA and residual trading.
    """
    
    def __init__(self, n_components: int = 3, lookback: int = 60,
                 entry_z: float = 1.5, exit_z: float = 0.3):
        self.n_components = n_components
        self.lookback = lookback
        self.entry_z = entry_z
        self.exit_z = exit_z
        
    def calculate_residual(self, returns_matrix: pd.DataFrame, 
                          target_col: int = 0) -> pd.Series:
        """
        Calculate residual returns using PCA.
        """
        from sklearn.decomposition import PCA
        
        # Fit PCA on rolling window
        residuals = []
        for i in range(self.lookback, len(returns_matrix)):
            window = returns_matrix.iloc[i-self.lookback:i]
            pca = PCA(n_components=self.n_components)
            pca.fit(window)
            
            # Reconstruct using components
            reconstructed = pca.inverse_transform(pca.transform(window.iloc[[-1]]))
            residual = returns_matrix.iloc[i, target_col] - reconstructed[0, target_col]
            residuals.append(residual)
            
        return pd.Series(residuals, index=returns_matrix.index[self.lookback:])
        
    def generate_signals(self, returns_matrix: pd.DataFrame) -> pd.Series:
        """Generate stat arb signals."""
        residuals = self.calculate_residual(returns_matrix)
        
        # Calculate z-score of residuals
        z_score = (residuals - residuals.rolling(self.lookback).mean()) / \
                  residuals.rolling(self.lookback).std()
                  
        signals = pd.Series(0, index=z_score.index)
        signals.loc[z_score > self.entry_z] = -1
        signals.loc[z_score < -self.entry_z] = 1
        signals.loc[abs(z_score) < self.exit_z] = 0
        
        return signals


class SectorRotationStrategy:
    """
    Sector rotation strategy based on momentum and valuation.
    """
    
    def __init__(self, momentum_window: int = 60, holding_period: int = 20,
                 top_n_sectors: int = 3):
        self.momentum_window = momentum_window
        self.holding_period = holding_period
        self.top_n_sectors = top_n_sectors
        
    def rank_sectors(self, sector_data: Dict[str, pd.DataFrame]) -> List[str]:
        """
        Rank sectors by momentum and other factors.
        
        Args:
            sector_data: Dict of {sector_name: DataFrame with OHLCV}
            
        Returns:
            List of ranked sector names
        """
        sector_scores = {}
        
        for sector_name, df in sector_data.items():
            if len(df) < self.momentum_window:
                continue
                
            # Momentum score
            momentum = (df['close'].iloc[-1] / df['close'].iloc[-self.momentum_window]) - 1
            
            # Volatility adjustment
            volatility = df['close'].pct_change().rolling(self.momentum_window).std()
            
            # Risk-adjusted momentum
            score = momentum / volatility.iloc[-1] if volatility.iloc[-1] > 0 else momentum
            
            sector_scores[sector_name] = score
            
        # Rank sectors
        ranked = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
        return [name for name, score in ranked[:self.top_n_sectors]]


if __name__ == "__main__":
    # Test pairs trading
    np.random.seed(42)
    dates = pd.bdate_range('2024-01-01', periods=200)
    
    # Generate correlated prices
    price1 = pd.Series(np.cumsum(np.random.normal(0, 0.02, 200)) + 100, index=dates)
    price2 = price1 * 1.2 + pd.Series(np.random.normal(0, 1, 200), index=dates)
    
    strategy = PairsTradingStrategy()
    coint_result = strategy.test_cointegration(price1, price2)
    print(f"Cointegrated: {coint_result['cointegrated']}")
    print(f"ADF p-value: {coint_result['p_value']:.4f}")
    print(f"Hedge ratio: {coint_result['hedge_ratio']:.4f}")
    
    signals = strategy.generate_signals(price1, price2)
    if not signals.empty:
        print(strategy.generate_report(signals))
