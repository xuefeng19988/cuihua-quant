"""
Phase 8: Paper Trading Simulator
Real-time paper trading with full pipeline integration.
"""

import os
import sys
import yaml
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.futu_sync import FutuSync
from src.data.database import get_db_engine
from src.analysis.signal_gen import SignalGenerator
from src.execution.risk_control import RiskManager
from src.data.trade_logger import TradeLogger

class PaperTradingSimulator:
    """
    Full paper trading simulator for Phase 8.
    Runs daily with real market data, simulates orders, tracks P&L.
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
        self.daily_pnl: List[Dict] = []
        self.start_date = datetime.now().strftime('%Y-%m-%d')
        
        # Components
        self.engine = get_db_engine()
        self.signal_gen = SignalGenerator()
        self.risk_mgr = RiskManager(self.configs.get('risk', {}))
        self.trade_logger = TradeLogger()
        
        # State file for persistence
        self.state_file = os.path.join(project_root, 'data', 'paper_trading_state.json')
        self._load_state()
        
    def _load_state(self):
        """Load previous state if exists."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                self.cash = state.get('cash', self.initial_capital)
                self.positions = state.get('positions', {})
                self.trade_history = state.get('trade_history', [])
                self.start_date = state.get('start_date', self.start_date)
                self.daily_pnl = state.get('daily_pnl', [])
            except Exception as e:
                pass
                
    def _save_state(self):
        """Save current state."""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        state = {
            'cash': self.cash,
            'positions': self.positions,
            'trade_history': self.trade_history,
            'start_date': self.start_date,
            'daily_pnl': self.daily_pnl,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)
            
    def run_daily(self, date: str = None) -> Dict:
        """
        Execute one day of paper trading.
        1. Sync data
        2. Generate signals
        3. Check existing positions
        4. Execute trades
        5. Update P&L
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        print("=" * 60)
        print(f"📊 Paper Trading Day: {date}")
        print("=" * 60)
        
        # 1. Sync data
        print("\n📥 Step 1: Syncing Data...")
        self._sync_data()
        
        # 2. Generate signals
        print("\n🧠 Step 2: Generating Signals...")
        signals_df = self._generate_signals()
        
        if signals_df is None or signals_df.empty:
            print("⚠️ No signals generated.")
            return {'status': 'NO_SIGNALS'}
            
        # 3. Get current prices
        current_prices = dict(zip(signals_df['code'], signals_df['close']))
        
        # 4. Check existing positions for stop-loss/take-profit
        print("\n🛡️ Step 3: Checking Positions...")
        self._check_positions(current_prices, date)
        
        # 5. Execute new trades
        print("\n💰 Step 4: Executing Trades...")
        trades_today = self._execute_trades(signals_df, current_prices, date)
        
        # 6. Update daily P&L
        print("\n📊 Step 5: Updating P&L...")
        daily_result = self._update_daily_pnl(current_prices, date, trades_today)
        
        # 7. Save state
        self._save_state()
        
        # 8. Log
        self._log_daily_result(daily_result)
        
        print("\n" + "=" * 60)
        print(f"✅ Day Complete: {date}")
        print(f"💰 Portfolio: ¥{daily_result['portfolio_value']:,.2f}")
        print(f"📈 Daily P&L: ¥{daily_result['daily_pnl']:,.2f} ({daily_result['daily_pnl_pct']:+.2f}%)")
        print(f"📊 Trades: {len(trades_today)}")
        print("=" * 60)
        
        return daily_result
        
    def _sync_data(self):
        """Sync market data."""
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        if not stocks:
            return
            
        syncer = FutuSync()
        if syncer.connect():
            syncer.run(pool_name='watchlist', days_back=5)
            syncer.close()
            
    def _generate_signals(self):
        """Generate trading signals."""
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        if not stocks:
            return None
        return self.signal_gen.generate_combined_signal(stocks)
        
    def _check_positions(self, current_prices: Dict, date: str):
        """Check existing positions for stop-loss/take-profit."""
        to_close = []
        for code, pos in self.positions.items():
            price = current_prices.get(code)
            if not price:
                continue
                
            pnl_pct = (price - pos['avg_cost']) / pos['avg_cost']
            
            # Stop-loss check
            if pnl_pct <= -self.risk_mgr.stop_loss_pct:
                print(f"  🛑 {code} STOP-LOSS: {pnl_pct:.1%}")
                to_close.append(code)
                
            # Take-profit check
            elif pnl_pct >= self.risk_mgr.take_profit_pct:
                print(f"  🎯 {code} TAKE-PROFIT: {pnl_pct:.1%}")
                to_close.append(code)
                
        # Close positions
        for code in to_close:
            self._close_position(code, current_prices[code], date)
            
    def _execute_trades(self, signals_df, current_prices, date):
        """Execute trades based on signals."""
        trades = []
        
        # Top 5 signals
        for _, row in signals_df.head(5).iterrows():
            code = row['code']
            price = row['close']
            score = row['combined_score']
            
            # Skip if already holding
            if code in self.positions:
                continue
                
            # Generate order via risk manager
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
                        'stop_loss': price * (1 - self.risk_mgr.stop_loss_pct),
                        'take_profit': price * (1 + self.risk_mgr.take_profit_pct)
                    }
                    trades.append({
                        'code': code,
                        'action': 'BUY',
                        'shares': order['shares'],
                        'price': price,
                        'value': cost,
                        'date': date
                    })
                    self.trade_logger.log_order(
                        code=code, action='BUY', shares=order['shares'],
                        price=price, estimated_value=cost, status='PAPER_FILLED'
                    )
                    print(f"  ✅ BUY {code} {order['shares']} @ {price}")
                    
        return trades
        
    def _close_position(self, code: str, price: float, date: str):
        """Close a position."""
        if code not in self.positions:
            return
            
        pos = self.positions[code]
        proceed = pos['shares'] * price
        pnl = proceed - (pos['shares'] * pos['avg_cost'])
        pnl_pct = (price - pos['avg_cost']) / pos['avg_cost']
        
        self.cash += proceed
        del self.positions[code]
        
        self.trade_history.append({
            'code': code,
            'action': 'SELL',
            'shares': pos['shares'],
            'entry_price': pos['avg_cost'],
            'exit_price': price,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'entry_date': pos['entry_date'],
            'exit_date': date
        })
        self.trade_logger.log_order(
            code=code, action='SELL', shares=pos['shares'],
            price=price, estimated_value=proceed, status='PAPER_CLOSED',
            notes=f"PnL: {pnl:.2f} ({pnl_pct:.1%})"
        )
        print(f"  📤 SELL {code} {pos['shares']} @ {price} (PnL: {pnl:.2f})")
        
    def _update_daily_pnl(self, current_prices, date, trades):
        """Update daily P&L."""
        # Calculate portfolio value
        positions_value = 0
        for code, pos in self.positions.items():
            price = current_prices.get(code, pos['avg_cost'])
            positions_value += pos['shares'] * price
            
        portfolio_value = self.cash + positions_value
        
        # Calculate daily P&L
        if self.daily_pnl:
            prev_value = self.daily_pnl[-1]['portfolio_value']
        else:
            prev_value = self.initial_capital
            
        daily_pnl = portfolio_value - prev_value
        daily_pnl_pct = daily_pnl / prev_value if prev_value > 0 else 0
        
        result = {
            'date': date,
            'portfolio_value': portfolio_value,
            'cash': self.cash,
            'positions_value': positions_value,
            'daily_pnl': daily_pnl,
            'daily_pnl_pct': daily_pnl_pct,
            'num_positions': len(self.positions),
            'trades_count': len(trades),
            'total_trades': len(self.trade_history)
        }
        
        self.daily_pnl.append(result)
        self.trade_logger.log_daily_pnl(
            date=date,
            total_value=portfolio_value,
            cash=self.cash,
            market_value=positions_value,
            daily_pnl=daily_pnl,
            daily_pnl_pct=daily_pnl_pct,
            num_positions=len(self.positions),
            num_trades=len(trades)
        )
        
        return result
        
    def _log_daily_result(self, result):
        """Log daily result."""
        print(f"\n📊 Daily Summary:")
        print(f"  Portfolio: ¥{result['portfolio_value']:,.2f}")
        print(f"  Daily P&L: ¥{result['daily_pnl']:,.2f} ({result['daily_pnl_pct']:+.2f}%)")
        print(f"  Positions: {result['num_positions']}")
        print(f"  Trades: {result['trades_count']}")
        
    def get_summary(self) -> Dict:
        """Get full paper trading summary."""
        if not self.daily_pnl:
            return {'status': 'NO_DATA'}
            
        total_pnl = self.daily_pnl[-1]['portfolio_value'] - self.initial_capital
        total_pnl_pct = total_pnl / self.initial_capital
        
        wins = sum(1 for d in self.daily_pnl if d['daily_pnl'] > 0)
        losses = sum(1 for d in self.daily_pnl if d['daily_pnl'] < 0)
        
        return {
            'start_date': self.start_date,
            'days': len(self.daily_pnl),
            'initial_capital': self.initial_capital,
            'current_value': self.daily_pnl[-1]['portfolio_value'],
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'daily_pnl_avg': sum(d['daily_pnl'] for d in self.daily_pnl) / len(self.daily_pnl),
            'win_days': wins,
            'loss_days': losses,
            'win_rate': wins / len(self.daily_pnl) if self.daily_pnl else 0,
            'total_trades': len(self.trade_history),
            'current_positions': len(self.positions)
        }
        
    def generate_report(self) -> str:
        """Generate paper trading report."""
        summary = self.get_summary()
        
        lines = []
        lines.append("=" * 60)
        lines.append("📊 翠花量化 - 模拟盘报告")
        lines.append("=" * 60)
        
        lines.append(f"\n📅 运行时间: {summary.get('start_date', 'N/A')} 至今")
        lines.append(f"📆 交易天数: {summary.get('days', 0)}")
        
        lines.append(f"\n💰 资金情况")
        lines.append(f"  初始资金: ¥{summary.get('initial_capital', 0):,.2f}")
        lines.append(f"  当前净值: ¥{summary.get('current_value', 0):,.2f}")
        lines.append(f"  总盈亏: ¥{summary.get('total_pnl', 0):,.2f} ({summary.get('total_pnl_pct', 0):+.2f}%)")
        lines.append(f"  日均盈亏: ¥{summary.get('daily_pnl_avg', 0):,.2f}")
        
        lines.append(f"\n📈 胜率统计")
        lines.append(f"  盈利天数: {summary.get('win_days', 0)}")
        lines.append(f"  亏损天数: {summary.get('loss_days', 0)}")
        lines.append(f"  胜率: {summary.get('win_rate', 0):.1%}")
        
        lines.append(f"\n📊 交易统计")
        lines.append(f"  总交易次数: {summary.get('total_trades', 0)}")
        lines.append(f"  当前持仓: {summary.get('current_positions', 0)}")
        
        if self.trade_history:
            lines.append(f"\n📋 最近交易")
            for trade in self.trade_history[-5:]:
                icon = "🔺" if trade['pnl'] > 0 else "🔻"
                lines.append(f"  {icon} {trade['code']}: {trade['pnl']:+,.2f} ({trade['pnl_pct']:+.1%})")
                
        lines.append("=" * 60)
        return "\n".join(lines)


if __name__ == "__main__":
    sim = PaperTradingSimulator(initial_capital=1000000)
    result = sim.run_daily()
    print(sim.generate_report())
