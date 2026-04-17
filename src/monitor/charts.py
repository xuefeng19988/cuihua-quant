"""
Phase 10.3: Interactive Charts
Chart generation for K-line, equity curve, drawdown, etc.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

class ChartGenerator:
    """
    Generates charts for trading analysis.
    Supports: K-line, equity curve, drawdown, volume, etc.
    """
    
    def __init__(self):
        pass
        
    def generate_kline_chart_data(self, code: str, engine, days: int = 60) -> Dict:
        """
        Generate K-line chart data.
        Returns dict ready for frontend rendering.
        """
        df = pd.read_sql(
            f"SELECT date, open_price as open, high_price as high, low_price as low, "
            f"close_price as close, volume FROM stock_daily "
            f"WHERE code='{code}' ORDER BY date DESC LIMIT {days}",
            engine
        )
        
        if df.empty:
            return {'error': 'No data'}
            
        df = df.iloc[::-1].reset_index(drop=True)  # Reverse to chronological
        
        chart_data = {
            'dates': df['date'].tolist(),
            'candles': [],
            'volumes': df['volume'].tolist()
        }
        
        for _, row in df.iterrows():
            chart_data['candles'].append({
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume']
            })
            
        # Calculate MAs
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        chart_data['ma5'] = df['ma5'].tolist()
        chart_data['ma20'] = df['ma20'].tolist()
        
        return chart_data
        
    def generate_equity_curve(self, daily_pnl: List[Dict]) -> Dict:
        """
        Generate equity curve data from daily P&L.
        """
        if not daily_pnl:
            return {'error': 'No data'}
            
        dates = []
        values = []
        cumulative = daily_pnl[0].get('portfolio_value', 0)
        
        for day in daily_pnl:
            dates.append(day.get('date', ''))
            values.append(day.get('portfolio_value', cumulative))
            
        return {
            'dates': dates,
            'values': values,
            'start_value': values[0] if values else 0,
            'end_value': values[-1] if values else 0,
            'max_value': max(values) if values else 0,
            'min_value': min(values) if values else 0
        }
        
    def generate_drawdown_chart(self, daily_pnl: List[Dict]) -> Dict:
        """Generate drawdown chart data."""
        if not daily_pnl:
            return {'error': 'No data'}
            
        values = [d.get('portfolio_value', 0) for d in daily_pnl]
        if not values:
            return {'error': 'No values'}
            
        # Calculate drawdown
        peak = values[0]
        drawdowns = []
        
        for value in values:
            if value > peak:
                peak = value
            dd = (value - peak) / peak if peak > 0 else 0
            drawdowns.append(dd)
            
        return {
            'dates': [d.get('date', '') for d in daily_pnl],
            'drawdowns': drawdowns,
            'max_drawdown': min(drawdowns) if drawdowns else 0
        }
        
    def generate_ascii_chart(self, data: List[float], width: int = 50) -> str:
        """Generate simple ASCII chart for console output."""
        if not data:
            return ""
            
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        lines = []
        for val in data[-20:]:  # Last 20 points
            bar_len = int((val - min_val) / range_val * width)
            bar = "█" * bar_len
            lines.append(f"{val:>10.2f} | {bar}")
            
        return "\n".join(lines)
        
    def generate_performance_summary(self, daily_pnl: List[Dict]) -> Dict:
        """Generate comprehensive performance summary."""
        if not daily_pnl:
            return {}
            
        values = [d.get('portfolio_value', 0) for d in daily_pnl]
        daily_returns = []
        
        for i in range(1, len(values)):
            if values[i-1] > 0:
                ret = (values[i] - values[i-1]) / values[i-1]
                daily_returns.append(ret)
                
        if not daily_returns:
            return {}
            
        total_return = (values[-1] - values[0]) / values[0] if values[0] > 0 else 0
        avg_return = np.mean(daily_returns)
        volatility = np.std(daily_returns) * np.sqrt(252)
        sharpe = (avg_return * 252 - 0.02) / volatility if volatility > 0 else 0
        
        # Max drawdown
        peak = values[0]
        max_dd = 0
        for val in values:
            if val > peak:
                peak = val
            dd = (val - peak) / peak
            if dd < max_dd:
                max_dd = dd
                
        return {
            'total_return': total_return,
            'annualized_return': (1 + total_return) ** (252 / len(values)) - 1 if len(values) > 0 else 0,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'win_rate': sum(1 for r in daily_returns if r > 0) / len(daily_returns),
            'avg_daily_return': avg_return,
            'trading_days': len(values)
        }


if __name__ == "__main__":
    generator = ChartGenerator()
    
    # Test ASCII chart
    data = [100, 102, 101, 105, 108, 106, 110, 112, 109, 115]
    print("Equity Curve:")
    print(generator.generate_ascii_chart(data))
    
    # Test performance summary
    daily_pnl = [{'portfolio_value': 100000 + i*1000} for i in range(20)]
    summary = generator.generate_performance_summary(daily_pnl)
    print("\nPerformance Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
