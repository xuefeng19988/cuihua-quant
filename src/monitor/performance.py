"""
Performance Analytics Module (Merged)
Combines: PerformanceAnalyzer, StrategyPerformanceAnalyzer, PerformanceDashboard
Calculates key trading metrics: Sharpe ratio, max drawdown, win rate, etc.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


# ============================================================================
# PerformanceAnalyzer - basic trading metrics
# ============================================================================

class PerformanceAnalyzer:
    """
    Analyzes trading performance from equity curve or trade log.
    """

    def __init__(self):
        self.trades = []
        self.equity_curve = None

    def load_trades(self, trades: List[Dict]):
        """Load trade log."""
        self.trades = trades

    def load_equity_curve(self, df: pd.DataFrame):
        """Load equity curve DataFrame. Expected columns: ['date', 'equity']."""
        self.equity_curve = df.copy()
        self.equity_curve['date'] = pd.to_datetime(self.equity_curve['date'])
        self.equity_curve = self.equity_curve.sort_values('date').reset_index(drop=True)

    def calculate_returns(self) -> pd.Series:
        """Calculate daily returns from equity curve."""
        if self.equity_curve is None:
            raise ValueError("No equity curve loaded.")
        return self.equity_curve['equity'].pct_change().dropna()

    def total_return(self) -> float:
        if self.equity_curve is None or len(self.equity_curve) < 2:
            return 0.0
        start = self.equity_curve['equity'].iloc[0]
        end = self.equity_curve['equity'].iloc[-1]
        return (end - start) / start

    def annualized_return(self) -> float:
        total = self.total_return()
        if len(self.equity_curve) < 2:
            return 0.0
        days = (self.equity_curve['date'].iloc[-1] - self.equity_curve['date'].iloc[0]).days
        years = days / 365.0
        if years <= 0:
            return 0.0
        return (1 + total) ** (1 / years) - 1

    def volatility(self) -> float:
        returns = self.calculate_returns()
        daily_vol = returns.std()
        return daily_vol * np.sqrt(252)

    def sharpe_ratio(self, risk_free_rate: float = 0.03) -> float:
        vol = self.volatility()
        if vol == 0:
            return 0.0
        ann_return = self.annualized_return()
        return (ann_return - risk_free_rate) / vol

    def sortino_ratio(self, risk_free_rate: float = 0.03) -> float:
        returns = self.calculate_returns()
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return 0.0
        downside_dev = downside_returns.std() * np.sqrt(252)
        if downside_dev == 0:
            return 0.0
        ann_return = self.annualized_return()
        return (ann_return - risk_free_rate) / downside_dev

    def max_drawdown(self) -> float:
        if self.equity_curve is None:
            return 0.0
        equity = self.equity_curve['equity']
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        return drawdown.min()

    def calmar_ratio(self) -> float:
        mdd = abs(self.max_drawdown())
        if mdd == 0:
            return 0.0
        return self.annualized_return() / mdd

    def win_rate(self) -> float:
        if not self.trades:
            return 0.0
        wins = sum(1 for t in self.trades if t.get('pnl', 0) > 0)
        return wins / len(self.trades)

    def profit_factor(self) -> float:
        if not self.trades:
            return 0.0
        gross_profit = sum(t.get('pnl', 0) for t in self.trades if t.get('pnl', 0) > 0)
        gross_loss = abs(sum(t.get('pnl', 0) for t in self.trades if t.get('pnl', 0) < 0))
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        return gross_profit / gross_loss

    def avg_win_loss_ratio(self) -> float:
        if not self.trades:
            return 0.0
        wins = [t.get('pnl', 0) for t in self.trades if t.get('pnl', 0) > 0]
        losses = [t.get('pnl', 0) for t in self.trades if t.get('pnl', 0) < 0]
        avg_win = np.mean(wins) if wins else 0
        avg_loss = abs(np.mean(losses)) if losses else 0
        if avg_loss == 0:
            return 0.0
        return avg_win / avg_loss

    def get_summary(self) -> Dict:
        summary = {
            'total_return': self.total_return(),
            'annualized_return': self.annualized_return(),
            'volatility': self.volatility(),
            'sharpe_ratio': self.sharpe_ratio(),
            'sortino_ratio': self.sortino_ratio(),
            'max_drawdown': self.max_drawdown(),
            'calmar_ratio': self.calmar_ratio(),
            'win_rate': self.win_rate(),
            'profit_factor': self.profit_factor(),
            'avg_win_loss_ratio': self.avg_win_loss_ratio(),
            'num_trades': len(self.trades)
        }
        if self.equity_curve is not None:
            summary['start_date'] = self.equity_curve['date'].iloc[0].strftime('%Y-%m-%d')
            summary['end_date'] = self.equity_curve['date'].iloc[-1].strftime('%Y-%m-%d')
            summary['trading_days'] = len(self.equity_curve)
        return summary

    def print_report(self):
        summary = self.get_summary()
        print("\n" + "=" * 50)
        print("📊 Performance Report")
        print("=" * 50)
        if 'start_date' in summary:
            print(f"📅 Period: {summary['start_date']} to {summary['end_date']} ({summary['trading_days']} days)")
        print(f"💰 Total Return: {summary['total_return']:.2%}")
        print(f"📈 Annualized Return: {summary['annualized_return']:.2%}")
        print(f"📉 Volatility: {summary['volatility']:.2%}")
        print(f"🏆 Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
        print(f"🎯 Sortino Ratio: {summary['sortino_ratio']:.2f}")
        print(f"📉 Max Drawdown: {summary['max_drawdown']:.2%}")
        print(f"📊 Calmar Ratio: {summary['calmar_ratio']:.2f}")
        print(f"✅ Win Rate: {summary['win_rate']:.2%}")
        print(f"💵 Profit Factor: {summary['profit_factor']:.2f}")
        print(f"📊 Avg Win/Loss: {summary['avg_win_loss_ratio']:.2f}")
        print(f"🔢 Total Trades: {summary['num_trades']}")
        print("=" * 50)


# ============================================================================
# StrategyPerformanceAnalyzer - comprehensive strategy analysis
# ============================================================================

class StrategyPerformanceAnalyzer:
    """
    Comprehensive strategy performance analysis and attribution.
    """

    def __init__(self):
        pass

    def analyze_strategy(self, equity_curve: pd.Series, trades: List[Dict] = None,
                        benchmark: pd.Series = None) -> Dict:
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
        volatility = returns.std() * np.sqrt(252)
        downside = returns[returns < 0].std() * np.sqrt(252)
        equity = (1 + returns).cumprod()
        peak = equity.cummax()
        drawdown = (equity - peak) / peak
        max_dd = drawdown.min()
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
        if returns.empty:
            return pd.DataFrame()
        return returns.resample('M').apply(lambda x: (1 + x).prod() - 1)

    def _rolling_metrics(self, returns: pd.Series, window: int = 60) -> Dict:
        rolling_sharpe = returns.rolling(window).mean() / returns.rolling(window).std() * np.sqrt(252)
        rolling_vol = returns.rolling(window).std() * np.sqrt(252)
        return {
            'rolling_sharpe': rolling_sharpe.dropna(),
            'rolling_volatility': rolling_vol.dropna(),
        }

    def _relative_analysis(self, strategy_returns: pd.Series,
                          benchmark_returns: pd.Series) -> Dict:
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
        lines = ["=" * 60, "📊 策略绩效分析报告", "=" * 60]
        basic = analysis.get('basic_metrics', {})
        lines.append(f"\n📈 基本指标")
        lines.append(f"  总收益: {basic.get('total_return', 0):.2%}")
        lines.append(f"  年化收益: {basic.get('annualized_return', 0):.2%}")
        lines.append(f"  交易天数: {basic.get('trading_days', 0)}")
        risk = analysis.get('risk_metrics', {})
        lines.append(f"\n🛡️  风险指标")
        lines.append(f"  波动率: {risk.get('volatility', 0):.2%}")
        lines.append(f"  夏普比率: {risk.get('sharpe_ratio', 0):.2f}")
        lines.append(f"  最大回撤: {risk.get('max_drawdown', 0):.2%}")
        trades = analysis.get('trade_analysis', {})
        if trades:
            lines.append(f"\n💼 交易分析")
            lines.append(f"  总交易: {trades.get('total_trades', 0)}")
            lines.append(f"  胜率: {trades.get('win_rate', 0):.1%}")
            lines.append(f"  盈亏比: {abs(trades.get('avg_win', 0) / trades.get('avg_loss', 1)):.2f}")
        return "\n".join(lines)


# ============================================================================
# PerformanceDashboard - text-based performance dashboard
# ============================================================================

class PerformanceDashboard:
    """
    Generates text-based performance dashboard with key metrics.
    """

    def __init__(self):
        from src.data.trade_logger import TradeLogger
        from src.data.database import get_db_engine
        from src.core.utils import load_stock_names
        self.logger = TradeLogger()
        self.engine = get_db_engine()
        self._load_stock_names = load_stock_names

    def generate_dashboard(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("📊 翠花量化 - 绩效看板")
        lines.append(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 60)

        summary = self.logger.get_summary()
        lines.append("\n📈 总览")
        lines.append(f"  总信号数: {summary['total_signals']}")
        lines.append(f"  总订单数: {summary['total_orders']}")
        lines.append(f"  已平仓: {summary['closed_trades']}")
        lines.append(f"  胜率: {summary['win_rate']:.1%}")
        lines.append(f"  总盈亏: ¥{summary['total_pnl']:,.2f}")

        pnl_hist = self.logger.get_pnl_history(days=30)
        if pnl_hist:
            lines.append("\n💰 近 30 日盈亏趋势")
            total = sum(p['daily_pnl'] for p in pnl_hist)
            avg = total / len(pnl_hist)
            best = max(pnl_hist, key=lambda x: x['daily_pnl'])
            worst = min(pnl_hist, key=lambda x: x['daily_pnl'])
            lines.append(f"  累计盈亏: ¥{total:,.2f}")
            lines.append(f"  日均盈亏: ¥{avg:,.2f}")
            lines.append(f"  最佳: {best['date']} (¥{best['daily_pnl']:,.2f})")
            lines.append(f"  最差: {worst['date']} (¥{worst['daily_pnl']:,.2f})")
            lines.append("\n  📊 盈亏分布")
            max_val = max(abs(p['daily_pnl']) for p in pnl_hist) if pnl_hist else 1
            if max_val == 0:
                max_val = 1
            for p in pnl_hist[-10:]:
                bar_len = int(abs(p['daily_pnl']) / max_val * 20)
                bar = "█" * bar_len
                icon = "🔺" if p['daily_pnl'] >= 0 else "🔻"
                lines.append(f"  {p['date'][-5:]} {icon} {bar} ¥{p['daily_pnl']:,.0f}")

        recent_signals = self.logger.get_recent_signals(limit=10)
        if recent_signals:
            lines.append("\n🧠 最近信号")
            for sig in recent_signals[:5]:
                icon = "🔺" if sig['direction'] == 'BUY' else "🔻"
                lines.append(f"  {icon} {sig['code']} | {sig['direction']} | Score: {sig['score']:.3f} | {sig['strategy']}")

        lines.append("\n📊 数据覆盖")
        stock_names = self._load_stock_names()
        try:
            df = pd.read_sql("SELECT code, COUNT(*) as cnt, MAX(date) as last FROM stock_daily GROUP BY code", self.engine)
            if not df.empty:
                lines.append(f"  股票数: {len(df)}")
                lines.append(f"  总记录: {df['cnt'].sum()}")
                lines.append(f"  平均记录: {df['cnt'].mean():.0f}")
                lines.append(f"  最新数据: {df['last'].max()}")
                lines.append("\n  股票列表:")
                for _, row in df.iterrows():
                    name = stock_names.get(row['code'], '')
                    label = f"{row['code']} {name}".strip() if name else row['code']
                    lines.append(f"    {label}: {row['cnt']} 条")
        except Exception:
            lines.append("  无法查询数据库")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def generate_stock_report(self, code: str) -> str:
        stock_names = self._load_stock_names()
        name = stock_names.get(code, '')
        label = f"{code} {name}".strip() if name else code
        lines = [f"📊 {label} 分析报告", "-" * 40]
        try:
            df = pd.read_sql(
f"SELECT * FROM stock_daily WHERE code=:code ORDER BY date DESC LIMIT 30",
                self.engine
            )
            if df.empty:
                return f"⚠️ 无 {code} 数据"
            df = df.sort_values('date')
            close = df['close_price']
            lines.append(f"  记录数: {len(df)}")
            lines.append(f"  日期范围: {df['date'].iloc[0]} ~ {df['date'].iloc[-1]}")
            lines.append(f"  最新价: ¥{close.iloc[-1]:.2f}")
            lines.append(f"  最高: ¥{close.max():.2f}")
            lines.append(f"  最低: ¥{close.min():.2f}")
            ret = close.pct_change().dropna()
            lines.append(f"  日均收益: {ret.mean():.2%}")
            lines.append(f"  日波动率: {ret.std():.2%}")
            lines.append(f"  年化波动: {ret.std() * np.sqrt(252):.2%}")
            peak = close.cummax()
            dd = (close - peak) / peak
            lines.append(f"  最大回撤: {dd.min():.2%}")
        except Exception as e:
            lines.append(f"⚠️ 查询失败: {e}")
        return "\n".join(lines)
