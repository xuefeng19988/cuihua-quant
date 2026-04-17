"""
Paper Trading Module
Simulates trading with real-time data but without real money.
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.futu_sync import FutuSync
from src.data.database import get_db_engine
from src.analysis.signal_gen import SignalGenerator
from src.execution.risk_control import RiskManager
from src.data.trade_logger import TradeLogger

class PaperTrader:
    """
    Paper trading simulator.
    Uses real market data and signals but simulates order execution.
    """
    
    def __init__(self, config_dir: str = None, initial_capital: float = 1000000):
        if not config_dir:
            config_dir = os.path.join(project_root, 'config')
            
        # Load configs
        self.configs = {}
        for fname in ['stocks.yaml', 'strategies.yaml', 'risk.yaml']:
            fpath = os.path.join(config_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    self.configs[fname.replace('.yaml', '')] = yaml.safe_load(f) or {}
                    
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        
        self.engine = get_db_engine()
        self.signal_gen = SignalGenerator()
        self.risk_mgr = RiskManager(self.configs.get('risk', {}))
        self.trade_logger = TradeLogger()
        
    def run_daily(self, date: str = None) -> Dict:
        """
        Simulate one day of trading.
        1. Get signals
        2. Check existing positions
        3. Execute trades
        4. Update P&L
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        if not stocks:
            return {'status': 'WARN', 'message': 'No stocks configured'}
            
        # Generate signals
        signals_df = self.signal_gen.generate_combined_signal(stocks[:10])
        
        if signals_df is None or signals_df.empty:
            return {'status': 'INFO', 'message': 'No signals generated'}
            
        # Get current prices from DB
        current_prices = {}
        for _, row in signals_df.iterrows():
            current_prices[row['code']] = row['close']
            
        # Check risk
        risk_status = self.risk_mgr.check_portfolio_risk(self.get_portfolio_value())
        if risk_status.get('trade_halt'):
            return {'status': 'HALT', 'message': risk_status.get('halt_reason')}
            
        # Execute trades for top signals
        trades_today = []
        for _, row in signals_df.head(5).iterrows():
            code = row['code']
            price = row['close']
            score = row['combined_score']
            
            # Generate order
            order = self.risk_mgr.generate_order(code, price, score)
            
            if not order.get('rejected') and order.get('action') == 'BUY':
                cost = order['shares'] * price
                if cost <= self.cash:
                    # Execute
                    self.cash -= cost
                    self.positions[code] = {
                        'shares': order['shares'],
                        'avg_cost': price,
                        'entry_date': date,
                        'stop_loss': order.get('stop_loss', price * 0.92),
                        'take_profit': order.get('take_profit', price * 1.20)
                    }
                    trades_today.append({
                        'code': code,
                        'action': 'BUY',
                        'shares': order['shares'],
                        'price': price,
                        'value': cost
                    })
                    self.trade_logger.log_order(
                        code=code, action='BUY', shares=order['shares'],
                        price=price, estimated_value=cost, status='PAPER_FILLED'
                    )
                    
        return {
            'status': 'OK',
            'date': date,
            'trades': trades_today,
            'portfolio_value': self.get_portfolio_value(),
            'cash': self.cash,
            'positions': len(self.positions)
        }
        
    def get_portfolio_value(self) -> float:
        """Calculate current portfolio value."""
        positions_value = 0
        for code, pos in self.positions.items():
            # Use latest close price
            try:
                import pandas as pd
                df = pd.read_sql(
                    f"SELECT close_price FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 1",
                    self.engine
                )
                if not df.empty:
                    positions_value += pos['shares'] * df.iloc[0]['close_price']
            except:
                positions_value += pos['shares'] * pos['avg_cost']
                
        return self.cash + positions_value
        
    def get_pnl(self) -> Dict:
        """Get P&L summary."""
        total = self.get_portfolio_value()
        pnl = total - self.initial_capital
        pnl_pct = pnl / self.initial_capital
        
        return {
            'initial_capital': self.initial_capital,
            'current_value': total,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'cash': self.cash,
            'positions': len(self.positions)
        }
        
    def get_positions_summary(self) -> str:
        """Get positions summary."""
        if not self.positions:
            return "No positions."
            
        lines = ["📊 持仓明细", "-" * 50]
        for code, pos in self.positions.items():
            lines.append(f"  {code}: {pos['shares']}股 @ ¥{pos['avg_cost']:.2f}")
            lines.append(f"    止损: ¥{pos['stop_loss']:.2f} | 止盈: ¥{pos['take_profit']:.2f}")
            
        pnl = self.get_pnl()
        lines.append(f"\n💰 总盈亏: ¥{pnl['pnl']:,.2f} ({pnl['pnl_pct']:+.2f}%)")
        
        return "\n".join(lines)


if __name__ == "__main__":
    trader = PaperTrader(initial_capital=1000000)
    result = trader.run_daily()
    print(result)
    print(trader.get_positions_summary())
