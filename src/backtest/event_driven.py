"""
Phase 35: Event-Driven Backtester
Event-driven architecture for realistic backtesting simulation.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Callable
from enum import Enum

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class EventType(Enum):
    MARKET = "MARKET"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"
    
class Event:
    """Base event class."""
    def __init__(self, event_type: EventType, data: Dict):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()
        
class EventDrivenBacktester:
    """
    Event-driven backtesting engine.
    Simulates realistic trading with event queue.
    """
    
    def __init__(self, initial_capital: float = 1000000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, int] = {}
        self.event_queue: List[Event] = []
        self.trade_log: List[Dict] = []
        self.equity_curve: List[Dict] = []
        
    def run(self, data: pd.DataFrame, strategy: Callable) -> Dict:
        """
        Run event-driven backtest.
        
        Args:
            data: Market data DataFrame
            strategy: Strategy function that returns signals
            
        Returns:
            Backtest results
        """
        for idx, row in data.iterrows():
            # Market event
            market_event = Event(EventType.MARKET, row.to_dict())
            self.event_queue.append(market_event)
            
            # Process events
            while self.event_queue:
                event = self.event_queue.pop(0)
                
                if event.event_type == EventType.MARKET:
                    # Generate signal
                    signal = strategy(event.data, self.positions)
                    if signal:
                        signal_event = Event(EventType.SIGNAL, {
                            **signal,
                            'price': row['close'],
                            'date': row.get('date', idx)
                        })
                        self.event_queue.append(signal_event)
                        
                elif event.event_type == EventType.SIGNAL:
                    # Create order
                    order_event = Event(EventType.ORDER, event.data)
                    self.event_queue.append(order_event)
                    
                elif event.event_type == EventType.ORDER:
                    # Fill order (with slippage and commission)
                    fill = self._fill_order(event.data)
                    fill_event = Event(EventType.FILL, fill)
                    self.event_queue.append(fill_event)
                    
                elif event.event_type == EventType.FILL:
                    # Update portfolio
                    self._update_portfolio(event.data)
                    
            # Record equity
            self._record_equity(row.get('date', idx))
            
        return self._generate_results()
        
    def _fill_order(self, order: Dict) -> Dict:
        """Fill order with slippage and commission."""
        price = order['price']
        slippage = price * 0.001  # 0.1% slippage
        commission = order.get('shares', 0) * price * 0.001  # 0.1% commission
        
        if order.get('action', '').upper() == 'BUY':
            fill_price = price + slippage
            total_cost = order['shares'] * fill_price + commission
            if total_cost <= self.cash:
                self.cash -= total_cost
                return {
                    'action': 'BUY',
                    'code': order['code'],
                    'shares': order['shares'],
                    'price': fill_price,
                    'commission': commission,
                    'filled': True
                }
        else:  # SELL
            fill_price = price - slippage
            code = order['code']
            if code in self.positions and self.positions[code] >= order.get('shares', 0):
                proceed = order['shares'] * fill_price - commission
                self.cash += proceed
                return {
                    'action': 'SELL',
                    'code': code,
                    'shares': order['shares'],
                    'price': fill_price,
                    'commission': commission,
                    'filled': True
                }
                
        return {**order, 'filled': False}
        
    def _update_portfolio(self, fill: Dict):
        """Update portfolio after fill."""
        if not fill.get('filled'):
            return
            
        code = fill['code']
        shares = fill['shares']
        
        if fill['action'] == 'BUY':
            self.positions[code] = self.positions.get(code, 0) + shares
        else:
            self.positions[code] = self.positions.get(code, 0) - shares
            if self.positions[code] <= 0:
                del self.positions[code]
                
        self.trade_log.append(fill)
        
    def _record_equity(self, date):
        """Record equity curve point."""
        self.equity_curve.append({
            'date': date,
            'cash': self.cash,
            'positions': len(self.positions)
        })
        
    def _generate_results(self) -> Dict:
        """Generate backtest results."""
        return {
            'initial_capital': self.initial_capital,
            'final_cash': self.cash,
            'total_trades': len(self.trade_log),
            'equity_curve': self.equity_curve,
            'trade_log': self.trade_log
        }
