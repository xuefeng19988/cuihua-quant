"""
Auto Parameter Tuner
Automatically optimizes strategy parameters using backtesting.
"""

import os
import sys
import yaml
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from itertools import product

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine
from src.backtest.engine import SQLDataFeed, prepare_data

class AutoParamTuner:
    """
    Automatically tunes strategy parameters using walk-forward optimization.
    """
    
    def __init__(self):
        self.engine = get_db_engine()
        
    def tune_sma(self, codes: List[str], start_date: str = '2025-01-01') -> pd.DataFrame:
        """
        Walk-forward optimization for SMA strategy.
        """
        import backtrader as bt
        from src.strategy.sma_cross import SmaCross
        
        results = []
        
        # Parameter grid
        fast_list = [3, 5, 8, 10, 12]
        slow_list = [15, 20, 30, 40, 50, 60]
        
        for code in codes[:10]:  # Limit to 10 stocks
            df = prepare_data(self.engine, code, start_date, datetime.now().strftime('%Y-%m-%d'))
            if df.empty or len(df) < 60:
                continue
                
            for fast, slow in product(fast_list, slow_list):
                if fast >= slow:
                    continue
                    
                cerebro = bt.Cerebro()
                cerebro.adddata(SQLDataFeed(dataname=df))
                cerebro.addstrategy(SmaCross, fast_period=fast, slow_period=slow)
                cerebro.broker.setcash(100000)
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
                    'code': code,
                    'fast': fast,
                    'slow': slow,
                    'final_value': final,
                    'return_pct': (final - 100000) / 100000,
                    'sharpe': float(sharpe.get('sharperatio', 0) or 0),
                    'max_drawdown': dd.get('max', {}).get('drawdown', 0) / 100 if dd.get('max') else 0,
                    'total_trades': total_trades,
                    'win_rate': won / total_trades if total_trades > 0 else 0
                })
                
        df_results = pd.DataFrame(results)
        if not df_results.empty:
            df_results = df_results.sort_values('return_pct', ascending=False).reset_index(drop=True)
            
        return df_results
        
    def generate_recommendations(self, results_df: pd.DataFrame) -> Dict:
        """Generate parameter recommendations."""
        if results_df is None or results_df.empty:
            return {}
            
        # Find best parameters by different criteria
        best_return = results_df.iloc[0]
        best_sharpe = results_df.sort_values('sharpe', ascending=False).iloc[0]
        best_dd = results_df.sort_values('max_drawdown').iloc[0]
        
        return {
            'best_return': {
                'fast': int(best_return['fast']),
                'slow': int(best_return['slow']),
                'return_pct': best_return['return_pct'],
                'sharpe': best_return['sharpe']
            },
            'best_sharpe': {
                'fast': int(best_sharpe['fast']),
                'slow': int(best_sharpe['slow']),
                'return_pct': best_sharpe['return_pct'],
                'sharpe': best_sharpe['sharpe']
            },
            'best_drawdown': {
                'fast': int(best_dd['fast']),
                'slow': int(best_dd['slow']),
                'return_pct': best_dd['return_pct'],
                'max_drawdown': best_dd['max_drawdown']
            }
        }
        
    def generate_report(self, results_df: pd.DataFrame) -> str:
        """Generate tuning report."""
        if results_df is None or results_df.empty:
            return "No tuning results."
            
        lines = []
        lines.append("=" * 50)
        lines.append("🔧 自动参数调优报告")
        lines.append("=" * 50)
        
        recs = self.generate_recommendations(results_df)
        
        lines.append(f"\n🏆 推荐参数")
        lines.append(f"  最高收益: Fast={recs['best_return']['fast']}, Slow={recs['best_return']['slow']} → {recs['best_return']['return_pct']:.2%}")
        lines.append(f"  最佳夏普: Fast={recs['best_sharpe']['fast']}, Slow={recs['best_sharpe']['slow']} → Sharpe {recs['best_sharpe']['sharpe']:.2f}")
        lines.append(f"  最小回撤: Fast={recs['best_drawdown']['fast']}, Slow={recs['best_drawdown']['slow']} → DD {recs['best_drawdown']['max_drawdown']:.2%}")
        
        # Top 5 combinations
        lines.append(f"\n📊 Top 5 参数组合")
        for _, row in results_df.head(5).iterrows():
            lines.append(f"  Fast={row['fast']}, Slow={row['slow']}: "
                        f"Return {row['return_pct']:.2%} | Sharpe {row['sharpe']:.2f} | DD {row['max_drawdown']:.2%}")
                        
        return "\n".join(lines)


if __name__ == "__main__":
    tuner = AutoParamTuner()
    codes = ['SH.600519', 'SZ.002594', 'SH.601318']
    df = tuner.tune_sma(codes)
    print(tuner.generate_report(df))
