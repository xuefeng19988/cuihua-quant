"""
Phase 59-62: Final Advanced Modules
Phase 59: Adaptive Position Sizing
Phase 60: Market Impact Model
Phase 61: Transaction Cost Analysis
Phase 62: Strategy Rotation Engine
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# ==================== Phase 59: Adaptive Position Sizing ====================

class AdaptivePositionSizer:
    """
    Adaptive position sizing based on market conditions and strategy performance.
    """
    def __init__(self, base_size: float = 0.10, max_size: float = 0.20,
                 min_size: float = 0.02):
        self.base_size = base_size
        self.max_size = max_size
        self.min_size = min_size
        
    def calculate_size(self, volatility: float, recent_performance: float,
                      market_regime: str = 'normal') -> float:
        """
        Calculate adaptive position size.
        
        Args:
            volatility: Current market volatility
            recent_performance: Recent strategy performance
            market_regime: Current market regime
            
        Returns:
            Position size as fraction of portfolio
        """
        # Start with base size
        size = self.base_size
        
        # Adjust for volatility (lower size in high vol)
        vol_adjustment = 1.0 - (volatility - 0.20) * 0.5
        size *= max(0.5, min(1.5, vol_adjustment))
        
        # Adjust for recent performance
        if recent_performance > 0:
            size *= (1 + min(recent_performance, 0.20))
        else:
            size *= (1 + recent_performance)
            
        # Adjust for market regime
        regime_multipliers = {
            'bull': 1.2,
            'normal': 1.0,
            'bear': 0.6,
            'crisis': 0.3
        }
        size *= regime_multipliers.get(market_regime, 1.0)
        
        # Clamp to min/max
        return max(self.min_size, min(self.max_size, size))


# ==================== Phase 60: Market Impact Model ====================

class MarketImpactModel:
    """
    Model market impact of trades.
    """
    @staticmethod
    def calculate_impact(trade_size: float, avg_volume: float, 
                        volatility: float, spread: float = 0.001) -> float:
        """
        Calculate market impact cost.
        
        Uses Almgren-Chriss model simplified.
        """
        # Participation rate
        participation = trade_size / avg_volume if avg_volume > 0 else 0
        
        # Impact = spread + temporary impact + permanent impact
        temporary = 0.5 * spread * np.sqrt(participation)
        permanent = 0.1 * volatility * participation
        
        return spread + temporary + permanent
    
    @staticmethod
    def optimal_execution(trade_size: float, duration: int = 60,
                         volatility: float = 0.20, risk_aversion: float = 1e-6) -> Dict:
        """
        Calculate optimal execution schedule.
        """
        # Simple TWAP vs VWAP comparison
        n_trades = duration
        
        # TWAP
        twap_size = trade_size / n_trades
        twap_impact = MarketImpactModel.calculate_impact(twap_size, trade_size * 10, volatility)
        
        # VWAP (front-loaded)
        vwap_sizes = np.array([np.exp(-i/10) for i in range(n_trades)])
        vwap_sizes = vwap_sizes / vwap_sizes.sum() * trade_size
        
        return {
            'twap': {'size_per_trade': twap_size, 'impact': twap_impact},
            'vwap': {'sizes': vwap_sizes.tolist(), 'avg_impact': twap_impact * 0.9},
            'recommended': 'vwap' if twap_impact > 0.01 else 'twap'
        }


# ==================== Phase 61: Transaction Cost Analysis ====================

class TransactionCostAnalyzer:
    """
    Analyze transaction costs and slippage.
    """
    def __init__(self, commission_rate: float = 0.001, slippage_rate: float = 0.0005,
                 stamp_tax: float = 0.001):
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.stamp_tax = stamp_tax
        
    def calculate_total_cost(self, trade_value: float, is_buy: bool = True) -> Dict:
        """
        Calculate total transaction cost.
        """
        commission = trade_value * self.commission_rate
        slippage = trade_value * self.slippage_rate
        tax = trade_value * self.stamp_tax if not is_buy else 0
        
        total = commission + slippage + tax
        
        return {
            'commission': commission,
            'slippage': slippage,
            'stamp_tax': tax,
            'total_cost': total,
            'cost_rate': total / trade_value if trade_value > 0 else 0
        }
        
    def analyze_trades(self, trades: List[Dict]) -> Dict:
        """
        Analyze costs for a list of trades.
        """
        total_costs = 0
        total_value = 0
        
        for trade in trades:
            value = trade.get('shares', 0) * trade.get('price', 0)
            cost_info = self.calculate_total_cost(value, trade.get('action', '').upper() == 'BUY')
            total_costs += cost_info['total_cost']
            total_value += value
            
        return {
            'total_trades': len(trades),
            'total_value': total_value,
            'total_costs': total_costs,
            'avg_cost_rate': total_costs / total_value if total_value > 0 else 0
        }


# ==================== Phase 62: Strategy Rotation Engine ====================

class StrategyRotationEngine:
    """
    Rotate strategies based on market conditions and recent performance.
    """
    def __init__(self, lookback: int = 20, min_trades: int = 10):
        self.lookback = lookback
        self.min_trades = min_trades
        self.strategy_returns: Dict[str, List[float]] = {}
        
    def add_strategy_return(self, strategy: str, return_value: float):
        """Record strategy return."""
        if strategy not in self.strategy_returns:
            self.strategy_returns[strategy] = []
        self.strategy_returns[strategy].append(return_value)
        
    def select_best_strategy(self) -> str:
        """Select best performing strategy."""
        best_strategy = None
        best_score = -float('inf')
        
        for strategy, returns in self.strategy_returns.items():
            if len(returns) < self.min_trades:
                continue
                
            recent = returns[-self.lookback:]
            
            # Score: Sharpe ratio of recent returns
            mean_ret = np.mean(recent)
            std_ret = np.std(recent)
            score = mean_ret / std_ret if std_ret > 0 else mean_ret
            
            if score > best_score:
                best_score = score
                best_strategy = strategy
                
        return best_strategy or 'default'
        
    def generate_report(self) -> str:
        """Generate strategy rotation report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🔄 策略轮动报告")
        lines.append("=" * 60)
        
        for strategy, returns in self.strategy_returns.items():
            if len(returns) >= self.min_trades:
                recent = returns[-self.lookback:]
                mean_ret = np.mean(recent)
                std_ret = np.std(recent)
                sharpe = mean_ret / std_ret if std_ret > 0 else 0
                
                lines.append(f"\n📊 {strategy}")
                lines.append(f"  期数: {len(recent)}")
                lines.append(f"  平均收益: {mean_ret:.4f}")
                lines.append(f"  夏普: {sharpe:.2f}")
                
        best = self.select_best_strategy()
        lines.append(f"\n🏆 当前最佳: {best}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Test modules
    print("✅ Phase 59-62 modules loaded successfully")
    
    # Test position sizing
    sizer = AdaptivePositionSizer()
    size = sizer.calculate_size(volatility=0.25, recent_performance=0.05, market_regime='normal')
    print(f"Position size: {size:.2%}")
    
    # Test transaction costs
    analyzer = TransactionCostAnalyzer()
    cost = analyzer.calculate_total_cost(100000, is_buy=True)
    print(f"Transaction cost: ¥{cost['total_cost']:.2f} ({cost['cost_rate']:.4%})")
    
    # Test strategy rotation
    engine = StrategyRotationEngine()
    np.random.seed(42)
    for strategy in ['momentum', 'mean_reversion', 'trend']:
        for _ in range(50):
            engine.add_strategy_return(strategy, np.random.normal(0.001, 0.02))
    print(engine.generate_report())
