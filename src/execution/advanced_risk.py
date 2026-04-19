"""
Phase 40: Enhanced Risk Management
Advanced risk metrics and portfolio risk analysis.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class AdvancedRiskManager:
    """
    Advanced risk management with VaR, CVaR, stress testing.
    """
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
        
    def calculate_var(self, returns: pd.Series, method: str = 'historical') -> float:
        """
        Calculate Value at Risk.
        
        Args:
            returns: Portfolio returns series
            method: 'historical', 'parametric', or 'monte_carlo'
            
        Returns:
            VaR at confidence level
        """
        if method == 'historical':
            return np.percentile(returns, (1 - self.confidence_level) * 100)
        elif method == 'parametric':
            mean = returns.mean()
            std = returns.std()
            from scipy.stats import norm
            return norm.ppf(1 - self.confidence_level, mean, std)
        elif method == 'monte_carlo':
            simulated = np.random.normal(returns.mean(), returns.std(), 10000)
            return np.percentile(simulated, (1 - self.confidence_level) * 100)
        else:
            raise ValueError(f"Unknown method: {method}")
            
    def calculate_cvar(self, returns: pd.Series) -> float:
        """
        Calculate Conditional Value at Risk (Expected Shortfall).
        """
        var = self.calculate_var(returns)
        return returns[returns <= var].mean()
        
    def stress_test(self, portfolio_returns: pd.Series, 
                   scenarios: Dict[str, float] = None) -> Dict:
        """
        Run stress tests with predefined scenarios.
        
        Args:
            portfolio_returns: Historical portfolio returns
            scenarios: Dict of {scenario_name: shock_percentage}
            
        Returns:
            Stress test results
        """
        if scenarios is None:
            scenarios = {
                '2008 金融危机': -0.40,
                '2020 疫情': -0.30,
                '利率上升': -0.15,
                '市场崩盘': -0.50,
                '温和下跌': -0.10
            }
            
        results = {}
        current_value = 1.0
        
        for scenario, shock in scenarios.items():
            stressed_value = current_value * (1 + shock)
            results[scenario] = {
                'shock': shock,
                'stressed_value': stressed_value,
                'loss': current_value - stressed_value,
                'loss_pct': shock
            }
            
        return results
        
    def calculate_risk_metrics(self, returns: pd.Series, 
                              benchmark_returns: pd.Series = None) -> Dict:
        """
        Calculate comprehensive risk metrics.
        """
        metrics = {
            'volatility': returns.std() * np.sqrt(252),
            'annualized_return': returns.mean() * 252,
            'sharpe_ratio': (returns.mean() * 252 - 0.02) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
            'sortino_ratio': (returns.mean() * 252 - 0.02) / (returns[returns < 0].std() * np.sqrt(252)) if len(returns[returns < 0]) > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(returns),
            'var_95': self.calculate_var(returns, 'historical'),
            'cvar_95': self.calculate_cvar(returns),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'calmar_ratio': (returns.mean() * 252) / abs(self._calculate_max_drawdown(returns)) if self._calculate_max_drawdown(returns) != 0 else 0
        }
        
        if benchmark_returns is not None:
            metrics['beta'] = returns.cov(benchmark_returns) / benchmark_returns.var() if benchmark_returns.var() > 0 else 0
            metrics['alpha'] = metrics['annualized_return'] - (0.02 + metrics['beta'] * (benchmark_returns.mean() * 252 - 0.02))
            metrics['information_ratio'] = (returns - benchmark_returns).mean() * np.sqrt(252) / (returns - benchmark_returns).std() if (returns - benchmark_returns).std() > 0 else 0
            metrics['tracking_error'] = (returns - benchmark_returns).std() * np.sqrt(252)
            
        return metrics
        
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown from returns."""
        equity = (1 + returns).cumprod()
        peak = equity.cummax()
        drawdown = (equity - peak) / peak
        return drawdown.min()
        
    def generate_risk_report(self, returns: pd.Series, benchmark: pd.Series = None) -> str:
        """Generate comprehensive risk report."""
        metrics = self.calculate_risk_metrics(returns, benchmark)
        
        lines = []
        lines.append("=" * 60)
        lines.append("🛡️  高级风险分析报告")
        lines.append("=" * 60)
        
        lines.append(f"\n📊 收益与风险")
        lines.append(f"  年化收益: {metrics['annualized_return']:.2%}")
        lines.append(f"  波动率: {metrics['volatility']:.2%}")
        lines.append(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
        lines.append(f"  索提诺比率: {metrics['sortino_ratio']:.2f}")
        lines.append(f"  卡尔马比率: {metrics['calmar_ratio']:.2f}")
        
        lines.append(f"\n📉 下行风险")
        lines.append(f"  最大回撤: {metrics['max_drawdown']:.2%}")
        lines.append(f"  VaR (95%): {metrics['var_95']:.2%}")
        lines.append(f"  CVaR (95%): {metrics['cvar_95']:.2%}")
        
        lines.append(f"\n📈 分布特征")
        lines.append(f"  偏度: {metrics['skewness']:.3f}")
        lines.append(f"  峰度: {metrics['kurtosis']:.3f}")
        
        if benchmark is not None:
            lines.append(f"\n📊 相对基准")
            lines.append(f"  Beta: {metrics['beta']:.3f}")
            lines.append(f"  Alpha: {metrics['alpha']:.2%}")
            lines.append(f"  信息比率: {metrics['information_ratio']:.2f}")
            lines.append(f"  跟踪误差: {metrics['tracking_error']:.2%}")
            
        return "\n".join(lines)


if __name__ == "__main__":
    # Test with mock data
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.0005, 0.015, 500))
    benchmark = pd.Series(np.random.normal(0.0003, 0.012, 500))
    
    risk_mgr = AdvancedRiskManager()
    print(risk_mgr.generate_risk_report(returns, benchmark))
