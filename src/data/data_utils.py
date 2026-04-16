"""
Data Utils
Common data processing utilities.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate daily returns."""
    return prices.pct_change()

def calculate_drawdown(equity: pd.Series) -> pd.Series:
    """Calculate drawdown series."""
    peak = equity.cummax()
    return (equity - peak) / peak

def calculate_sharpe(returns: pd.Series, risk_free: float = 0.03) -> float:
    """Calculate annualized Sharpe ratio."""
    if returns.std() == 0:
        return 0.0
    return (returns.mean() * 252 - risk_free) / (returns.std() * np.sqrt(252))

def calculate_max_drawdown(equity: pd.Series) -> float:
    """Calculate maximum drawdown."""
    dd = calculate_drawdown(equity)
    return dd.min()

def calculate_win_rate(pnls: pd.Series) -> float:
    """Calculate win rate from P&L series."""
    if len(pnls) == 0:
        return 0.0
    return (pnls > 0).sum() / len(pnls)

def calculate_profit_factor(pnls: pd.Series) -> float:
    """Calculate profit factor."""
    gross_profit = pnls[pnls > 0].sum()
    gross_loss = abs(pnls[pnls < 0].sum())
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    return gross_profit / gross_loss

def get_trading_days(start: str, end: str = None) -> List[str]:
    """Get list of trading days (Mon-Fri)."""
    if end is None:
        end = datetime.now().strftime('%Y-%m-%d')
    start_dt = datetime.strptime(start, '%Y-%m-%d')
    end_dt = datetime.strptime(end, '%Y-%m-%d')
    days = []
    current = start_dt
    while current <= end_dt:
        if current.weekday() < 5:
            days.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    return days
