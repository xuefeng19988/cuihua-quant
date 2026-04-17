"""
Chart Generation Module (Merged)
Combines: ChartGenerator + AdvancedChartGenerator + InteractiveCharts
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
    """Generates charts for trading analysis (data format + ASCII)."""

    def generate_kline_chart_data(self, code: str, engine, days: int = 60) -> Dict:
        df = pd.read_sql(
            f"SELECT date, open_price as open, high_price as high, low_price as low, "
            f"close_price as close, volume FROM stock_daily WHERE code='{code}' "
            f"ORDER BY date DESC LIMIT {days}", engine)
        if df.empty:
            return {'error': 'No data'}
        df = df.iloc[::-1].reset_index(drop=True)
        chart_data = {'dates': df['date'].tolist(), 'candles': [], 'volumes': df['volume'].tolist()}
        for _, row in df.iterrows():
            chart_data['candles'].append({
                'open': row['open'], 'high': row['high'],
                'low': row['low'], 'close': row['close'], 'volume': row['volume']})
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        chart_data['ma5'] = df['ma5'].tolist()
        chart_data['ma20'] = df['ma20'].tolist()
        return chart_data

    def generate_equity_curve(self, daily_pnl: List[Dict]) -> Dict:
        if not daily_pnl:
            return {'error': 'No data'}
        dates, values = [], []
        cumulative = daily_pnl[0].get('portfolio_value', 0)
        for day in daily_pnl:
            dates.append(day.get('date', ''))
            values.append(day.get('portfolio_value', cumulative))
        return {'dates': dates, 'values': values,
                'start_value': values[0] if values else 0,
                'end_value': values[-1] if values else 0,
                'max_value': max(values) if values else 0,
                'min_value': min(values) if values else 0}

    def generate_drawdown_chart(self, daily_pnl: List[Dict]) -> Dict:
        if not daily_pnl:
            return {'error': 'No data'}
        values = [d.get('portfolio_value', 0) for d in daily_pnl]
        if not values:
            return {'error': 'No values'}
        peak = values[0]
        drawdowns = []
        for value in values:
            if value > peak:
                peak = value
            drawdowns.append((value - peak) / peak if peak > 0 else 0)
        return {'dates': [d.get('date', '') for d in daily_pnl],
                'drawdowns': drawdowns, 'max_drawdown': min(drawdowns) if drawdowns else 0}

    def generate_ascii_chart(self, data: List[float], width: int = 50) -> str:
        if not data:
            return ""
        min_val, max_val = min(data), max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        lines = []
        for val in data[-20:]:
            bar_len = int((val - min_val) / range_val * width)
            lines.append(f"{val:>10.2f} | {'█' * bar_len}")
        return "\n".join(lines)

    def generate_performance_summary(self, daily_pnl: List[Dict]) -> Dict:
        if not daily_pnl:
            return {}
        values = [d.get('portfolio_value', 0) for d in daily_pnl]
        daily_returns = []
        for i in range(1, len(values)):
            if values[i - 1] > 0:
                daily_returns.append((values[i] - values[i - 1]) / values[i - 1])
        if not daily_returns:
            return {}
        total_return = (values[-1] - values[0]) / values[0] if values[0] > 0 else 0
        avg_return = np.mean(daily_returns)
        volatility = np.std(daily_returns) * np.sqrt(252)
        sharpe = (avg_return * 252 - 0.02) / volatility if volatility > 0 else 0
        peak = values[0]
        max_dd = 0
        for val in values:
            if val > peak:
                peak = val
            dd = (val - peak) / peak
            if dd < max_dd:
                max_dd = dd
        return {'total_return': total_return,
                'annualized_return': (1 + total_return) ** (252 / len(values)) - 1 if len(values) > 0 else 0,
                'volatility': volatility, 'sharpe_ratio': sharpe,
                'max_drawdown': max_dd,
                'win_rate': sum(1 for r in daily_returns if r > 0) / len(daily_returns),
                'avg_daily_return': avg_return, 'trading_days': len(values)}


class AdvancedChartGenerator:
    """Generate advanced charts with technical indicators using Plotly."""

    def __init__(self):
        self.engine = None
        try:
            from src.data.database import get_db_engine
            self.engine = get_db_engine()
        except Exception:
            pass

    def generate_kline_with_indicators(self, code: str, days: int = 60,
                                       indicators: List[str] = None) -> Optional[str]:
        if indicators is None:
            indicators = ['ma', 'volume']
        if self.engine is None:
            return None
        df = pd.read_sql(
            f"SELECT date, open_price as open, high_price as high, "
            f"low_price as low, close_price as close, volume FROM stock_daily "
            f"WHERE code='{code}' ORDER BY date DESC LIMIT {days}", self.engine)
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
        from src.core.utils import load_stock_names
        stock_name = load_stock_names().get(code, '')
        title_label = f"{code} {stock_name} K线图".strip() if stock_name else f"{code} K线图"
        row_count = 1 + sum(1 for x in ['volume', 'macd', 'rsi'] if x in indicators)
        subplot_titles = [title_label]
        if 'volume' in indicators:
            subplot_titles.append('成交量')
        if 'macd' in indicators:
            subplot_titles.append('MACD')
        if 'rsi' in indicators:
            subplot_titles.append('RSI 相对强弱指标')
        fig = make_subplots(rows=row_count, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                            row_heights=[0.5] + [0.5 / (row_count - 1)] * (row_count - 1) if row_count > 1 else [1],
                            subplot_titles=subplot_titles[:row_count])
        fig.add_trace(go.Candlestick(x=df['date_cn'], open=df['open'], high=df['high'],
                                     low=df['low'], close=df['close'], name='K线',
                                     increasing_line_color='#ef4444', decreasing_line_color='#22c55e',
                                     increasing_fillcolor='#ef4444', decreasing_fillcolor='#22c55e'), row=1, col=1)
        if 'ma' in indicators:
            for ma, name in [('ma5', 'MA5'), ('ma10', 'MA10'), ('ma20', 'MA20')]:
                fig.add_trace(go.Scatter(x=df['date_cn'], y=df[ma], name=f'{name} 均线',
                                         line=dict(width=1)), row=1, col=1)
        if 'bb' in indicators:
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['bb_upper'], name='布林上轨',
                                     line=dict(width=1, dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['bb_lower'], name='布林下轨',
                                     line=dict(width=1, dash='dash')), row=1, col=1)
        current_row = 2
        if 'volume' in indicators:
            colors = ['red' if row['close'] >= row['open'] else 'green' for _, row in df.iterrows()]
            fig.add_trace(go.Bar(x=df['date_cn'], y=df['volume'], marker_color=colors, name='成交量'),
                          row=current_row, col=1)
            current_row += 1
        if 'macd' in indicators:
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['macd'], name='MACD 线',
                                     line=dict(width=1)), row=current_row, col=1)
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['macd_signal'], name='信号线',
                                     line=dict(width=1)), row=current_row, col=1)
            colors = ['red' if v >= 0 else 'green' for v in df['macd_hist']]
            fig.add_trace(go.Bar(x=df['date_cn'], y=df['macd_hist'], marker_color=colors, name='MACD 柱'),
                          row=current_row, col=1)
            current_row += 1
        if 'rsi' in indicators:
            fig.add_trace(go.Scatter(x=df['date_cn'], y=df['rsi'], name='RSI 相对强弱',
                                     line=dict(width=2)), row=current_row, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)
        fig.update_layout(title=f'{code} {stock_name} 技术分析图表' if stock_name else f'{code} 技术分析图表',
                          xaxis_title='日期', yaxis_title='价格 (元)', template='plotly_dark',
                          height=300 * row_count, showlegend=True,
                          legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0.5)', font=dict(color='white')))
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    def generate_equity_curve(self, daily_pnl: List[Dict]) -> Optional[str]:
        if not daily_pnl:
            return None
        try:
            import plotly.graph_objects as go
        except ImportError:
            return None
        dates = [d.get('date', '') for d in daily_pnl]
        values = [d.get('portfolio_value', 0) for d in daily_pnl]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=values, mode='lines+markers', name='组合净值',
                                 line=dict(color='#1f77b4', width=2), fill='tozeroy',
                                 fillcolor='rgba(31, 119, 180, 0.1)'))
        fig.update_layout(title='投资组合净值曲线', xaxis_title='日期', yaxis_title='组合净值 (元)',
                          template='plotly_dark', height=400)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    def generate_drawdown_chart(self, daily_pnl: List[Dict]) -> Optional[str]:
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
            drawdowns.append((val - peak) / peak if peak > 0 else 0)
        dates = [d.get('date', '') for d in daily_pnl]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=drawdowns, mode='lines', name='回撤',
                                 line=dict(color='#d62728', width=2), fill='tozeroy',
                                 fillcolor='rgba(214, 39, 40, 0.2)'))
        fig.update_layout(title='投资组合回撤曲线', xaxis_title='日期', yaxis_title='回撤比例',
                          yaxis_tickformat='.1%', template='plotly_dark', height=300)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')


class InteractiveCharts:
    """Generates interactive charts using Plotly."""

    def __init__(self):
        self.engine = None
        try:
            from src.data.database import get_db_engine
            self.engine = get_db_engine()
        except Exception:
            pass

    def generate_kline_chart(self, code: str, days: int = 60) -> Optional[str]:
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
            f"WHERE code='{code}' ORDER BY date DESC LIMIT {days}", self.engine)
        if df.empty:
            return None
        df = df.iloc[::-1].reset_index(drop=True)
        df['date'] = pd.to_datetime(df['date'])
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                            row_heights=[0.7, 0.3], subplot_titles=(f'{code} K-Line', 'Volume'))
        fig.add_trace(go.Candlestick(x=df['date'], open=df['open'], high=df['high'],
                                     low=df['low'], close=df['close'], name='K-Line'), row=1, col=1)
        colors = ['red' if row['close'] >= row['open'] else 'green' for _, row in df.iterrows()]
        fig.add_trace(go.Bar(x=df['date'], y=df['volume'], marker_color=colors, name='Volume'),
                      row=2, col=1)
        fig.update_layout(title=f'{code} Interactive K-Line Chart', xaxis_title='Date',
                          yaxis_title='Price', template='plotly_dark', height=600)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    def generate_equity_curve(self, daily_pnl: List[Dict]) -> Optional[str]:
        try:
            import plotly.graph_objects as go
        except ImportError:
            return None
        if not daily_pnl:
            return None
        dates = [d.get('date', '') for d in daily_pnl]
        values = [d.get('portfolio_value', 0) for d in daily_pnl]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=values, mode='lines+markers', name='Portfolio Value',
                                 line=dict(color='#1f77b4', width=2), fill='tozeroy',
                                 fillcolor='rgba(31, 119, 180, 0.1)'))
        fig.update_layout(title='Portfolio Equity Curve', xaxis_title='Date', yaxis_title='Value',
                          template='plotly_dark', height=400)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    def generate_drawdown_chart(self, daily_pnl: List[Dict]) -> Optional[str]:
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
            drawdowns.append((val - peak) / peak if peak > 0 else 0)
        dates = [d.get('date', '') for d in daily_pnl]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=drawdowns, mode='lines', name='Drawdown',
                                 line=dict(color='#d62728', width=2), fill='tozeroy',
                                 fillcolor='rgba(214, 39, 40, 0.2)'))
        fig.update_layout(title='Portfolio Drawdown', xaxis_title='Date', yaxis_title='Drawdown',
                          yaxis_tickformat='.1%', template='plotly_dark', height=300)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    def generate_factor_heatmap(self, factor_data: pd.DataFrame) -> Optional[str]:
        try:
            import plotly.express as px
        except ImportError:
            return None
        if factor_data.empty:
            return None
        corr = factor_data.corr()
        fig = px.imshow(corr, labels=dict(x="Factor", y="Factor", color="Correlation"),
                        color_continuous_scale='RdBu_r', aspect='auto')
        fig.update_layout(title='Factor Correlation Heatmap', template='plotly_dark', height=600)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    def generate_strategy_comparison(self, strategies: Dict[str, List[float]]) -> Optional[str]:
        try:
            import plotly.graph_objects as go
        except ImportError:
            return None
        fig = go.Figure()
        for name, values in strategies.items():
            fig.add_trace(go.Scatter(y=values, mode='lines', name=name, line=dict(width=2)))
        fig.update_layout(title='Strategy Performance Comparison', xaxis_title='Trading Days',
                          yaxis_title='Cumulative Return', template='plotly_dark', height=400)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
