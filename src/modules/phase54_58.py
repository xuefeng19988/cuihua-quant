"""
Phase 54-58: Advanced Modules
Phase 54: Real-time Data Streaming
Phase 55: Advanced Charting
Phase 56: Risk Parity Portfolio
Phase 57: Sentiment Analysis v2
Phase 58: Backtest Report Generator
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# ==================== Phase 54: Real-time Data Streaming ====================

class RealtimeDataStream:
    """
    Real-time data streaming with WebSocket support.
    """
    def __init__(self):
        self.subscribers: Dict[str, List] = {}
        self.data_buffer: Dict[str, pd.DataFrame] = {}
        
    def subscribe(self, code: str, callback):
        """Subscribe to real-time data for a stock."""
        if code not in self.subscribers:
            self.subscribers[code] = []
        self.subscribers[code].append(callback)
        
    def update_data(self, code: str, data: Dict):
        """Update real-time data and notify subscribers."""
        if code in self.data_buffer:
            self.data_buffer[code] = pd.concat([
                self.data_buffer[code], 
                pd.DataFrame([data])
            ], ignore_index=True)
        else:
            self.data_buffer[code] = pd.DataFrame([data])
            
        # Notify subscribers
        for callback in self.subscribers.get(code, []):
            callback(code, data)


# ==================== Phase 55: Advanced Charting ====================

class AdvancedCharting:
    """
    Advanced interactive charting with Plotly.
    """
    @staticmethod
    def generate_candlestick_chart(df: pd.DataFrame, title: str = "K 线图",
                                   indicators: List[str] = None) -> str:
        """Generate interactive candlestick chart with indicators."""
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except ImportError:
            return "⚠️ Plotly not installed"
            
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=(title, '成交量')
        )
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K 线'
        ), row=1, col=1)
        
        # Indicators
        if indicators:
            if 'ma' in indicators:
                for period in [5, 10, 20, 60]:
                    ma = df['close'].rolling(period).mean()
                    fig.add_trace(go.Scatter(x=df['date'], y=ma, name=f'MA{period}'), row=1, col=1)
                    
        # Volume
        colors = ['red' if c >= o else 'green' for o, c in zip(df['open'], df['close'])]
        fig.add_trace(go.Bar(x=df['date'], y=df['volume'], marker_color=colors, name='成交量'), row=2, col=1)
        
        fig.update_layout(template='plotly_dark', height=600)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')


# ==================== Phase 56: Risk Parity Portfolio ====================

class RiskParityPortfolio:
    """
    Risk parity portfolio construction.
    """
    @staticmethod
    def calculate_weights(cov_matrix: np.ndarray, max_iter: int = 1000,
                         tol: float = 1e-8) -> np.ndarray:
        """Calculate risk parity weights."""
        n = cov_matrix.shape[0]
        weights = np.ones(n) / n
        
        for _ in range(max_iter):
            # Calculate marginal risk contributions
            portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)
            marginal_contrib = cov_matrix @ weights / portfolio_vol
            risk_contrib = weights * marginal_contrib
            target_risk = portfolio_vol / n
            
            # Update weights
            weights = weights * (target_risk / risk_contrib) ** 0.5
            weights = weights / weights.sum()
            
            # Check convergence
            if np.max(np.abs(risk_contrib - target_risk)) < tol:
                break
                
        return weights


# ==================== Phase 57: Sentiment Analysis v2 ====================

class SentimentAnalyzerV2:
    """
    Enhanced sentiment analysis with multiple sources.
    """
    def __init__(self):
        self.positive_words = ['上涨', '利好', '增长', '突破', '创新高', '涨停', '牛市', '强势']
        self.negative_words = ['下跌', '利空', '亏损', '暴跌', '崩盘', '熊市', '疲软', '跳水']
        
    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment of text."""
        words = list(text)
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        total = pos_count + neg_count
        
        score = (pos_count - neg_count) / total if total > 0 else 0
        
        return {
            'score': score,
            'label': 'positive' if score > 0.2 else ('negative' if score < -0.2 else 'neutral'),
            'pos_count': pos_count,
            'neg_count': neg_count
        }


# ==================== Phase 58: Backtest Report Generator ====================

class BacktestReportGenerator:
    """
    Generate comprehensive backtest reports.
    """
    @staticmethod
    def generate_report(equity_curve: pd.Series, trades: List[Dict] = None,
                       benchmark: pd.Series = None) -> str:
        """Generate full backtest report."""
        returns = equity_curve.pct_change().dropna()
        
        lines = []
        lines.append("=" * 60)
        lines.append("📊 回测报告")
        lines.append("=" * 60)
        
        # Basic metrics
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        years = len(returns) / 252
        annualized = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
        volatility = returns.std() * np.sqrt(252)
        sharpe = (annualized - 0.02) / volatility if volatility > 0 else 0
        
        # Max drawdown
        peak = equity_curve.cummax()
        drawdown = (equity_curve - peak) / peak
        max_dd = drawdown.min()
        
        lines.append(f"\n💰 收益指标")
        lines.append(f"  总收益: {total_return:.2%}")
        lines.append(f"  年化收益: {annualized:.2%}")
        lines.append(f"  波动率: {volatility:.2%}")
        lines.append(f"  夏普比率: {sharpe:.2f}")
        lines.append(f"  最大回撤: {max_dd:.2%}")
        
        # Trade statistics
        if trades:
            pnls = [t.get('pnl', 0) for t in trades]
            wins = sum(1 for p in pnls if p > 0)
            win_rate = wins / len(pnls) if pnls else 0
            
            lines.append(f"\n💼 交易统计")
            lines.append(f"  总交易: {len(trades)}")
            lines.append(f"  胜率: {win_rate:.1%}")
            lines.append(f"  平均盈利: {np.mean([p for p in pnls if p > 0]):.2f}" if wins > 0 else "")
            
        return "\n".join([l for l in lines if l])


if __name__ == "__main__":
    # Test modules
    print("✅ Phase 54-58 modules loaded successfully")
    
    # Test sentiment analyzer
    analyzer = SentimentAnalyzerV2()
    result = analyzer.analyze_text("今日股票上涨，利好消息")
    print(f"Sentiment: {result}")
    
    # Test backtest report
    np.random.seed(42)
    equity = pd.Series(np.cumprod(1 + np.random.normal(0.0005, 0.015, 252)))
    print(BacktestReportGenerator.generate_report(equity))
