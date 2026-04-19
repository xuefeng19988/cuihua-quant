"""
Phase 37: Live Trading Monitor
Real-time monitoring for live trading with alerts and kill switch.
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class LiveTradingMonitor:
    """
    Real-time monitoring for live trading.
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.max_daily_loss = self.config.get('max_daily_loss_pct', 0.03)
        self.max_drawdown = self.config.get('max_drawdown_pct', 0.15)
        self.alert_callbacks: List[Callable] = []
        self.kill_switch_callbacks: List[Callable] = []
        
        self._trading_halted = False
        self._daily_start_value = 0
        self._peak_value = 0
        self._current_value = 0
        self._daily_trades = 0
        self._alerts_sent = 0
        
    def set_daily_start(self, value: float):
        """Set daily starting value."""
        self._daily_start_value = value
        self._peak_value = value
        self._current_value = value
        self._daily_trades = 0
        
    def update_value(self, current_value: float):
        """Update current portfolio value."""
        self._current_value = current_value
        if current_value > self._peak_value:
            self._peak_value = current_value
            
    def check_risk_limits(self) -> Dict:
        """Check all risk limits."""
        alerts = []
        
        if self._daily_start_value > 0:
            # Daily loss check
            daily_pnl = (self._current_value - self._daily_start_value) / self._daily_start_value
            if daily_pnl <= -self.max_daily_loss:
                alerts.append({
                    'type': 'DAILY_LOSS_LIMIT',
                    'severity': 'CRITICAL',
                    'message': f'🚨 日亏损限制触发: {daily_pnl:.1%}',
                    'action': 'HALT'
                })
                
            # Drawdown check
            drawdown = (self._peak_value - self._current_value) / self._peak_value
            if drawdown >= self.max_drawdown:
                alerts.append({
                    'type': 'MAX_DRAWDOWN',
                    'severity': 'CRITICAL',
                    'message': f'🚨 最大回撤触发: {drawdown:.1%}',
                    'action': 'HALT'
                })
                
            # Warning levels
            if daily_pnl <= -self.max_daily_loss * 0.75:
                alerts.append({
                    'type': 'DAILY_LOSS_WARNING',
                    'severity': 'WARNING',
                    'message': f'⚠️ 接近日亏损限制: {daily_pnl:.1%}'
                })
                
        return {
            'alerts': alerts,
            'trading_halted': self._trading_halted,
            'daily_pnl': (self._current_value - self._daily_start_value) / self._daily_start_value if self._daily_start_value > 0 else 0,
            'drawdown': (self._peak_value - self._current_value) / self._peak_value if self._peak_value > 0 else 0
        }
        
    def record_trade(self):
        """Record a trade."""
        self._daily_trades += 1
        
    def halt_trading(self, reason: str):
        """Emergency halt trading."""
        self._trading_halted = True
        alert = {
            'type': 'TRADING_HALTED',
            'severity': 'CRITICAL',
            'message': f'🛑 交易暂停: {reason}',
            'timestamp': datetime.now().isoformat()
        }
        self._send_alert(alert)
        self._trigger_kill_switch(reason)
        
    def resume_trading(self):
        """Resume trading after halt."""
        self._trading_halted = False
        
    def register_alert_callback(self, callback: Callable):
        """Register alert callback."""
        self.alert_callbacks.append(callback)
        
    def register_kill_switch_callback(self, callback: Callable):
        """Register kill switch callback."""
        self.kill_switch_callbacks.append(callback)
        
    def _send_alert(self, alert: Dict):
        """Send alert to all callbacks."""
        self._alerts_sent += 1
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                pass
                
    def _trigger_kill_switch(self, reason: str):
        """Trigger kill switch."""
        for callback in self.kill_switch_callbacks:
            try:
                callback(reason)
            except Exception as e:
                pass
                
    def get_status(self) -> Dict:
        """Get monitor status."""
        return {
            'trading_halted': self._trading_halted,
            'daily_trades': self._daily_trades,
            'alerts_sent': self._alerts_sent,
            'current_value': self._current_value,
            'daily_pnl': (self._current_value - self._daily_start_value) / self._daily_start_value if self._daily_start_value > 0 else 0,
            'drawdown': (self._peak_value - self._current_value) / self._peak_value if self._peak_value > 0 else 0
        }
        
    def generate_report(self) -> str:
        """Generate monitor report."""
        status = self.get_status()
        
        lines = []
        lines.append("=" * 60)
        lines.append("🔴 实盘监控报告")
        lines.append("=" * 60)
        
        lines.append(f"\n📊 交易状态: {'🛑 暂停' if status['trading_halted'] else '✅ 运行中'}")
        lines.append(f"📈 今日交易: {status['daily_trades']} 笔")
        lines.append(f"🔔 警报发送: {status['alerts_sent']} 次")
        
        lines.append(f"\n💰 盈亏: {status['daily_pnl']:+.2%}")
        lines.append(f"📉 回撤: {status['drawdown']:.2%}")
        
        return "\n".join(lines)
