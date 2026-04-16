"""
Performance Report Generator
Generates comprehensive trading reports.
"""

import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.trade_logger import TradeLogger

class PerformanceReporter:
    """Generates daily and weekly performance reports."""
    
    def __init__(self):
        self.logger = TradeLogger()
        
    def daily_report(self, date: str = None) -> str:
        """Generate daily report."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        summary = self.logger.get_summary()
        pnl_hist = self.logger.get_pnl_history(days=7)
        recent = self.logger.get_recent_orders(limit=5)
        
        lines = []
        lines.append("=" * 50)
        lines.append(f"📊 翠花量化 - 每日报告")
        lines.append(f"📅 {date}")
        lines.append("=" * 50)
        
        lines.append(f"\n📈 交易统计")
        lines.append(f"  总信号: {summary['total_signals']}")
        lines.append(f"  总订单: {summary['total_orders']}")
        lines.append(f"  胜率: {summary['win_rate']:.1%}")
        lines.append(f"  总盈亏: ¥{summary['total_pnl']:,.2f}")
        
        if pnl_hist:
            lines.append(f"\n💰 近 7 日盈亏")
            for p in pnl_hist[:7]:
                icon = "🔺" if p['daily_pnl'] >= 0 else "🔻"
                lines.append(f"  {p['date']} | {icon} ¥{p['daily_pnl']:,.2f} ({p['daily_pnl_pct']:+.2f}%)")
                
        if recent:
            lines.append(f"\n📋 最近订单")
            for o in recent:
                icon = "✅" if o['status'] == 'FILLED' else "⏳"
                lines.append(f"  {icon} {o['code']} {o['action']} {o['shares']}股 @ ¥{o['price']:.2f}")
                
        lines.append("=" * 50)
        return "\n".join(lines)
        
    def weekly_report(self) -> str:
        """Generate weekly report."""
        pnl_hist = self.logger.get_pnl_history(days=30)
        summary = self.logger.get_summary()
        
        lines = []
        lines.append("=" * 50)
        lines.append(f"📊 翠花量化 - 周度报告")
        lines.append("=" * 50)
        
        lines.append(f"\n📈 累计统计")
        lines.append(f"  总交易: {summary['total_orders']}")
        lines.append(f"  胜率: {summary['win_rate']:.1%}")
        lines.append(f"  总盈亏: ¥{summary['total_pnl']:,.2f}")
        
        if pnl_hist:
            best = max(pnl_hist, key=lambda x: x['daily_pnl'])
            worst = min(pnl_hist, key=lambda x: x['daily_pnl'])
            avg = sum(p['daily_pnl'] for p in pnl_hist) / len(pnl_hist)
            lines.append(f"\n🏆 最佳: {best['date']} (¥{best['daily_pnl']:,.2f})")
            lines.append(f"📉 最差: {worst['date']} (¥{worst['daily_pnl']:,.2f})")
            lines.append(f"📊 日均: ¥{avg:,.2f}")
            
        lines.append("=" * 50)
        return "\n".join(lines)
