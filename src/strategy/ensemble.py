"""
Ensemble Strategy
Combines multiple strategies with dynamic weighting.
Merged from: ensemble.py, ensemble_manager.py
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

try:
    from src.strategy.base import BaseStrategy, Signal
except ImportError:
    class BaseStrategy:
        def __init__(self, name, params=None): pass
    class Signal:
        def __init__(self, code, direction, strength=0, reason=''):
            self.code, self.direction, self.strength, self.reason = code, direction, strength, reason
            self.score = 0

from src.strategy.momentum import MomentumStrategy
from src.strategy.mean_reversion import MeanReversionStrategy


class EnsembleStrategy(BaseStrategy):
    """
    Ensemble strategy that combines multiple strategies using voting mechanism.
    BUY=+1, SELL=-1, HOLD=0
    """
    
    def __init__(self, params: Dict = None):
        super().__init__("Ensemble", params)
        self.strategies = {
            'momentum': MomentumStrategy(params.get('momentum', {})),
            'mean_reversion': MeanReversionStrategy(params.get('mean_reversion', {}))
        }
        self.weights = params.get('weights', {
            'momentum': 0.5, 'mean_reversion': 0.5
        })
        
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """Generate ensemble signals by combining sub-strategy signals."""
        all_signals = {}
        for name, strategy in self.strategies.items():
            signals = strategy.generate_signals(data)
            for sig in signals:
                if sig.code not in all_signals:
                    all_signals[sig.code] = {
                        'signals': [], 'total_score': 0.0, 'total_strength': 0.0
                    }
                all_signals[sig.code]['signals'].append({
                    'strategy': name, 'direction': sig.direction,
                    'score': sig.score, 'strength': sig.strength, 'reason': sig.reason
                })
                all_signals[sig.code]['total_score'] += sig.score * self.weights.get(name, 0.5)
                all_signals[sig.code]['total_strength'] += sig.strength * self.weights.get(name, 0.5)
        ensemble_signals = []
        for code, info in all_signals.items():
            buy_count = sum(1 for s in info['signals'] if s['direction'] == 'BUY')
            sell_count = sum(1 for s in info['signals'] if s['direction'] == 'SELL')
            total = len(info['signals'])
            consensus = (buy_count - sell_count) / total if total > 0 else 0
            if consensus > 0.3:
                direction = 'BUY'
            elif consensus < -0.3:
                direction = 'SELL'
            else:
                direction = 'HOLD'
            reasons = [f"{s['strategy']}: {s['reason']}" for s in info['signals']]
            sig = Signal(code=code, direction=direction, strength=info['total_strength'],
                        reason=', '.join(reasons))
            sig.score = info['total_score']
            ensemble_signals.append(sig)
        ensemble_signals.sort(key=lambda x: x.score, reverse=True)
        return ensemble_signals


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
        """Calculate dynamic weights based on recent performance."""
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
        total_score = sum(max(s, 0) for s in scores.values())
        if total_score > 0:
            self.weights = {s: max(score, 0) / total_score for s, score in scores.items()}
        else:
            self._initialize_weights()
        return self.weights
        
    def ensemble_prediction(self, predictions: Dict[str, float]) -> float:
        """Combine strategy predictions using weights."""
        ensemble = 0.0
        for strategy, pred in predictions.items():
            if strategy in self.weights:
                ensemble += self.weights[strategy] * pred
        return ensemble
        
    def generate_report(self) -> str:
        """Generate ensemble report."""
        lines = ["=" * 60, "🎯 策略组合报告", "=" * 60]
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
