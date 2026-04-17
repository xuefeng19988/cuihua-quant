"""
Phase 18.4: Mock data generator for testing.
"""

import os
import sys
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MockDataGenerator:
    """
    Generates realistic mock data for testing without real market data.
    """
    
    @staticmethod
    def generate_ohlcv(
        code: str = "SH.600519",
        days: int = 252,
        start_price: float = 100.0,
        volatility: float = 0.02,
        trend: float = 0.0001,
        start_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Generate realistic OHLCV data.
        
        Args:
            code: Stock code
            days: Number of trading days
            start_price: Initial price
            volatility: Daily volatility
            trend: Daily trend bias
            start_date: Start date (YYYY-MM-DD)
            
        Returns:
            DataFrame with OHLCV data
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        dates = []
        current_dt = start_dt
        
        # Generate trading days (skip weekends)
        while len(dates) < days:
            if current_dt.weekday() < 5:
                dates.append(current_dt.strftime("%Y-%m-%d"))
            current_dt += timedelta(days=1)
            
        # Generate prices using geometric Brownian motion
        np.random.seed(hash(code) % 2**32)  # Reproducible per code
        returns = np.random.normal(trend, volatility, days)
        prices = start_price * np.cumprod(1 + returns)
        
        # Generate OHLCV
        data = []
        for i, date in enumerate(dates):
            close = prices[i]
            daily_range = close * np.random.uniform(0.005, 0.03)
            open_price = close + np.random.uniform(-daily_range/2, daily_range/2)
            high = max(open_price, close) + np.random.uniform(0, daily_range/2)
            low = min(open_price, close) - np.random.uniform(0, daily_range/2)
            volume = int(np.random.uniform(1e6, 1e8))
            turnover = volume * close
            
            data.append({
                "date": date,
                "open_price": round(open_price, 2),
                "high_price": round(high, 2),
                "low_price": round(low, 2),
                "close_price": round(close, 2),
                "volume": volume,
                "turnover": round(turnover, 2),
                "change_pct": round((close / prices[i-1] - 1) * 100 if i > 0 else 0, 2),
                "turnover_rate": round(np.random.uniform(0.5, 5.0), 2),
                "pe_ratio": round(np.random.uniform(10, 50), 2),
            })
            
        return pd.DataFrame(data)
        
    @staticmethod
    def generate_portfolio(initial_capital: float = 1000000, days: int = 60) -> pd.DataFrame:
        """Generate mock portfolio daily P&L."""
        np.random.seed(42)
        daily_returns = np.random.normal(0.0005, 0.015, days)
        
        values = [initial_capital]
        for ret in daily_returns:
            values.append(values[-1] * (1 + ret))
            
        dates = [(datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d") for i in range(days+1)]
        
        return pd.DataFrame({
            "date": dates[1:],
            "portfolio_value": values[1:],
            "daily_pnl": np.diff(values),
            "daily_pnl_pct": daily_returns,
            "cash": np.random.uniform(100000, 300000, days),
            "market_value": [v - c for v, c in zip(values[1:], np.random.uniform(100000, 300000, days))],
            "num_positions": np.random.randint(3, 10, days),
        })
        
    @staticmethod
    def generate_trades(count: int = 100, start_date: Optional[str] = None) -> pd.DataFrame:
        """Generate mock trade history."""
        np.random.seed(123)
        codes = ["SH.600519", "SZ.002594", "HK.00700", "SZ.300750", "SH.601318"]
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            
        trades = []
        for i in range(count):
            code = random.choice(codes)
            entry_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=random.randint(0, 60))
            exit_date = entry_date + timedelta(days=random.randint(1, 30))
            
            entry_price = random.uniform(50, 500)
            exit_price = entry_price * (1 + random.uniform(-0.1, 0.15))
            shares = random.randint(1, 10) * 100
            
            trades.append({
                "code": code,
                "action": "SELL",
                "shares": shares,
                "entry_price": round(entry_price, 2),
                "exit_price": round(exit_price, 2),
                "pnl": round((exit_price - entry_price) * shares, 2),
                "pnl_pct": round((exit_price / entry_price - 1), 4),
                "entry_date": entry_date.strftime("%Y-%m-%d"),
                "exit_date": exit_date.strftime("%Y-%m-%d"),
            })
            
        return pd.DataFrame(trades)
        
    @staticmethod
    def generate_signals(codes: List[str], count: int = 10) -> pd.DataFrame:
        """Generate mock trading signals."""
        np.random.seed(456)
        
        signals = []
        for code in codes:
            for _ in range(random.randint(1, count)):
                score = np.random.uniform(-1, 1)
                signals.append({
                    "code": code,
                    "close": round(np.random.uniform(50, 500), 2),
                    "tech_score": round(np.random.uniform(-1, 1), 3),
                    "sentiment_score": round(np.random.uniform(-1, 1), 3),
                    "combined_score": round(score, 3),
                    "signals": random.sample(["MACD_GoldenCross", "RSI_OverSold", "Above_MA20", "BB_Lower"], k=random.randint(0, 3)),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                })
                
        df = pd.DataFrame(signals)
        if not df.empty:
            df = df.sort_values("combined_score", ascending=False).reset_index(drop=True)
            df["rank"] = df.index + 1
            
        return df
