"""
Phase 9.1: Options Strategy Support
Support for stock options trading and analysis.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from scipy import stats

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

class OptionsAnalyzer:
    """
    Analyzes stock options and generates trading signals.
    Supports: Black-Scholes pricing, Greeks calculation, strategy recommendations.
    """
    
    def __init__(self):
        pass
        
    def black_scholes(self, S: float, K: float, T: float, r: float, sigma: float,
                      option_type: str = 'call') -> Dict:
        """
        Calculate Black-Scholes option price and Greeks.
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Dict with price and Greeks
        """
        d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'call':
            price = S * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2)
            delta = stats.norm.cdf(d1)
        else:
            price = K * np.exp(-r * T) * stats.norm.cdf(-d2) - S * stats.norm.cdf(-d1)
            delta = stats.norm.cdf(d1) - 1
            
        gamma = stats.norm.pdf(d1) / (S * sigma * np.sqrt(T))
        theta = -(S * stats.norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
        if option_type == 'call':
            theta += r * K * np.exp(-r * T) * stats.norm.cdf(d2)
        else:
            theta -= r * K * np.exp(-r * T) * stats.norm.cdf(-d2)
        theta /= 365  # Per day
        
        vega = S * stats.norm.pdf(d1) * np.sqrt(T) / 100
        rho = K * T * np.exp(-r * T) * stats.norm.cdf(d2) / 100 if option_type == 'call' else -K * T * np.exp(-r * T) * stats.norm.cdf(-d2) / 100
        
        return {
            'price': price,
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        }
        
    def implied_volatility(self, market_price: float, S: float, K: float, T: float,
                           r: float, option_type: str = 'call', tol: float = 1e-6) -> float:
        """Calculate implied volatility using Newton-Raphson method."""
        sigma = 0.3  # Initial guess
        for _ in range(100):
            bs = self.black_scholes(S, K, T, r, sigma, option_type)
            price_diff = bs['price'] - market_price
            vega = bs['vega'] * 100  # Convert back
            
            if abs(vega) < 1e-10:
                break
                
            sigma = sigma - price_diff / vega
            
            if abs(price_diff) < tol:
                break
                
        return max(sigma, 0.01)
        
    def generate_strategy_recommendations(self, S: float, sigma: float, T: float, 
                                          r: float = 0.03) -> List[Dict]:
        """
        Generate options strategy recommendations based on market conditions.
        """
        strategies = []
        
        # Covered Call
        if sigma > 0.3:
            strategies.append({
                'name': 'Covered Call',
                'description': '持有正股 + 卖出 call',
                'signal': 'NEUTRAL_TO_BULLISH',
                'max_profit': 'Limited',
                'max_loss': 'Substantial',
                'iv_rank': 'High IV environment'
            })
            
        # Protective Put
        strategies.append({
            'name': 'Protective Put',
            'description': '持有正股 + 买入 put 作为保险',
            'signal': 'BULLISH_WITH_PROTECTION',
            'max_profit': 'Unlimited',
            'max_loss': 'Limited',
            'iv_rank': 'Any'
        })
        
        # Straddle (if expecting high volatility)
        if sigma < 0.2:
            strategies.append({
                'name': 'Long Straddle',
                'description': '同时买入 call 和 put',
                'signal': 'VOLATILITY_EXPECTED',
                'max_profit': 'Unlimited',
                'max_loss': 'Limited to premium',
                'iv_rank': 'Low IV environment'
            })
            
        return strategies
        
    def calculate_strategy_pnl(self, strategy: str, S: float, K: float, T: float,
                               r: float, sigma: float, premium: float) -> Dict:
        """Calculate P&L for common options strategies."""
        if strategy == 'covered_call':
            # Long stock + short call
            max_profit = K - S + premium
            max_loss = S - premium
            breakeven = S - premium
        elif strategy == 'protective_put':
            # Long stock + long put
            max_profit = float('inf')
            max_loss = S - K - premium
            breakeven = S + premium
        elif strategy == 'long_straddle':
            # Long call + long put
            max_profit = float('inf')
            max_loss = premium
            breakeven_up = K + premium
            breakeven_down = K - premium
            return {
                'strategy': strategy,
                'max_profit': 'Unlimited',
                'max_loss': max_loss,
                'breakeven_up': breakeven_up,
                'breakeven_down': breakeven_down
            }
            
        return {
            'strategy': strategy,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'breakeven': breakeven
        }


if __name__ == "__main__":
    analyzer = OptionsAnalyzer()
    
    # Test Black-Scholes
    result = analyzer.black_scholes(S=100, K=105, T=30/365, r=0.03, sigma=0.25)
    print("Black-Scholes Result:")
    for k, v in result.items():
        print(f"  {k}: {v:.4f}")
        
    # Generate recommendations
    recs = analyzer.generate_strategy_recommendations(S=100, sigma=0.35, T=30/365)
    print("\nStrategy Recommendations:")
    for rec in recs:
        print(f"  {rec['name']}: {rec['description']}")
