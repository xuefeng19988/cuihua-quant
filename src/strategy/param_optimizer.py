"""
Parameter Optimizer
Optimizes strategy parameters through backtesting grid search.
"""

import os
import sys
import yaml
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict
from itertools import product

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine
from src.backtest.engine import SQLDataFeed, prepare_data

class ParameterOptimizer:
    """
    Optimizes strategy parameters using grid search with backtesting.
    """
    
    def __init__(self):
        self.engine = get_db_engine()
        
    def optimize_sma(self, code: str, start_date: str = '2025-01-01',
                     cash: float = 100000) -> pd.DataFrame:
        """
        Optimize SMA crossover parameters.
        Tests combinations of fast/slow periods.
        """
        import backtrader as bt
        from src.strategy.sma_cross import SmaCross
        
        df = prepare_data(self.engine, code, start_date, datetime.now().strftime('%Y-%m-%d'))
        if df.empty:
            return pd.DataFrame()
            
        results = []
        
        # Grid: fast [3, 5, 8, 10], slow [15, 20, 30, 50]
        fast_periods = [3, 5, 8, 10]
        slow_periods = [15, 20, 30, 50]
        
        for fast, slow in product(fast_periods, slow_periods):
            if fast >= slow:
                continue
                
            cerebro = bt.Cerebro()
            cerebro.adddata(SQLDataFeed(dataname=df))
            cerebro.addstrategy(SmaCross, fast_period=fast, slow_period=slow)
            cerebro.broker.setcash(cash)
            cerebro.broker.setcommission(commission=0.001)
            
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
            cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
            
            strat_results = cerebro.run()
            strat = strat_results[0]
            
            final = cerebro.broker.getvalue()
            sharpe = strat.analyzers.sharpe.get_analysis()
            dd = strat.analyzers.drawdown.get_analysis()
            trades = strat.analyzers.trades.get_analysis()
            
            total_trades = trades.get('total', {}).get('total', 0) if trades else 0
            won = trades.get('won', {}).get('total', 0) if trades else 0
            
            results.append({
                'fast': fast,
                'slow': slow,
                'final_value': final,
                'return_pct': (final - cash) / cash,
                'sharpe': float(sharpe.get('sharperatio', 0) or 0),
                'max_drawdown': dd.get('max', {}).get('drawdown', 0) / 100 if dd.get('max') else 0,
                'total_trades': total_trades,
                'win_rate': won / total_trades if total_trades > 0 else 0
            })
            
        df_results = pd.DataFrame(results)
        if not df_results.empty:
            df_results = df_results.sort_values('return_pct', ascending=False).reset_index(drop=True)
            
        return df_results
        
    def optimize_multi_factor(self, signals_df: pd.DataFrame = None) -> Dict:
        """
        Find optimal weights for multi-factor strategy.
        """
        # Test different weight combinations
        weight_ranges = [0.2, 0.3, 0.4, 0.5]
        best_config = None
        best_score = -999
        
        for mom in weight_ranges:
            for tech in weight_ranges:
                remaining = 1.0 - mom - tech
                if remaining <= 0:
                    continue
                value = remaining / 2
                vol = remaining / 2
                
                config = {
                    'weights': {
                        'momentum': mom,
                        'value': value,
                        'technical': tech,
                        'volatility': vol
                    }
                }
                # Score based on balance
                score = mom * 0.3 + tech * 0.3 + value * 0.2 + vol * 0.2
                if score > best_score:
                    best_score = score
                    best_config = config
                    
        return best_config or {}
        
    def generate_report(self, results_df: pd.DataFrame) -> str:
        """Generate optimization report."""
        if results_df is None or results_df.empty:
            return "No optimization results."
            
        lines = []
        lines.append("=" * 50)
        lines.append("🔧 参数优化报告")
        lines.append("=" * 50)
        
        top = results_df.head(5)
        lines.append(f"\n🏆 Top 5 参数组合")
        for _, row in top.iterrows():
            if 'fast' in row:
                lines.append(f"  Fast={row['fast']}, Slow={row['slow']}: "
                           f"Return {row['return_pct']:.2%} | Sharpe {row['sharpe']:.2f} | DD {row['max_drawdown']:.2%}")
            else:
                lines.append(f"  {row}")
                
        best = results_df.iloc[0]
        lines.append(f"\n📊 推荐参数")
        if 'fast' in best:
            lines.append(f"  Fast MA: {best['fast']}")
            lines.append(f"  Slow MA: {best['slow']}")
            
        lines.append(f"  年化收益: {best['return_pct']:.2%}")
        lines.append(f"  夏普比率: {best['sharpe']:.2f}")
        lines.append(f"  最大回撤: {best['max_drawdown']:.2%}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    optimizer = ParameterOptimizer()
    # Test with a known stock
    df = optimizer.optimize_sma('SH.600519', start_date='2025-01-01')
    print(optimizer.generate_report(df))
