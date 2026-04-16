"""
Backtest Runner
Run and compare multiple strategies on historical data.
"""

import os
import sys
import yaml
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine
from src.backtest.engine import SQLDataFeed, prepare_data

class BacktestRunner:
    """
    Run backtests on multiple stocks and strategies.
    """
    
    def __init__(self):
        self.engine = get_db_engine()
        
    def run_single(self, code: str, strategy_cls, cash: float = 100000, 
                   start_date: str = '2025-01-01') -> Dict:
        """Run backtest for single stock."""
        import backtrader as bt
        
        df = prepare_data(self.engine, code, start_date, datetime.now().strftime('%Y-%m-%d'))
        if df.empty:
            return {'code': code, 'error': 'No data'}
            
        cerebro = bt.Cerebro()
        cerebro.adddata(SQLDataFeed(dataname=df))
        cerebro.addstrategy(strategy_cls)
        cerebro.broker.setcash(cash)
        cerebro.broker.setcommission(commission=0.001)
        
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        print(f"🚀 Backtesting {code}...")
        results = cerebro.run()
        strat = results[0]
        
        final_value = cerebro.broker.getvalue()
        
        sharpe = strat.analyzers.sharpe.get_analysis()
        dd = strat.analyzers.drawdown.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        
        total_trades = trades.get('total', {}).get('total', 0) if trades else 0
        won = trades.get('won', {}).get('total', 0) if trades else 0
        
        return {
            'code': code,
            'start_date': start_date,
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'initial_capital': cash,
            'final_value': final_value,
            'total_return': (final_value - cash) / cash,
            'sharpe_ratio': float(sharpe.get('sharperatio', 0) or 0),
            'max_drawdown': dd.get('max', {}).get('drawdown', 0) / 100 if dd.get('max') else 0,
            'total_trades': total_trades,
            'win_rate': won / total_trades if total_trades > 0 else 0
        }
        
    def run_batch(self, codes: List[str], strategy_cls, cash: float = 100000, 
                  start_date: str = '2025-01-01') -> pd.DataFrame:
        """Run backtests on multiple stocks."""
        results = []
        for code in codes:
            try:
                r = self.run_single(code, strategy_cls, cash, start_date)
                results.append(r)
            except Exception as e:
                print(f"❌ {code}: {e}")
                
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values('total_return', ascending=False).reset_index(drop=True)
        return df
        
    def generate_report(self, df: pd.DataFrame) -> str:
        """Generate comparison report."""
        if df is None or df.empty:
            return "No backtest results."
            
        lines = ["=" * 50, "📊 Backtest Comparison Report", "=" * 50]
        
        avg_ret = df['total_return'].mean()
        avg_sharpe = df['sharpe_ratio'].mean()
        avg_dd = df['max_drawdown'].mean()
        
        lines.append(f"\n📈 Summary")
        lines.append(f"  Avg Return: {avg_ret:.2%}")
        lines.append(f"  Avg Sharpe: {avg_sharpe:.2f}")
        lines.append(f"  Avg MaxDD: {avg_dd:.2%}")
        
        lines.append(f"\n🏆 Top 5")
        for _, row in df.head(5).iterrows():
            lines.append(f"  {row['code']}: {row['total_return']:.2%} | Sharpe: {row['sharpe_ratio']:.2f}")
            
        return "\n".join(lines)
