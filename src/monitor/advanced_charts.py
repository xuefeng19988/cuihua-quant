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
sys.path.insert(0, project_root)

from src.core.utils import load_stock_names

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
        df['date_cn'] = df['date'].dt.strftime('%Y年%m月%d日')
        
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
            
        # Load stock name
        stock_names = load_stock_names()
        stock_name = stock_names.get(code, '')
        title_label = f"{code} {stock_name} K线图".strip() if stock_name else f"{code} K线图"
        
        # Create subplots
        row_count = 1
        if 'volume' in indicators:
            row_count += 1
        if 'macd' in indicators:
            row_count += 1
        if 'rsi' in indicators:
            row_count += 1
        
        # Chinese subplot titles
        subplot_titles = [title_label]
        if 'volume' in indicators:
            subplot_titles.append('成交量')
        if 'macd' in indicators:
            subplot_titles.append('MACD')
        if 'rsi' in indicators:
            subplot_titles.append('RSI 相对强弱指标')
            
        fig = make_subplots(
            rows=row_count, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.5] + [0.5/(row_count-1)]*(row_count-1) if row_count > 1 else [1],
            subplot_titles=subplot_titles[:row_count]
        )
        
        # Candlestick (中国股市：红涨绿跌)
        fig.add_trace(go.Candlestick(
            x=df['date_cn'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K线',
            increasing_line_color='#ef4444',
            decreasing_line_color='#22c55e',
            increasing_fillcolor='#ef4444',
            decreasing_fillcolor='#22c55e',
        ), row=1, col=1)
        
        # Moving Averages
        if 'ma' in indicators:
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['ma5'], name='MA5 均线', line=dict(width=1)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['ma10'], name='MA10 均线', line=dict(width=1)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['ma20'], name='MA20 均线', line=dict(width=1)), row=1, col=1)
            
        # Bollinger Bands
        if 'bb' in indicators:
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['bb_upper'], name='布林上轨', 
                                    line=dict(width=1, dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['bb_lower'], name='布林下轨', 
                                    line=dict(width=1, dash='dash')), row=1, col=1)
            
        # Volume
        current_row = 2
        if 'volume' in indicators:
            colors = ['red' if row['close'] >= row['open'] else 'green' for _, row in df.iterrows()]
            fig.add_trace(go.Bar(x=df['date_cn'], y=df['volume'], marker_color=colors, name='成交量'), 
                         row=current_row, col=1)
            current_row += 1
            
        # MACD
        if 'macd' in indicators:
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['macd'], name='MACD 线', line=dict(width=1)), 
                         row=current_row, col=1)
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['macd_signal'], name='信号线', line=dict(width=1)), 
                         row=current_row, col=1)
            colors = ['red' if v >= 0 else 'green' for v in df['macd_hist']]
            fig.add_trace(go.Bar(x=df['date_cn'], y=df['macd_hist'], marker_color=colors, name='MACD 柱'), 
                         row=current_row, col=1)
            current_row += 1
            
        # RSI
        if 'rsi' in indicators:
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['rsi'], name='RSI 相对强弱', line=dict(width=2)), 
                         row=current_row, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)
            
        fig.update_layout(
            title=f'{code} {stock_name} 技术分析图表' if stock_name else f'{code} 技术分析图表',
            xaxis_title='日期',
            yaxis_title='价格 (元)',
            template='plotly_dark',
            height=300 * row_count,
            showlegend=True,
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0.5)', font=dict(color='white'))
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
            yaxis_title='组合净值 (元)',
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
            yaxis_title='回撤比例',
            yaxis_tickformat='.1%',
            template='plotly_dark',
            height=300
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
