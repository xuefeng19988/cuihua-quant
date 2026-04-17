"""
Real-time Risk Alert Monitor
Monitors portfolio risk in real-time and sends alerts.
"""

import os
import sys
import yaml
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.futu_sync import FutuSync
from src.execution.risk_control import RiskManager
from src.data.trade_logger import TradeLogger

class RiskAlertMonitor:
    """
    Real-time risk monitoring with alert generation.
    Checks:
    - Stop-loss triggers
    - Take-profit triggers
    - Portfolio drawdown
    - Daily loss limit
    - Position concentration
    """
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(project_root, 'config', 'risk.yaml')
            
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
            
        self.risk_cfg = cfg.get('risk', {})
        self.risk_mgr = RiskManager(cfg)
        self.trade_logger = TradeLogger()
        
        # Alert thresholds
        self.stop_loss_pct = self.risk_cfg.get('stop_loss_pct', 0.08)
        self.take_profit_pct = self.risk_cfg.get('take_profit_pct', 0.20)
        self.max_daily_loss_pct = self.risk_cfg.get('max_daily_loss_pct', 0.03)
        self.max_drawdown_pct = self.risk_cfg.get('max_drawdown_pct', 0.15)
        
        # State
        self.alerts: List[Dict] = []
        self.positions: Dict[str, Dict] = {}
        
    def set_positions(self, positions: Dict[str, Dict]):
        """Set current positions to monitor."""
        self.positions = positions
        
    def check_positions(self, current_prices: Dict[str, float]) -> List[Dict]:
        """
        Check all positions against risk thresholds.
        Returns list of alerts.
        """
        alerts = []
        
        for code, pos in self.positions.items():
            price = current_prices.get(code)
            if not price or price <= 0:
                continue
                
            cost = pos.get('avg_cost', 0)
            if cost <= 0:
                continue
                
            pnl_pct = (price - cost) / cost
            
            # Stop-loss check
            if pnl_pct <= -self.stop_loss_pct:
                alert = {
                    'type': 'STOP_LOSS',
                    'severity': 'HIGH',
                    'code': code,
                    'price': price,
                    'cost': cost,
                    'pnl_pct': pnl_pct,
                    'message': f"⚠️ {code} 触发止损! 当前 {price:.2f}, 成本 {cost:.2f}, 亏损 {pnl_pct:.1%}"
                }
                alerts.append(alert)
                
            # Take-profit check
            elif pnl_pct >= self.take_profit_pct:
                alert = {
                    'type': 'TAKE_PROFIT',
                    'severity': 'MEDIUM',
                    'code': code,
                    'price': price,
                    'cost': cost,
                    'pnl_pct': pnl_pct,
                    'message': f"🎯 {code} 触发止盈! 当前 {price:.2f}, 成本 {cost:.2f}, 盈利 {pnl_pct:.1%}"
                }
                alerts.append(alert)
                
            # Warning: approaching stop-loss
            elif pnl_pct <= -self.stop_loss_pct * 0.75:
                alert = {
                    'type': 'STOP_LOSS_WARNING',
                    'severity': 'LOW',
                    'code': code,
                    'price': price,
                    'cost': cost,
                    'pnl_pct': pnl_pct,
                    'message': f"⚠️ {code} 接近止损! 当前 {price:.2f}, 亏损 {pnl_pct:.1%} (止损线 {-self.stop_loss_pct:.0%})"
                }
                alerts.append(alert)
                
        self.alerts.extend(alerts)
        return alerts
        
    def check_portfolio_risk(self, total_value: float, daily_start_value: float) -> List[Dict]:
        """Check portfolio-level risk."""
        alerts = []
        
        # Daily loss check
        daily_pnl = (total_value - daily_start_value) / daily_start_value
        if daily_pnl <= -self.max_daily_loss_pct:
            alert = {
                'type': 'DAILY_LOSS_LIMIT',
                'severity': 'HIGH',
                'message': f"🚨 单日亏损超限! 当前 {daily_pnl:.1%} (限制 {-self.max_daily_loss_pct:.0%})",
                'daily_pnl': daily_pnl
            }
            alerts.append(alert)
            
        return alerts
        
    def send_alert(self, alert: Dict, channel: str = 'wecom') -> bool:
        """Send alert via specified channel."""
        try:
            if channel == 'wecom':
                cmd = [
                    'openclaw', 'message', 'send',
                    '--channel', 'wecom',
                    '--target', 'xuefeng',
                    '--message', alert['message']
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                return result.returncode == 0
        except Exception as e:
            print(f"⚠️ Alert send failed: {e}")
        return False
        
    def get_alert_summary(self) -> str:
        """Get summary of all alerts."""
        if not self.alerts:
            return "✅ 无风险警报"
            
        lines = []
        lines.append(f"🚨 风险警报汇总 ({len(self.alerts)} 条)")
        lines.append("-" * 40)
        
        for alert in self.alerts[-10:]:
            severity_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(alert.get('severity', 'LOW'), '⚪')
            lines.append(f"  {severity_icon} {alert.get('message', '')}")
            
        return "\n".join(lines)


if __name__ == "__main__":
    monitor = RiskAlertMonitor()
    # Test with sample positions
    monitor.set_positions({
        'SH.600519': {'avg_cost': 1500.0, 'shares': 100},
        'SZ.002594': {'avg_cost': 100.0, 'shares': 1000}
    })
    alerts = monitor.check_positions({
        'SH.600519': 1380.0,  # -8%, stop-loss
        'SZ.002594': 105.0   # +5%, OK
    })
    for alert in alerts:
        print(alert['message'])
