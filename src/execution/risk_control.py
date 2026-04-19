"""
Risk Control Module
Position sizing, stop-loss, take-profit, and drawdown protection.
"""

import os
import yaml
from typing import Dict
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class RiskManager:
    """
    Manages portfolio risk with configurable rules.
    """
    
    def __init__(self, config_path: str = None):
        # Load config
        risk_cfg = {}
        if config_path:
            if isinstance(config_path, dict):
                # Allow passing config dict directly (for testing)
                risk_cfg = config_path.get('risk', config_path)
            elif os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = yaml.safe_load(f)
                risk_cfg = cfg.get('risk', {})
            
        # Risk Parameters
        self.total_capital = risk_cfg.get('total_capital', 1000000)
        self.max_single_position_pct = risk_cfg.get('max_single_position_pct', 0.15)  # 15% max per stock
        self.max_total_exposure_pct = risk_cfg.get('max_total_exposure_pct', 0.90)     # 90% max invested
        self.stop_loss_pct = risk_cfg.get('stop_loss_pct', 0.08)                      # 8% stop-loss
        self.take_profit_pct = risk_cfg.get('take_profit_pct', 0.20)                  # 20% take-profit
        self.max_daily_loss_pct = risk_cfg.get('max_daily_loss_pct', 0.03)            # 3% daily loss limit
        self.max_drawdown_pct = risk_cfg.get('max_drawdown_pct', 0.15)                # 15% max drawdown
        
        # State tracking
        self.peak_portfolio_value = self.total_capital
        self.current_portfolio_value = self.total_capital
        self.daily_start_value = self.total_capital
        self.trade_halt = False
        self.halt_reason = ""
        
    def calculate_position_size(self, price: float, signal_score: float = 0.5) -> int:
        """
        Calculate position size based on signal strength and risk limits.
        Uses Kelly-inspired sizing capped by max_single_position_pct.
        
        Args:
            price: Current stock price
            signal_score: Signal strength (0.0 to 1.0)
            
        Returns:
            Number of shares (rounded to 100-share lots)
        """
        if price <= 0:
            return 0
            
        # Base allocation: scale by signal strength
        allocation = self.total_capital * self.max_single_position_pct * signal_score
        
        # Calculate shares
        shares = int(allocation / price)
        
        # Round down to nearest 100 (A-share/HK-share lot size)
        shares = (shares // 100) * 100
        
        return max(0, shares)
        
    def check_stop_loss(self, entry_price: float, current_price: float) -> bool:
        """Check if stop-loss is triggered."""
        if current_price <= 0 or entry_price <= 0:
            return False
        loss_pct = (entry_price - current_price) / entry_price
        return loss_pct >= self.stop_loss_pct
        
    def check_take_profit(self, entry_price: float, current_price: float) -> bool:
        """Check if take-profit is triggered."""
        if current_price <= 0 or entry_price <= 0:
            return False
        gain_pct = (current_price - entry_price) / entry_price
        return gain_pct >= self.take_profit_pct
        
    def check_portfolio_risk(self, current_value: float) -> Dict:
        """
        Check portfolio-level risk limits.
        Returns dict with risk status and any alerts.
        """
        self.current_portfolio_value = current_value
        alerts = []
        
        # Update peak
        if current_value > self.peak_portfolio_value:
            self.peak_portfolio_value = current_value
            
        # Drawdown check
        drawdown = (self.peak_portfolio_value - current_value) / self.peak_portfolio_value
        if drawdown >= self.max_drawdown_pct:
            self.trade_halt = True
            self.halt_reason = f"Max drawdown exceeded: {drawdown:.1%}"
            alerts.append("🚨 HALT: Max drawdown limit reached!")
            
        # Daily loss check
        daily_pnl = (current_value - self.daily_start_value) / self.daily_start_value
        if daily_pnl <= -self.max_daily_loss_pct:
            alerts.append(f"⚠️ Daily loss limit: {daily_pnl:.1%}")
            
        # Exposure check
        exposure = 1.0 - (self.get_cash_ratio() if hasattr(self, 'get_cash_ratio') else 0.0)
        
        return {
            'drawdown': drawdown,
            'daily_pnl': daily_pnl,
            'trade_halt': self.trade_halt,
            'halt_reason': self.halt_reason,
            'alerts': alerts
        }
        
    def reset_daily(self, value: float = None):
        """Reset daily tracking (call at start of each trading day)."""
        self.daily_start_value = value or self.current_portfolio_value
        self.trade_halt = False
        self.halt_reason = ""
        
    def generate_order(self, code: str, price: float, signal_score: float, current_positions: Dict) -> Dict:
        """
        Generate a validated order with risk checks.
        
        Returns:
            Order dict or None if rejected
        """
        if self.trade_halt:
            return {'rejected': True, 'reason': self.halt_reason}
            
        # Calculate position size
        shares = self.calculate_position_size(price, signal_score)
        if shares <= 0:
            return {'rejected': True, 'reason': 'Invalid position size'}
            
        # Check existing position
        existing = current_positions.get(code, 0)
        total_shares = existing + shares
        total_value = total_shares * price
        
        # Check single position limit
        if total_value > self.total_capital * self.max_single_position_pct:
            max_shares = int(self.total_capital * self.max_single_position_pct / price / 100) * 100
            shares = max(0, max_shares - existing)
            if shares <= 0:
                return {'rejected': True, 'reason': 'Single position limit reached'}
                
        return {
            'rejected': False,
            'code': code,
            'action': 'BUY',
            'shares': shares,
            'price': price,
            'estimated_value': shares * price,
            'stop_loss': price * (1 - self.stop_loss_pct),
            'take_profit': price * (1 + self.take_profit_pct)
        }
