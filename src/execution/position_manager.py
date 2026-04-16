"""
Position Manager
Manages portfolio positions, rebalancing, and trade execution logic.
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine

@dataclass
class Position:
    """Represents a single stock position."""
    code: str
    shares: int
    avg_cost: float
    current_price: float = 0.0
    target_weight: float = 0.0  # Target portfolio weight
    
    @property
    def market_value(self) -> float:
        return self.shares * self.current_price
    
    @property
    def pnl(self) -> float:
        return (self.current_price - self.avg_cost) * self.shares
    
    @property
    def pnl_pct(self) -> float:
        if self.avg_cost == 0:
            return 0.0
        return ((self.current_price - self.avg_cost) / self.avg_cost) * 100.0

@dataclass
class TradeOrder:
    """Represents a trade order."""
    code: str
    action: str  # 'BUY' or 'SELL'
    shares: int
    price: float
    reason: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class PositionManager:
    """
    Manages portfolio positions and generates rebalancing orders.
    """
    
    def __init__(self, config_path: str = None):
        # Load config
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
            risk_cfg = cfg.get('risk', {})
        else:
            risk_cfg = {}
            
        # Risk parameters
        self.total_capital = risk_cfg.get('total_capital', 1000000)
        self.max_single_weight = risk_cfg.get('max_single_weight', 0.10)  # Max 10% per stock
        self.max_position_count = risk_cfg.get('max_position_count', 10)  # Max 10 positions
        self.rebalance_threshold = risk_cfg.get('rebalance_threshold', 0.05)  # 5% deviation triggers rebalance
        
        # State
        self.positions: Dict[str, Position] = {}
        self.cash = self.total_capital
        self.trade_log: List[TradeOrder] = []
        
        # DB
        self.engine = get_db_engine()
        
    def update_prices(self, prices: Dict[str, float]):
        """Update current prices for all positions."""
        for code, price in prices.items():
            if code in self.positions:
                self.positions[code].current_price = price
                
    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value."""
        positions_value = sum(p.market_value for p in self.positions.values())
        return self.cash + positions_value
        
    def get_portfolio_weights(self) -> Dict[str, float]:
        """Calculate current weight of each position."""
        total = self.get_portfolio_value()
        if total == 0:
            return {}
        return {code: pos.market_value / total for code, pos in self.positions.items()}
        
    def generate_rebalance_orders(self, target_weights: Dict[str, float], current_prices: Dict[str, float]) -> List[TradeOrder]:
        """
        Generate orders to rebalance portfolio to target weights.
        
        Args:
            target_weights: Dict of code -> target_weight (e.g., {'SH.600519': 0.10})
            current_prices: Dict of code -> current_price
            
        Returns:
            List of TradeOrder objects
        """
        orders = []
        total_value = self.get_portfolio_value()
        
        # 1. Calculate target shares for each stock
        target_shares = {}
        for code, weight in target_weights.items():
            if weight <= 0:
                continue
                
            price = current_prices.get(code, 0)
            if price <= 0:
                continue
                
            # Target value for this stock
            target_value = total_value * weight
            
            # Target shares (round down to 100 for A-shares)
            shares = int(target_value / price / 100) * 100
            
            target_shares[code] = {
                'shares': shares,
                'price': price,
                'value': shares * price
            }
            
        # 2. Generate SELL orders for positions to reduce/exit
        for code, pos in self.positions.items():
            target = target_shares.get(code, {'shares': 0})
            diff = pos.shares - target['shares']
            
            if diff > 0:
                # Need to sell
                reason = "Rebalance: Reduce position" if target['shares'] > 0 else "Rebalance: Exit position"
                orders.append(TradeOrder(
                    code=code,
                    action='SELL',
                    shares=diff,
                    price=pos.current_price,
                    reason=reason
                ))
                
        # 3. Generate BUY orders for new/increase positions
        for code, target in target_shares.items():
            current_shares = self.positions[code].shares if code in self.positions else 0
            diff = target['shares'] - current_shares
            
            if diff > 0:
                # Need to buy
                orders.append(TradeOrder(
                    code=code,
                    action='BUY',
                    shares=diff,
                    price=target['price'],
                    reason="Rebalance: Buy/Increase position"
                ))
                
        # 4. Validate cash constraint
        buy_cost = sum(o.shares * o.price for o in orders if o.action == 'BUY')
        sell_proceeds = sum(o.shares * o.price for o in orders if o.action == 'SELL')
        
        # If buy cost exceeds available cash + sell proceeds, scale down buys
        available = self.cash + sell_proceeds
        if buy_cost > available:
            scale = available / buy_cost if buy_cost > 0 else 0
            for order in orders:
                if order.action == 'BUY':
                    order.shares = int(order.shares * scale / 100) * 100
                    
        return orders
        
    def execute_orders(self, orders: List):
        """
        Simulate execution of orders (update positions and cash).
        In production, this would call Futu API.
        Accepts both TradeOrder objects and dicts.
        """
        for order in orders:
            # Support both dict and TradeOrder objects
            if isinstance(order, dict):
                action = order.get('action')
                code = order.get('code')
                shares = order.get('shares')
                price = order.get('price')
            else:
                action = order.action
                code = order.code
                shares = order.shares
                price = order.price
                
            if action == 'BUY':
                cost = shares * price
                if cost <= self.cash:
                    self.cash -= cost
                    
                    if code in self.positions:
                        # Average up
                        pos = self.positions[code]
                        total_shares = pos.shares + shares
                        pos.avg_cost = (pos.avg_cost * pos.shares + cost) / total_shares
                        pos.shares = total_shares
                    else:
                        self.positions[code] = Position(
                            code=code,
                            shares=shares,
                            avg_cost=price,
                            current_price=price
                        )
                        
            elif action == 'SELL':
                if code in self.positions:
                    pos = self.positions[code]
                    proceed = shares * price
                    self.cash += proceed
                    
                    pos.shares -= shares
                    if pos.shares <= 0:
                        del self.positions[code]
                        
            self.trade_log.append(order)
            
    def get_performance_summary(self) -> Dict:
        """Get portfolio performance summary."""
        total = self.get_portfolio_value()
        pnl = total - self.total_capital
        pnl_pct = (pnl / self.total_capital) * 100
        
        return {
            'total_value': total,
            'cash': self.cash,
            'positions_value': total - self.cash,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'num_positions': len(self.positions),
            'trade_count': len(self.trade_log)
        }
        
    def generate_report(self) -> str:
        """Generate text report of portfolio status."""
        summary = self.get_performance_summary()
        
        report = f"# 💼 投资组合报告\n"
        report += f"日期: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        report += f"## 📊 总览\n"
        report += f"- 总资产: ¥{summary['total_value']:,.2f}\n"
        report += f"- 现金: ¥{summary['cash']:,.2f}\n"
        report += f"- 持仓市值: ¥{summary['positions_value']:,.2f}\n"
        report += f"- 盈亏: ¥{summary['pnl']:,.2f} ({summary['pnl_pct']:.2f}%)\n"
        report += f"- 持仓数量: {summary['num_positions']}\n\n"
        
        if self.positions:
            report += "## 📈 持仓详情\n"
            report += "| 代码 | 股数 | 成本价 | 现价 | 盈亏% |\n"
            report += "|------|------|--------|------|-------|\n"
            for code, pos in self.positions.items():
                report += f"| {code} | {pos.shares} | {pos.avg_cost:.2f} | {pos.current_price:.2f} | {pos.pnl_pct:.2f}% |\n"
                
        return report
