"""
Performance Dashboard
Generates visual performance reports with charts.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.trade_logger import TradeLogger
from src.data.database import get_db_engine

class PerformanceDashboard:
    """
    Generates text-based performance dashboard with key metrics.
    """
    
    def __init__(self):
        self.logger = TradeLogger()
        self.engine = get_db_engine()
        
    def generate_dashboard(self) -> str:
        """Generate full performance dashboard."""
        lines = []
        lines.append("=" * 60)
        lines.append("📊 翠花量化 - 绩效看板")
        lines.append(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 60)
        
        # Overview
        summary = self.logger.get_summary()
        lines.append("\n📈 总览")
        lines.append(f"  总信号数: {summary['total_signals']}")
        lines.append(f"  总订单数: {summary['total_orders']}")
        lines.append(f"  已平仓: {summary['closed_trades']}")
        lines.append(f"  胜率: {summary['win_rate']:.1%}")
        lines.append(f"  总盈亏: ¥{summary['total_pnl']:,.2f}")
        
        # P&L Trend
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
            
            # ASCII chart
            lines.append("\n  📊 盈亏分布")
            max_val = max(abs(p['daily_pnl']) for p in pnl_hist) if pnl_hist else 1
            if max_val == 0:
                max_val = 1
            for p in pnl_hist[-10:]:
                bar_len = int(abs(p['daily_pnl']) / max_val * 20)
                bar = "█" * bar_len
                icon = "🔺" if p['daily_pnl'] >= 0 else "🔻"
                lines.append(f"  {p['date'][-5:]} {icon} {bar} ¥{p['daily_pnl']:,.0f}")
                
        # Top Signals
        recent_signals = self.logger.get_recent_signals(limit=10)
        if recent_signals:
            lines.append("\n🧠 最近信号")
            for sig in recent_signals[:5]:
                icon = "🔺" if sig['direction'] == 'BUY' else "🔻"
                lines.append(f"  {icon} {sig['code']} | {sig['direction']} | Score: {sig['score']:.3f} | {sig['strategy']}")
                
        # Data Coverage
        lines.append("\n📊 数据覆盖")
        try:
            df = pd.read_sql("SELECT code, COUNT(*) as cnt, MAX(date) as last FROM stock_daily GROUP BY code", self.engine)
            if not df.empty:
                lines.append(f"  股票数: {len(df)}")
                lines.append(f"  总记录: {df['cnt'].sum()}")
                lines.append(f"  平均记录: {df['cnt'].mean():.0f}")
                lines.append(f"  最新数据: {df['last'].max()}")
        except:
            lines.append("  无法查询数据库")
            
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
        
    def generate_stock_report(self, code: str) -> str:
        """Generate report for single stock."""
        lines = []
        lines.append(f"📊 {code} 分析报告")
        lines.append("-" * 40)
        
        try:
            df = pd.read_sql(
                f"SELECT * FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 30",
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
            
            # Returns
            ret = close.pct_change().dropna()
            lines.append(f"  日均收益: {ret.mean():.2%}")
            lines.append(f"  日波动率: {ret.std():.2%}")
            lines.append(f"  年化波动: {ret.std() * np.sqrt(252):.2%}")
            
            # Drawdown
            peak = close.cummax()
            dd = (close - peak) / peak
            lines.append(f"  最大回撤: {dd.min():.2%}")
            
        except Exception as e:
            lines.append(f"⚠️ 查询失败: {e}")
            
        return "\n".join(lines)


if __name__ == "__main__":
    dashboard = PerformanceDashboard()
    print(dashboard.generate_dashboard())
