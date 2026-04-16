"""
Performance Analytics Module
Calculates key trading metrics: Sharpe ratio, max drawdown, win rate, etc.
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime

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
        """
        Load equity curve DataFrame.
        Expected columns: ['date', 'equity']
        """
        self.equity_curve = df.copy()
        self.equity_curve['date'] = pd.to_datetime(self.equity_curve['date'])
        self.equity_curve = self.equity_curve.sort_values('date').reset_index(drop=True)
        
    def calculate_returns(self) -> pd.Series:
        """Calculate daily returns from equity curve."""
        if self.equity_curve is None:
            raise ValueError("No equity curve loaded.")
        return self.equity_curve['equity'].pct_change().dropna()
        
    def total_return(self) -> float:
        """Calculate total return percentage."""
        if self.equity_curve is None or len(self.equity_curve) < 2:
            return 0.0
        start = self.equity_curve['equity'].iloc[0]
        end = self.equity_curve['equity'].iloc[-1]
        return (end - start) / start
        
    def annualized_return(self) -> float:
        """Calculate annualized return."""
        total = self.total_return()
        if len(self.equity_curve) < 2:
            return 0.0
            
        # Calculate number of years
        days = (self.equity_curve['date'].iloc[-1] - self.equity_curve['date'].iloc[0]).days
        years = days / 365.0
        if years <= 0:
            return 0.0
            
        return (1 + total) ** (1 / years) - 1
        
    def volatility(self) -> float:
        """Calculate annualized volatility."""
        returns = self.calculate_returns()
        daily_vol = returns.std()
        return daily_vol * np.sqrt(252)  # Annualized
        
    def sharpe_ratio(self, risk_free_rate: float = 0.03) -> float:
        """
        Calculate Sharpe Ratio.
        (Annualized Return - Risk Free Rate) / Annualized Volatility
        """
        vol = self.volatility()
        if vol == 0:
            return 0.0
            
        ann_return = self.annualized_return()
        return (ann_return - risk_free_rate) / vol
        
    def sortino_ratio(self, risk_free_rate: float = 0.03) -> float:
        """
        Calculate Sortino Ratio.
        Uses downside deviation instead of total volatility.
        """
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
        """Calculate maximum drawdown percentage."""
        if self.equity_curve is None:
            return 0.0
            
        equity = self.equity_curve['equity']
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        return drawdown.min()
        
    def calmar_ratio(self) -> float:
        """Calculate Calmar Ratio (Annualized Return / Max Drawdown)."""
        mdd = abs(self.max_drawdown())
        if mdd == 0:
            return 0.0
            
        return self.annualized_return() / mdd
        
    def win_rate(self) -> float:
        """Calculate win rate from trade log."""
        if not self.trades:
            return 0.0
            
        wins = sum(1 for t in self.trades if t.get('pnl', 0) > 0)
        return wins / len(self.trades)
        
    def profit_factor(self) -> float:
        """Calculate profit factor (Gross Profit / Gross Loss)."""
        if not self.trades:
            return 0.0
            
        gross_profit = sum(t.get('pnl', 0) for t in self.trades if t.get('pnl', 0) > 0)
        gross_loss = abs(sum(t.get('pnl', 0) for t in self.trades if t.get('pnl', 0) < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
            
        return gross_profit / gross_loss
        
    def avg_win_loss_ratio(self) -> float:
        """Calculate average win / average loss ratio."""
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
        """Get comprehensive performance summary."""
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
        """Print formatted performance report."""
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
