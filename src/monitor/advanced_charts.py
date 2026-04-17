"""
Phase 26: Advanced Chart Generator
Charts with technical indicators overlay.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class AdvancedChartGenerator:
    """
    Generate advanced charts with technical indicators.
    """
    
    def __init__(self):
        self.engine = None
        try:
            from src.data.database import get_db_engine
            self.engine = get_db_engine()
        except:
            pass
            
    def generate_kline_with_indicators(self, code: str, days: int = 60, 
                                        indicators: List[str] = None) -> Optional[str]:
        """
        Generate K-line chart with technical indicators overlay.
        
        Args:
            code: Stock code
            days: Number of days
            indicators: List of indicators to show ['ma', 'macd', 'rsi', 'bb']
            
        Returns:
            HTML string with chart
        """
        if indicators is None:
            indicators = ['ma', 'volume']
            
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
        
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except ImportError:
            return None
            
        # Calculate indicators
        if 'ma' in indicators:
            df['ma5'] = df['close'].rolling(5).mean()
            df['ma10'] = df['close'].rolling(10).mean()
            df['ma20'] = df['close'].rolling(20).mean()
            
        if 'macd' in indicators:
            ema12 = df['close'].ewm(span=12, adjust=False).mean()
            ema26 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = ema12 - ema26
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
            
        if 'rsi' in indicators:
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
        if 'bb' in indicators:
            df['bb_mid'] = df['close'].rolling(20).mean()
            std20 = df['close'].rolling(20).std()
            df['bb_upper'] = df['bb_mid'] + 2 * std20
            df['bb_lower'] = df['bb_mid'] - 2 * std20
            
        # Create subplots
        row_count = 1
        if 'volume' in indicators:
            row_count += 1
        if 'macd' in indicators:
            row_count += 1
        if 'rsi' in indicators:
            row_count += 1
            
        fig = make_subplots(
            rows=row_count, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.5] + [0.5/(row_count-1)]*(row_count-1) if row_count > 1 else [1],
            subplot_titles=[f'{code} K-Line'] + ['', '', ''][:row_count-1]
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
        
        # Moving Averages
        if 'ma' in indicators:
            fig.add_trace(go.Scatter(x=df['date'], y=df['ma5'], name='MA5', line=dict(width=1)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['date'], y=df['ma10'], name='MA10', line=dict(width=1)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['date'], y=df['ma20'], name='MA20', line=dict(width=1)), row=1, col=1)
            
        # Bollinger Bands
        if 'bb' in indicators:
            fig.add_trace(go.Scatter(x=df['date'], y=df['bb_upper'], name='BB Upper', 
                                    line=dict(width=1, dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['date'], y=df['bb_lower'], name='BB Lower', 
                                    line=dict(width=1, dash='dash')), row=1, col=1)
            
        # Volume
        current_row = 2
        if 'volume' in indicators:
            colors = ['red' if row['close'] >= row['open'] else 'green' for _, row in df.iterrows()]
            fig.add_trace(go.Bar(x=df['date'], y=df['volume'], marker_color=colors, name='Volume'), 
                         row=current_row, col=1)
            current_row += 1
            
        # MACD
        if 'macd' in indicators:
            fig.add_trace(go.Scatter(x=df['date'], y=df['macd'], name='MACD', line=dict(width=1)), 
                         row=current_row, col=1)
            fig.add_trace(go.Scatter(x=df['date'], y=df['macd_signal'], name='Signal', line=dict(width=1)), 
                         row=current_row, col=1)
            colors = ['red' if v >= 0 else 'green' for v in df['macd_hist']]
            fig.add_trace(go.Bar(x=df['date'], y=df['macd_hist'], marker_color=colors, name='Histogram'), 
                         row=current_row, col=1)
            current_row += 1
            
        # RSI
        if 'rsi' in indicators:
            fig.add_trace(go.Scatter(x=df['date'], y=df['rsi'], name='RSI', line=dict(width=2)), 
                         row=current_row, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)
            
        fig.update_layout(
            title=f'{code} 技术分析图表',
            xaxis_title='日期',
            yaxis_title='价格',
            template='plotly_dark',
            height=300 * row_count,
            showlegend=True
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    def generate_equity_curve(self, daily_pnl: List[Dict]) -> Optional[str]:
        """Generate interactive equity curve chart."""
        if not daily_pnl:
            return None
            
        try:
            import plotly.graph_objects as go
        except ImportError:
            return None
            
        dates = [d.get('date', '') for d in daily_pnl]
        values = [d.get('portfolio_value', 0) for d in daily_pnl]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='组合净值',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        
        fig.update_layout(
            title='投资组合净值曲线',
            xaxis_title='日期',
            yaxis_title='净值',
            template='plotly_dark',
            height=400
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    def generate_drawdown_chart(self, daily_pnl: List[Dict]) -> Optional[str]:
        """Generate drawdown chart."""
        if not daily_pnl:
            return None
            
        try:
            import plotly.graph_objects as go
        except ImportError:
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
            name='回撤',
            line=dict(color='#d62728', width=2),
            fill='tozeroy',
            fillcolor='rgba(214, 39, 40, 0.2)'
        ))
        
        fig.update_layout(
            title='投资组合回撤曲线',
            xaxis_title='日期',
            yaxis_title='回撤',
            yaxis_tickformat='.1%',
            template='plotly_dark',
            height=300
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
