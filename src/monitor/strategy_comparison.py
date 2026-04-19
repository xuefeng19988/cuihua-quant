"""
Phase 23.3: Strategy Comparison Panel
Compare multiple strategies with interactive visualizations.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict

class StrategyComparisonPanel:
    """
    Compare multiple strategies with performance metrics and charts.
    """
    
    def __init__(self):
        pass
        
    def compute_metrics(self, equity_curve: pd.Series) -> Dict:
        """Compute comprehensive performance metrics."""
        if len(equity_curve) < 2:
            return {}
            
        returns = equity_curve.pct_change().dropna()
        
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        annualized = (1 + total_return) ** (252 / len(returns)) - 1 if len(returns) > 0 else 0
        volatility = returns.std() * np.sqrt(252)
        sharpe = (annualized - 0.02) / volatility if volatility > 0 else 0
        
        # Sortino
        downside = returns[returns < 0].std() * np.sqrt(252)
        sortino = (annualized - 0.02) / downside if downside > 0 else 0
        
        # Max Drawdown
        peak = equity_curve.cummax()
        drawdown = (equity_curve - peak) / peak
        max_dd = drawdown.min()
        
        # Calmar
        calmar = annualized / abs(max_dd) if max_dd != 0 else 0
        
        # Win rate
        win_rate = (returns > 0).sum() / len(returns) if len(returns) > 0 else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': max_dd,
            'calmar_ratio': calmar,
            'win_rate': win_rate,
            'trading_days': len(returns),
        }
        
    def compare_strategies(self, equity_curves: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        Compare multiple strategies.
        
        Args:
            equity_curves: Dict mapping strategy name to equity curve Series
            
        Returns:
            DataFrame with metrics for each strategy
        """
        results = []
        for name, curve in equity_curves.items():
            metrics = self.compute_metrics(curve)
            metrics['strategy'] = name
            results.append(metrics)
            
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values('sharpe_ratio', ascending=False).reset_index(drop=True)
        return df
        
    def generate_comparison_report(self, equity_curves: Dict[str, pd.Series]) -> str:
        """Generate comprehensive comparison report."""
        df = self.compare_strategies(equity_curves)
        
        if df.empty:
            return "⚠️ No strategy data to compare"
            
        lines = []
        lines.append("=" * 70)
        lines.append("📊 策略对比报告")
        lines.append("=" * 70)
        
        # Summary table
        lines.append(f"\n{'策略':<15} {'年化收益':>10} {'夏普':>8} {'最大回撤':>10} {'胜率':>8}")
        lines.append("-" * 60)
        
        for _, row in df.iterrows():
            lines.append(
                f"{row['strategy']:<15} "
                f"{row['annualized_return']:>10.2%} "
                f"{row['sharpe_ratio']:>8.2f} "
                f"{row['max_drawdown']:>10.2%} "
                f"{row['win_rate']:>8.1%}"
            )
            
        # Best strategy
        best = df.iloc[0]
        lines.append(f"\n🏆 最佳策略: {best['strategy']}")
        lines.append(f"  年化收益: {best['annualized_return']:.2%}")
        lines.append(f"  夏普比率: {best['sharpe_ratio']:.2f}")
        lines.append(f"  最大回撤: {best['max_drawdown']:.2%}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    panel = StrategyComparisonPanel()
    
    # Test with mock data
    np.random.seed(42)
    days = 252
    strategies = {
        'SMA_Cross': pd.Series(100000 * np.cumprod(1 + np.random.normal(0.0005, 0.015, days))),
        'Momentum': pd.Series(100000 * np.cumprod(1 + np.random.normal(0.0008, 0.018, days))),
        'Mean_Revert': pd.Series(100000 * np.cumprod(1 + np.random.normal(0.0003, 0.012, days))),
    }
    
    print(panel.generate_comparison_report(strategies))
