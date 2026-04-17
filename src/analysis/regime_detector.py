"""
Phase 45: Market Regime Detector
Detect market regimes and adapt strategies accordingly.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class MarketRegimeDetector:
    """
    Detect market regimes using Hidden Markov Models and clustering.
    """
    
    def __init__(self, n_regimes: int = 3):
        self.n_regimes = n_regimes
        self.model = None
        self.scaler = StandardScaler()
        self.regime_labels = {
            0: "熊市",
            1: "震荡市",
            2: "牛市"
        }
        
    def prepare_features(self, returns: pd.Series, volatility: pd.Series = None,
                        volume: pd.Series = None) -> pd.DataFrame:
        """Prepare features for regime detection."""
        features = pd.DataFrame(index=returns.index)
        features['return'] = returns
        features['return_squared'] = returns ** 2
        
        if volatility is not None:
            features['volatility'] = volatility
        else:
            features['volatility'] = returns.rolling(20).std()
            
        if volume is not None:
            features['volume_change'] = volume.pct_change()
            
        features['momentum'] = (1 + returns).rolling(60).apply(np.prod, raw=True) - 1
        
        return features.dropna()
        
    def fit(self, features: pd.DataFrame) -> Dict:
        """
        Fit regime detection model.
        
        Args:
            features: Feature DataFrame
            
        Returns:
            Model results
        """
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Fit Gaussian Mixture Model
        self.model = GaussianMixture(
            n_components=self.n_regimes,
            covariance_type='full',
            random_state=42,
            n_init=10
        )
        
        regime_labels = self.model.fit_predict(scaled_features)
        regime_probabilities = self.model.predict_proba(scaled_features)
        
        # Analyze regimes
        regime_stats = {}
        for i in range(self.n_regimes):
            mask = regime_labels == i
            regime_stats[i] = {
                'label': self.regime_labels.get(i, f" regime_{i}"),
                'frequency': mask.mean(),
                'mean_return': features['return'][mask].mean(),
                'volatility': features['return'][mask].std(),
                'sharpe': features['return'][mask].mean() / features['return'][mask].std() if features['return'][mask].std() > 0 else 0
            }
            
        # Sort regimes by mean return to assign labels
        sorted_regimes = sorted(regime_stats.items(), key=lambda x: x[1]['mean_return'])
        for idx, (regime_id, stats) in enumerate(sorted_regimes):
            stats['label'] = self.regime_labels.get(idx, f" regime_{idx}")
            
        return {
            'regime_labels': regime_labels,
            'regime_probabilities': regime_probabilities,
            'regime_stats': regime_stats,
            'current_regime': regime_labels[-1],
            'current_probabilities': regime_probabilities[-1]
        }
        
    def predict(self, features: pd.DataFrame) -> int:
        """Predict current market regime."""
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
            
        scaled_features = self.scaler.transform(features)
        return self.model.predict(scaled_features)[-1]
        
    def get_regime_strategy(self, regime: int) -> Dict:
        """Get recommended strategy for regime."""
        strategies = {
            0: {  # Bear market
                'allocation': 0.3,
                'stop_loss': 0.05,
                'take_profit': 0.10,
                'position_size': 0.05,
                'description': '防御策略：低仓位，严格止损'
            },
            1: {  # Range-bound
                'allocation': 0.6,
                'stop_loss': 0.08,
                'take_profit': 0.15,
                'position_size': 0.10,
                'description': '中性策略：中等仓位，均值回归'
            },
            2: {  # Bull market
                'allocation': 0.9,
                'stop_loss': 0.10,
                'take_profit': 0.20,
                'position_size': 0.15,
                'description': '进攻策略：高仓位，趋势跟踪'
            }
        }
        
        strategy = strategies.get(regime, strategies[1])
        strategy['regime'] = self.regime_labels.get(regime, 'Unknown')
        
        return strategy
        
    def generate_report(self, results: Dict) -> str:
        """Generate regime detection report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🌍 市场状态检测报告")
        lines.append("=" * 60)
        
        # Current regime
        current = results['current_regime']
        lines.append(f"\n📊 当前市场状态: {self.regime_labels.get(current, 'Unknown')}")
        
        probs = results['current_probabilities']
        for i, prob in enumerate(probs):
            lines.append(f"  {self.regime_labels.get(i, f'Regime {i}')}: {prob:.1%}")
            
        # Regime statistics
        lines.append(f"\n📈 状态统计")
        for regime_id, stats in sorted(results['regime_stats'].items(), 
                                       key=lambda x: x[1]['mean_return']):
            lines.append(f"\n  {stats['label']}:")
            lines.append(f"    频率: {stats['frequency']:.1%}")
            lines.append(f"    平均收益: {stats['mean_return']:.4f}")
            lines.append(f"    波动率: {stats['volatility']:.4f}")
            lines.append(f"    夏普: {stats['sharpe']:.2f}")
            
        # Recommended strategy
        strategy = self.get_regime_strategy(current)
        lines.append(f"\n🎯 推荐策略")
        lines.append(f"  状态: {strategy['regime']}")
        lines.append(f"  仓位: {strategy['allocation']:.0%}")
        lines.append(f"  止损: {strategy['stop_loss']:.0%}")
        lines.append(f"  止盈: {strategy['take_profit']:.0%}")
        lines.append(f"  描述: {strategy['description']}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Test regime detection
    np.random.seed(42)
    days = 500
    
    # Simulate different regimes
    returns = np.zeros(days)
    for i in range(days):
        if i < 150:  # Bull
            returns[i] = np.random.normal(0.001, 0.01)
        elif i < 300:  # Bear
            returns[i] = np.random.normal(-0.001, 0.02)
        else:  # Range
            returns[i] = np.random.normal(0, 0.015)
            
    returns_series = pd.Series(returns)
    
    detector = MarketRegimeDetector(n_regimes=3)
    features = detector.prepare_features(returns_series)
    results = detector.fit(features)
    print(detector.generate_report(results))
