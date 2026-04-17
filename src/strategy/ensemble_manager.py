"""
Phase 46: Strategy Ensemble Manager
Combine multiple strategies with dynamic weighting.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class StrategyEnsembleManager:
    """
    Strategy ensemble with dynamic weighting based on performance.
    """
    
    def __init__(self, strategies: List[str] = None, rebalance_period: int = 20):
        self.strategies = strategies or []
        self.rebalance_period = rebalance_period
        self.weights: Dict[str, float] = {}
        self.performance_history: Dict[str, List[float]] = {s: [] for s in self.strategies}
        self._initialize_weights()
        
    def _initialize_weights(self):
        """Initialize equal weights."""
        if self.strategies:
            weight = 1.0 / len(self.strategies)
            self.weights = {s: weight for s in self.strategies}
            
    def add_strategy(self, name: str):
        """Add a strategy to ensemble."""
        if name not in self.strategies:
            self.strategies.append(name)
            self.performance_history[name] = []
            self._initialize_weights()
            
    def update_performance(self, strategy: str, return_value: float):
        """Update strategy performance history."""
        if strategy in self.performance_history:
            self.performance_history[strategy].append(return_value)
            
    def calculate_dynamic_weights(self, method: str = 'performance') -> Dict[str, float]:
        """
        Calculate dynamic weights based on recent performance.
        
        Args:
            method: 'performance', 'risk_adjusted', or 'equal'
            
        Returns:
            Dict of {strategy: weight}
        """
        if method == 'equal':
            weight = 1.0 / len(self.strategies)
            return {s: weight for s in self.strategies}
            
        scores = {}
        for strategy in self.strategies:
            returns = self.performance_history.get(strategy, [])
            if not returns or len(returns) < self.rebalance_period:
                scores[strategy] = 0
                continue
                
            recent_returns = returns[-self.rebalance_period:]
            
            if method == 'performance':
                scores[strategy] = np.mean(recent_returns)
            elif method == 'risk_adjusted':
                mean_ret = np.mean(recent_returns)
                std_ret = np.std(recent_returns)
                scores[strategy] = mean_ret / std_ret if std_ret > 0 else 0
                
        # Normalize weights
        total_score = sum(max(s, 0) for s in scores.values())
        if total_score > 0:
            self.weights = {s: max(score, 0) / total_score for s, score in scores.items()}
        else:
            self._initialize_weights()
            
        return self.weights
        
    def ensemble_prediction(self, predictions: Dict[str, float]) -> float:
        """
        Combine strategy predictions using weights.
        
        Args:
            predictions: Dict of {strategy: prediction}
            
        Returns:
            Ensemble prediction
        """
        ensemble = 0.0
        for strategy, pred in predictions.items():
            if strategy in self.weights:
                ensemble += self.weights[strategy] * pred
                
        return ensemble
        
    def generate_report(self) -> str:
        """Generate ensemble report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🎯 策略组合报告")
        lines.append("=" * 60)
        
        lines.append(f"\n📊 当前权重")
        for strategy, weight in sorted(self.weights.items(), key=lambda x: x[1], reverse=True):
            returns = self.performance_history.get(strategy, [])
            avg_ret = np.mean(returns) if returns else 0
            lines.append(f"  {strategy}: {weight:.1%} (平均收益: {avg_ret:+.4f})")
            
        lines.append(f"\n📈 策略表现")
        for strategy in self.strategies:
            returns = self.performance_history.get(strategy, [])
            if returns:
                total = np.prod(1 + pd.Series(returns)) - 1
                lines.append(f"  {strategy}: {len(returns)} 期 | 累计: {total:+.2%}")
                
        return "\n".join(lines)


if __name__ == "__main__":
    # Test ensemble
    ensemble = StrategyEnsembleManager(['momentum', 'mean_reversion', 'trend'])
    
    # Simulate performance
    np.random.seed(42)
    for i in range(50):
        for strategy in ensemble.strategies:
            if strategy == 'momentum':
                ret = np.random.normal(0.001, 0.02)
            elif strategy == 'mean_reversion':
                ret = np.random.normal(0.0005, 0.015)
            else:
                ret = np.random.normal(0.0008, 0.018)
            ensemble.update_performance(strategy, ret)
            
        if i % 20 == 0:
            ensemble.calculate_dynamic_weights('risk_adjusted')
            
    print(ensemble.generate_report())
