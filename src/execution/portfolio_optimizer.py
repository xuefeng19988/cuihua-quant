"""
Phase 47: Portfolio Optimization Engine
Modern portfolio theory implementation with multiple optimization methods.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from scipy.optimize import minimize

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class PortfolioOptimizer:
    """
    Portfolio optimization using Modern Portfolio Theory.
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        
    def calculate_portfolio_metrics(self, weights: np.ndarray, 
                                   expected_returns: np.ndarray,
                                   cov_matrix: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate portfolio return, volatility, and Sharpe ratio.
        """
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return portfolio_return, portfolio_volatility, sharpe_ratio
        
    def minimum_variance_portfolio(self, expected_returns: np.ndarray,
                                  cov_matrix: np.ndarray) -> np.ndarray:
        """
        Find minimum variance portfolio weights.
        """
        n_assets = len(expected_returns)
        initial_weights = np.ones(n_assets) / n_assets
        bounds = tuple((0.0, 1.0) for _ in range(n_assets))
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        
        result = minimize(
            fun=lambda w: np.sqrt(np.dot(w.T, np.dot(cov_matrix, w))),
            x0=initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return result.x
        
    def maximum_sharpe_portfolio(self, expected_returns: np.ndarray,
                                cov_matrix: np.ndarray) -> np.ndarray:
        """
        Find maximum Sharpe ratio portfolio weights.
        """
        n_assets = len(expected_returns)
        initial_weights = np.ones(n_assets) / n_assets
        bounds = tuple((0.0, 1.0) for _ in range(n_assets))
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        
        def negative_sharpe(weights):
            ret, vol, sharpe = self.calculate_portfolio_metrics(weights, expected_returns, cov_matrix)
            return -sharpe
            
        result = minimize(
            fun=negative_sharpe,
            x0=initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return result.x
        
    def efficient_frontier(self, expected_returns: np.ndarray,
                          cov_matrix: np.ndarray, n_points: int = 50) -> pd.DataFrame:
        """
        Calculate efficient frontier.
        """
        # Find min and max return portfolios
        min_var_weights = self.minimum_variance_portfolio(expected_returns, cov_matrix)
        _, min_vol, _ = self.calculate_portfolio_metrics(min_var_weights, expected_returns, cov_matrix)
        
        max_sharpe_weights = self.maximum_sharpe_portfolio(expected_returns, cov_matrix)
        max_ret, max_vol, _ = self.calculate_portfolio_metrics(max_sharpe_weights, expected_returns, cov_matrix)
        
        target_returns = np.linspace(min_vol * 0.9, max_ret * 1.1, n_points)
        frontier_points = []
        
        for target_return in target_returns:
            n_assets = len(expected_returns)
            initial_weights = np.ones(n_assets) / n_assets
            bounds = tuple((0.0, 1.0) for _ in range(n_assets))
            constraints = (
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},
                {'type': 'eq', 'fun': lambda w, tr=target_return: np.dot(w, expected_returns) - tr}
            )
            
            result = minimize(
                fun=lambda w: np.sqrt(np.dot(w.T, np.dot(cov_matrix, w))),
                x0=initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                ret, vol, sharpe = self.calculate_portfolio_metrics(result.x, expected_returns, cov_matrix)
                frontier_points.append({
                    'return': ret,
                    'volatility': vol,
                    'sharpe': sharpe,
                    'weights': result.x.tolist()
                })
                
        return pd.DataFrame(frontier_points)
        
    def risk_parity_portfolio(self, cov_matrix: np.ndarray) -> np.ndarray:
        """
        Calculate risk parity portfolio weights.
        """
        n_assets = cov_matrix.shape[0]
        initial_weights = np.ones(n_assets) / n_assets
        
        def risk_budget_objective(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
            risk_contrib = weights * marginal_contrib
            target_risk = portfolio_vol / n_assets
            return np.sum((risk_contrib - target_risk) ** 2)
            
        bounds = tuple((0.0, 1.0) for _ in range(n_assets))
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        
        result = minimize(
            fun=risk_budget_objective,
            x0=initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return result.x
        
    def generate_report(self, weights: np.ndarray, asset_names: List[str],
                       expected_returns: np.ndarray, cov_matrix: np.ndarray) -> str:
        """Generate portfolio optimization report."""
        portfolio_return, portfolio_volatility, sharpe_ratio = \
            self.calculate_portfolio_metrics(weights, expected_returns, cov_matrix)
            
        lines = []
        lines.append("=" * 60)
        lines.append("📊 投资组合优化报告")
        lines.append("=" * 60)
        
        lines.append(f"\n💰 组合指标")
        lines.append(f"  预期年化收益: {portfolio_return:.2%}")
        lines.append(f"  年化波动率: {portfolio_volatility:.2%}")
        lines.append(f"  夏普比率: {sharpe_ratio:.2f}")
        
        lines.append(f"\n📈 资产配置")
        for i, (name, weight) in enumerate(sorted(zip(asset_names, weights), key=lambda x: x[1], reverse=True)):
            if weight > 0.01:
                lines.append(f"  {name}: {weight:.1%}")
                
        return "\n".join(lines)


if __name__ == "__main__":
    # Test portfolio optimization
    np.random.seed(42)
    n_assets = 5
    asset_names = ['股票 A', '股票 B', '股票 C', '股票 D', '股票 E']
    
    expected_returns = np.array([0.12, 0.10, 0.08, 0.15, 0.09])
    cov_matrix = np.array([
        [0.04, 0.006, 0.008, 0.01, 0.005],
        [0.006, 0.03, 0.004, 0.008, 0.006],
        [0.008, 0.004, 0.025, 0.006, 0.004],
        [0.01, 0.008, 0.006, 0.06, 0.008],
        [0.005, 0.006, 0.004, 0.008, 0.02]
    ])
    
    optimizer = PortfolioOptimizer()
    
    # Maximum Sharpe portfolio
    max_sharpe_weights = optimizer.maximum_sharpe_portfolio(expected_returns, cov_matrix)
    print(optimizer.generate_report(max_sharpe_weights, asset_names, expected_returns, cov_matrix))
