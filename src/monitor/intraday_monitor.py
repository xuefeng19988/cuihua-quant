"""
Intraday Monitor Module
Real-time price monitoring with stop-loss / take-profit alerts.
"""

import os
import sys
import yaml
import json
import time
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

class IntradayMonitor:
    """
    Monitors positions during trading hours.
    Checks for:
    - Stop-loss triggers
    - Take-profit triggers
    - Price anomalies (sudden spikes/drops)
    """
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(project_root, 'config', 'risk.yaml')
            
        # Load config
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
            monitor_cfg = cfg.get('monitor', {})
        else:
            monitor_cfg = {}
            
        self.anomaly_threshold = monitor_cfg.get('anomaly_threshold', 0.03)  # 3%
        self.check_interval = monitor_cfg.get('check_interval', 300)  # 5 minutes
        
        # State
        self.positions: Dict[str, Dict] = {}
        self.last_prices: Dict[str, float] = {}
        self.alerts: List[Dict] = []
        
    def set_positions(self, positions: Dict[str, Dict]):
        """Set current positions to monitor."""
        self.positions = positions
        
    def load_from_trade_log(self):
        """Load positions from trade log."""
        from src.data.trade_logger import TradeLogger
        logger = TradeLogger()
        orders = logger.get_recent_orders(limit=50)
        
        # Reconstruct positions from filled orders
        for order in orders:
            if order['status'] == 'FILLED':
                code = order['code']
                if code not in self.positions:
                    self.positions[code] = {
                        'shares': 0,
                        'avg_cost': 0.0,
                        'stop_loss': 0.0,
                        'take_profit': 0.0
                    }
                pos = self.positions[code]
                if order['action'] == 'BUY':
                    total_shares = pos['shares'] + order['filled_shares']
                    pos['avg_cost'] = (pos['avg_cost'] * pos['shares'] + order['filled_price'] * order['filled_shares']) / total_shares
                    pos['shares'] = total_shares
                    
    def check_prices(self, current_prices: Dict[str, float]) -> List[Dict]:
        """
        Check current prices against stop-loss / take-profit levels.
        Returns list of alerts.
        """
        alerts = []
        
        for code, price in current_prices.items():
            if code not in self.positions:
                continue
                
            pos = self.positions[code]
            cost = pos.get('avg_cost', 0)
            stop_loss = pos.get('stop_loss', 0)
            take_profit = pos.get('take_profit', 0)
            
            if cost <= 0:
                continue
                
            # Stop-loss check
            if stop_loss > 0 and price <= stop_loss:
                alert = {
                    'type': 'STOP_LOSS',
                    'code': code,
                    'price': price,
                    'stop_loss': stop_loss,
                    'loss_pct': (price - cost) / cost,
                    'action': 'SELL',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                alerts.append(alert)
                
            # Take-profit check
            if take_profit > 0 and price >= take_profit:
                alert = {
                    'type': 'TAKE_PROFIT',
                    'code': code,
                    'price': price,
                    'take_profit': take_profit,
                    'profit_pct': (price - cost) / cost,
                    'action': 'SELL',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                alerts.append(alert)
                
            # Anomaly check (sudden price movement)
            if code in self.last_prices:
                prev = self.last_prices[code]
                if prev > 0:
                    change = abs(price - prev) / prev
                    if change >= self.anomaly_threshold:
                        direction = 'UP' if price > prev else 'DOWN'
                        alert = {
                            'type': 'ANOMALY',
                            'code': code,
                            'price': price,
                            'prev_price': prev,
                            'change_pct': change,
                            'direction': direction,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        alerts.append(alert)
                        
            self.last_prices[code] = price
            
        self.alerts.extend(alerts)
        return alerts
        
    def get_monitor_status(self) -> Dict:
        """Get current monitoring status."""
        return {
            'monitored_positions': len(self.positions),
            'tracked_stocks': len(self.last_prices),
            'total_alerts': len(self.alerts),
            'recent_alerts': self.alerts[-10:] if self.alerts else []
        }
