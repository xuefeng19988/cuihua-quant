"""
Phase 36: Multi-Asset Portfolio Manager
Support for stocks, bonds, and commodities.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class MultiAssetPortfolio:
    """
    Multi-asset portfolio manager.
    Supports stocks, bonds, commodities.
    """
    
    def __init__(self, initial_capital: float = 1000000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Dict] = {}
        self.asset_classes = {
            'stocks': {'allocation': 0.70, 'positions': {}},
            'bonds': {'allocation': 0.20, 'positions': {}},
            'commodities': {'allocation': 0.10, 'positions': {}}
        }
        
    def allocate_assets(self, target_allocations: Dict[str, float]) -> Dict:
        """
        Set target asset allocations.
        
        Args:
            target_allocations: Dict of {asset_class: target_pct}
            
        Returns:
            Allocation summary
        """
        total = sum(target_allocations.values())
        if abs(total - 1.0) > 0.01:
            return {'status': 'error', 'message': f'Allocations must sum to 1.0, got {total}'}
            
        self.asset_classes = {}
        for asset_class, allocation in target_allocations.items():
            self.asset_classes[asset_class] = {
                'allocation': allocation,
                'positions': {}
            }
            
        return {
            'status': 'success',
            'allocations': target_allocations
        }
        
    def add_position(self, asset_class: str, code: str, shares: int, 
                     cost: float) -> bool:
        """Add a position to portfolio."""
        if asset_class not in self.asset_classes:
            return False
            
        total_cost = shares * cost
        if total_cost > self.cash:
            return False
            
        self.cash -= total_cost
        self.asset_classes[asset_class]['positions'][code] = {
            'shares': shares,
            'cost': cost,
            'total_cost': total_cost,
            'added_at': datetime.now().isoformat()
        }
        
        return True
        
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Dict:
        """Calculate current portfolio value."""
        total_value = self.cash
        class_values = {}
        
        for asset_class, data in self.asset_classes.items():
            class_value = 0
            for code, pos in data['positions'].items():
                if code in current_prices:
                    class_value += pos['shares'] * current_prices[code]
            class_values[asset_class] = class_value
            total_value += class_value
            
        # Calculate allocations
        allocations = {}
        for asset_class, value in class_values.items():
            allocations[asset_class] = value / total_value if total_value > 0 else 0
            
        return {
            'total_value': total_value,
            'cash': self.cash,
            'class_values': class_values,
            'allocations': allocations,
            'pnl': total_value - self.initial_capital,
            'pnl_pct': (total_value / self.initial_capital) - 1
        }
        
    def rebalance(self, current_prices: Dict[str, float]) -> List[Dict]:
        """
        Generate rebalancing trades.
        
        Returns:
            List of trades to execute
        """
        portfolio = self.get_portfolio_value(current_prices)
        total_value = portfolio['total_value']
        trades = []
        
        for asset_class, data in self.asset_classes.items():
            target_value = total_value * data['allocation']
            current_value = portfolio['class_values'].get(asset_class, 0)
            
            diff = target_value - current_value
            if abs(diff) > total_value * 0.05:  # 5% threshold
                trades.append({
                    'asset_class': asset_class,
                    'target_value': target_value,
                    'current_value': current_value,
                    'diff': diff,
                    'action': 'BUY' if diff > 0 else 'SELL'
                })
                
        return trades
        
    def generate_report(self, current_prices: Dict[str, float]) -> str:
        """Generate portfolio report."""
        portfolio = self.get_portfolio_value(current_prices)
        
        lines = []
        lines.append("=" * 60)
        lines.append("🌍 多资产投资组合报告")
        lines.append("=" * 60)
        
        lines.append(f"\n💰 总价值: ¥{portfolio['total_value']:,.2f}")
        lines.append(f"📈 盈亏: ¥{portfolio['pnl']:,.2f} ({portfolio['pnl_pct']:+.2%})")
        lines.append(f"💵 现金: ¥{portfolio['cash']:,.2f}")
        
        lines.append(f"\n📊 资产配置")
        for asset_class, data in self.asset_classes.items():
            current = portfolio['class_values'].get(asset_class, 0)
            target_pct = data['allocation']
            current_pct = portfolio['allocations'].get(asset_class, 0)
            
            lines.append(f"  {asset_class}:")
            lines.append(f"    目标: {target_pct:.0%} | 当前: {current_pct:.0%}")
            lines.append(f"    价值: ¥{current:,.2f}")
            
            if current > 0:
                lines.append(f"    持仓: {len(data['positions'])} 个")
                
        return "\n".join(lines)
