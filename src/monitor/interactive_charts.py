"""
Phase 23.1: Interactive Charts with Plotly
Generates interactive visualizations for trading analysis.
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

class InteractiveCharts:
    """
    Generates interactive charts using Plotly.
    """
    
    def __init__(self):
        self.engine = None
        try:
            from src.data.database import get_db_engine
            self.engine = get_db_engine()
        except:
            pass
            
    def generate_kline_chart(self, code: str, days: int = 60) -> Optional[str]:
        """
        Generate interactive K-line chart.
        Returns HTML string.
        """
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except ImportError:
            return None
            
        if self.engine is None:
            return None
            
        df = pd.read_sql(
            f"SELECT date, open_price as open, high_price as high, "
            f"low_price as low, close_price as close, volume FROM stock_daily "
            f"WHERE code='{code}' ORDER BY date DESC LIMIT {days}",
            self.engine
        )
        
        if df.empty:
            return None
            
        df = df.iloc[::-1].reset_index(drop=True)
        df['date'] = pd.to_datetime(df['date'])
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=(f'{code} K-Line', 'Volume')
        )
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K-Line'
        ), row=1, col=1)
        
        # Volume
        colors = ['red' if row['close'] >= row['open'] else 'green' for _, row in df.iterrows()]
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['volume'],
            marker_color=colors,
            name='Volume'
        ), row=2, col=1)
        
        fig.update_layout(
            title=f'{code} Interactive K-Line Chart',
            xaxis_title='Date',
            yaxis_title='Price',
            template='plotly_dark',
            height=600
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    def generate_equity_curve(self, daily_pnl: List[Dict]) -> Optional[str]:
        """Generate interactive equity curve."""
        try:
            import plotly.graph_objects as go
        except ImportError:
            return None
            
        if not daily_pnl:
            return None
            
        dates = [d.get('date', '') for d in daily_pnl]
        values = [d.get('portfolio_value', 0) for d in daily_pnl]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        
        fig.update_layout(
            title='Portfolio Equity Curve',
            xaxis_title='Date',
            yaxis_title='Value',
            template='plotly_dark',
            height=400
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    def generate_drawdown_chart(self, daily_pnl: List[Dict]) -> Optional[str]:
        """Generate interactive drawdown chart."""
        try:
            import plotly.graph_objects as go
        except ImportError:
            return None
            
        if not daily_pnl:
            return None
            
        values = [d.get('portfolio_value', 0) for d in daily_pnl]
        peak = values[0]
        drawdowns = []
        
        for val in values:
            if val > peak:
                peak = val
            dd = (val - peak) / peak if peak > 0 else 0
            drawdowns.append(dd)
            
        dates = [d.get('date', '') for d in daily_pnl]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=drawdowns,
            mode='lines',
            name='Drawdown',
            line=dict(color='#d62728', width=2),
            fill='tozeroy',
            fillcolor='rgba(214, 39, 40, 0.2)'
        ))
        
        fig.update_layout(
            title='Portfolio Drawdown',
            xaxis_title='Date',
            yaxis_title='Drawdown',
            yaxis_tickformat='.1%',
            template='plotly_dark',
            height=300
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    def generate_factor_heatmap(self, factor_data: pd.DataFrame) -> Optional[str]:
        """Generate factor correlation heatmap."""
        try:
            import plotly.express as px
        except ImportError:
            return None
            
        if factor_data.empty:
            return None
            
        corr = factor_data.corr()
        
        fig = px.imshow(
            corr,
            labels=dict(x="Factor", y="Factor", color="Correlation"),
            color_continuous_scale='RdBu_r',
            aspect='auto'
        )
        
        fig.update_layout(
            title='Factor Correlation Heatmap',
            template='plotly_dark',
            height=600
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    def generate_strategy_comparison(self, strategies: Dict[str, List[float]]) -> Optional[str]:
        """Generate strategy comparison chart."""
        try:
            import plotly.graph_objects as go
        except ImportError:
            return None
            
        fig = go.Figure()
        
        for name, values in strategies.items():
            fig.add_trace(go.Scatter(
                y=values,
                mode='lines',
                name=name,
                line=dict(width=2)
            ))
            
        fig.update_layout(
            title='Strategy Performance Comparison',
            xaxis_title='Trading Days',
            yaxis_title='Cumulative Return',
            template='plotly_dark',
            height=400
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')


if __name__ == "__main__":
    charts = InteractiveCharts()
    print("Interactive Charts module initialized")
    print("Requires: pip install plotly")
