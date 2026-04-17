"""
Ensemble Strategy
Combines multiple strategies into one unified signal.
"""

import os
import sys
import yaml
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.strategy.base import BaseStrategy, Signal
from src.strategy.momentum import MomentumStrategy
from src.strategy.mean_reversion import MeanReversionStrategy

class EnsembleStrategy(BaseStrategy):
    """
    Ensemble strategy that combines multiple strategies.
    Uses voting mechanism: BUY=+1, SELL=-1, HOLD=0
    """
    
    def __init__(self, params: Dict = None):
        super().__init__("Ensemble", params)
        
        # Initialize sub-strategies
        self.strategies = {
            'momentum': MomentumStrategy(params.get('momentum', {})),
            'mean_reversion': MeanReversionStrategy(params.get('mean_reversion', {}))
        }
        
        # Weights for each strategy
        self.weights = params.get('weights', {
            'momentum': 0.5,
            'mean_reversion': 0.5
        })
        
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """
        Generate ensemble signals by combining sub-strategy signals.
        """
        all_signals = {}
        
        # Run each strategy
        for name, strategy in self.strategies.items():
            signals = strategy.generate_signals(data)
            for sig in signals:
                if sig.code not in all_signals:
                    all_signals[sig.code] = {
                        'signals': [],
                        'total_score': 0.0,
                        'total_strength': 0.0
                    }
                all_signals[sig.code]['signals'].append({
                    'strategy': name,
                    'direction': sig.direction,
                    'score': sig.score,
                    'strength': sig.strength,
                    'reason': sig.reason
                })
                all_signals[sig.code]['total_score'] += sig.score * self.weights.get(name, 0.5)
                all_signals[sig.code]['total_strength'] += sig.strength * self.weights.get(name, 0.5)
                
        # Create ensemble signals
        ensemble_signals = []
        for code, info in all_signals.items():
            # Determine consensus
            buy_count = sum(1 for s in info['signals'] if s['direction'] == 'BUY')
            sell_count = sum(1 for s in info['signals'] if s['direction'] == 'SELL')
            total = len(info['signals'])
            
            # Consensus score
            consensus = (buy_count - sell_count) / total if total > 0 else 0
            
            # Determine action
            if consensus > 0.3:
                direction = 'BUY'
            elif consensus < -0.3:
                direction = 'SELL'
            else:
                direction = 'HOLD'
                
            reasons = [f"{s['strategy']}: {s['reason']}" for s in info['signals']]
            
            sig = Signal(
                code=code,
                direction=direction,
                strength=info['total_strength'],
                reason=', '.join(reasons)
            )
            sig.score = info['total_score']
            ensemble_signals.append(sig)
            
        # Sort by score
        ensemble_signals.sort(key=lambda x: x.score, reverse=True)
        return ensemble_signals
