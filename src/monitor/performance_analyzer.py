"""
Phase 41: Strategy Performance Analyzer
Comprehensive strategy performance analysis and attribution.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class StrategyPerformanceAnalyzer:
    """
    Comprehensive strategy performance analysis.
    """
    
    def __init__(self):
        pass
        
    def analyze_strategy(self, equity_curve: pd.Series, trades: List[Dict] = None,
                        benchmark: pd.Series = None) -> Dict:
        """
        Comprehensive strategy analysis.
        
        Args:
            equity_curve: Strategy equity curve
            trades: List of trade records
            benchmark: Benchmark equity curve
            
        Returns:
            Analysis results
        """
        returns = equity_curve.pct_change().dropna()
        
        results = {
            'basic_metrics': self._basic_metrics(returns),
            'risk_metrics': self._risk_metrics(returns),
            'trade_analysis': self._analyze_trades(trades) if trades else {},
            'monthly_returns': self._monthly_returns(returns),
            'rolling_metrics': self._rolling_metrics(returns),
        }
        
        if benchmark is not None:
            results['relative_analysis'] = self._relative_analysis(returns, benchmark)
            
        return results
        
    def _basic_metrics(self, returns: pd.Series) -> Dict:
        """Calculate basic performance metrics."""
        total_return = (1 + returns).prod() - 1
        years = len(returns) / 252
        annualized = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized,
            'trading_days': len(returns),
            'years': years,
            'avg_daily_return': returns.mean(),
            'best_day': returns.max(),
            'worst_day': returns.min(),
        }
        
    def _risk_metrics(self, returns: pd.Series) -> Dict:
        """Calculate risk metrics."""
        volatility = returns.std() * np.sqrt(252)
        downside = returns[returns < 0].std() * np.sqrt(252)
        
        # Max drawdown
        equity = (1 + returns).cumprod()
        peak = equity.cummax()
        drawdown = (equity - peak) / peak
        max_dd = drawdown.min()
        
        # VaR
        var_95 = np.percentile(returns, 5)
        cvar_95 = returns[returns <= var_95].mean()
        
        return {
            'volatility': volatility,
            'downside_deviation': downside,
            'max_drawdown': max_dd,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'sharpe_ratio': (returns.mean() * 252 - 0.02) / volatility if volatility > 0 else 0,
            'sortino_ratio': (returns.mean() * 252 - 0.02) / downside if downside > 0 else 0,
            'calmar_ratio': (returns.mean() * 252) / abs(max_dd) if max_dd != 0 else 0,
        }
        
    def _analyze_trades(self, trades: List[Dict]) -> Dict:
        """Analyze trade statistics."""
        if not trades:
            return {}
            
        pnls = [t.get('pnl', 0) for t in trades]
        pnls = pd.Series(pnls)
        
        wins = pnls[pnls > 0]
        losses = pnls[pnls <= 0]
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': len(wins) / len(trades) if trades else 0,
            'avg_win': wins.mean() if len(wins) > 0 else 0,
            'avg_loss': losses.mean() if len(losses) > 0 else 0,
            'profit_factor': wins.sum() / abs(losses.sum()) if len(losses) > 0 and losses.sum() != 0 else 0,
            'avg_pnl': pnls.mean(),
            'best_trade': pnls.max(),
            'worst_trade': pnls.min(),
            'avg_holding_period': np.mean([t.get('holding_days', 0) for t in trades]) if trades else 0,
        }
        
    def _monthly_returns(self, returns: pd.Series) -> pd.DataFrame:
        """Calculate monthly returns."""
        if returns.empty:
            return pd.DataFrame()
            
        monthly = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
        return monthly
        
    def _rolling_metrics(self, returns: pd.Series, window: int = 60) -> Dict:
        """Calculate rolling metrics."""
        rolling_sharpe = returns.rolling(window).mean() / returns.rolling(window).std() * np.sqrt(252)
        rolling_vol = returns.rolling(window).std() * np.sqrt(252)
        
        return {
            'rolling_sharpe': rolling_sharpe.dropna(),
            'rolling_volatility': rolling_vol.dropna(),
        }
        
    def _relative_analysis(self, strategy_returns: pd.Series, 
                          benchmark_returns: pd.Series) -> Dict:
        """Analyze strategy relative to benchmark."""
        excess_returns = strategy_returns - benchmark_returns
        
        beta = strategy_returns.cov(benchmark_returns) / benchmark_returns.var() if benchmark_returns.var() > 0 else 0
        alpha = excess_returns.mean() * 252
        tracking_error = excess_returns.std() * np.sqrt(252)
        information_ratio = alpha / tracking_error if tracking_error > 0 else 0
        
        return {
            'alpha': alpha,
            'beta': beta,
            'tracking_error': tracking_error,
            'information_ratio': information_ratio,
            'up_capture': self._capture_ratio(strategy_returns, benchmark_returns, True),
            'down_capture': self._capture_ratio(strategy_returns, benchmark_returns, False),
        }
        
    def _capture_ratio(self, strategy: pd.Series, benchmark: pd.Series, 
                      up_market: bool) -> float:
        """Calculate up/down market capture ratio."""
        if up_market:
            up_days = benchmark > 0
        else:
            up_days = benchmark < 0
            
        if up_days.sum() == 0:
            return 0
            
        strategy_avg = strategy[up_days].mean()
        benchmark_avg = benchmark[up_days].mean()
        
        return strategy_avg / benchmark_avg if benchmark_avg != 0 else 0
        
    def generate_report(self, analysis: Dict) -> str:
        """Generate comprehensive performance report."""
        lines = []
        lines.append("=" * 60)
        lines.append("📊 策略绩效分析报告")
        lines.append("=" * 60)
        
        # Basic metrics
        basic = analysis.get('basic_metrics', {})
        lines.append(f"\n📈 基本指标")
        lines.append(f"  总收益: {basic.get('total_return', 0):.2%}")
        lines.append(f"  年化收益: {basic.get('annualized_return', 0):.2%}")
        lines.append(f"  交易天数: {basic.get('trading_days', 0)}")
        
        # Risk metrics
        risk = analysis.get('risk_metrics', {})
        lines.append(f"\n🛡️  风险指标")
        lines.append(f"  波动率: {risk.get('volatility', 0):.2%}")
        lines.append(f"  夏普比率: {risk.get('sharpe_ratio', 0):.2f}")
        lines.append(f"  最大回撤: {risk.get('max_drawdown', 0):.2%}")
        
        # Trade analysis
        trades = analysis.get('trade_analysis', {})
        if trades:
            lines.append(f"\n💼 交易分析")
            lines.append(f"  总交易: {trades.get('total_trades', 0)}")
            lines.append(f"  胜率: {trades.get('win_rate', 0):.1%}")
            lines.append(f"  盈亏比: {abs(trades.get('avg_win', 0) / trades.get('avg_loss', 1)):.2f}")
            
        return "\n".join(lines)


if __name__ == "__main__":
    # Test with mock data
    np.random.seed(42)
    days = 500
    returns = pd.Series(np.random.normal(0.0005, 0.015, days), 
                       index=pd.date_range('2024-01-01', periods=days, freq='B'))
    equity = (1 + returns).cumprod() * 1000000
    
    trades = [
        {'pnl': 5000, 'holding_days': 5},
        {'pnl': -2000, 'holding_days': 3},
        {'pnl': 8000, 'holding_days': 10},
        {'pnl': 3000, 'holding_days': 7},
        {'pnl': -1000, 'holding_days': 2},
    ]
    
    analyzer = StrategyPerformanceAnalyzer()
    results = analyzer.analyze_strategy(equity, trades)
    print(analyzer.generate_report(results))
