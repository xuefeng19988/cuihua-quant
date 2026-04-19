"""
Phase 25: Internationalization (i18n)
Multi-language support for CLI and Web UI.
"""

import os
import sys
from typing import Dict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class I18nManager:
    """
    Internationalization manager.
    Supports Chinese (zh) and English (en).
    """
    
    def __init__(self, default_lang: str = "zh"):
        self.current_lang = default_lang
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
        
    def _load_translations(self) -> None:
        """Load translation dictionaries."""
        self.translations = {
            "en": {
                # CLI messages
                "sync_data": "Syncing market data...",
                "analyze_stocks": "Analyzing {count} stocks...",
                "generating_signals": "Generating signals...",
                "running_backtest": "Running backtest...",
                "executing_pipeline": "Running Trading Pipeline...",
                "portfolio_allocation": "Portfolio Allocation",
                "daily_report": "Daily Performance Report",
                "system_status": "System Status",
                "database": "Database",
                "records": "records",
                "futu_connected": "Futu OpenD: Connected",
                "futu_disconnected": "Futu OpenD: Not connected",
                "config": "Config",
                "missing": "missing",
                
                # Trading messages
                "buy": "BUY",
                "sell": "SELL",
                "hold": "HOLD",
                "stop_loss": "STOP-LOSS",
                "take_profit": "TAKE-PROFIT",
                "position": "Position",
                "pnl": "P&L",
                "portfolio_value": "Portfolio Value",
                "cash": "Cash",
                "positions_count": "Positions",
                "trades_today": "Trades Today",
                
                # Error messages
                "error": "Error",
                "warning": "Warning",
                "success": "Success",
                "no_data": "No data available",
                "no_signals": "No signals generated",
                "connection_failed": "Connection failed",
                
                # Report headers
                "backtest_report": "Backtest Comparison Report",
                "performance_summary": "Performance Summary",
                "top_performers": "Top Performers",
                "avg_return": "Avg Return",
                "avg_sharpe": "Avg Sharpe",
                "avg_drawdown": "Avg MaxDD",
            },
            "zh": {
                # CLI messages
                "sync_data": "📥 同步市场数据...",
                "analyze_stocks": "🔍 分析 {count} 只股票...",
                "generating_signals": "🧠 生成信号...",
                "running_backtest": "📉 运行回测...",
                "executing_pipeline": "🚀 运行交易流水线...",
                "portfolio_allocation": "💼 组合配置",
                "daily_report": "📊 每日绩效报告",
                "system_status": "📊 系统状态",
                "database": "✅ 数据库",
                "records": "条记录",
                "futu_connected": "✅ Futu OpenD: 已连接",
                "futu_disconnected": "⚠️ Futu OpenD: 未连接",
                "config": "配置",
                "missing": "缺失",
                
                # Trading messages
                "buy": "买入",
                "sell": "卖出",
                "hold": "持有",
                "stop_loss": "止损",
                "take_profit": "止盈",
                "position": "持仓",
                "pnl": "盈亏",
                "portfolio_value": "投资组合",
                "cash": "现金",
                "positions_count": "持仓数",
                "trades_today": "今日交易",
                
                # Error messages
                "error": "错误",
                "warning": "警告",
                "success": "成功",
                "no_data": "无数据",
                "no_signals": "无信号生成",
                "connection_failed": "连接失败",
                
                # Report headers
                "backtest_report": "📊 回测对比报告",
                "performance_summary": "📈 组合摘要",
                "top_performers": "🏆 最佳表现",
                "avg_return": "平均收益",
                "avg_sharpe": "平均夏普",
                "avg_drawdown": "平均回撤",
            }
        }
        
    def set_language(self, lang: str) -> None:
        """Set current language."""
        if lang in self.translations:
            self.current_lang = lang
            
    def get(self, key: str, **kwargs) -> str:
        """Get translated string."""
        translations = self.translations.get(self.current_lang, {})
        text = translations.get(key, key)
        
        # Format with kwargs
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
                
        return text
        
    def t(self, key: str, **kwargs) -> str:
        """Alias for get()."""
        return self.get(key, **kwargs)
        
    def get_supported_languages(self) -> list:
        """Get list of supported languages."""
        return list(self.translations.keys())
        
    def generate_report(self) -> str:
        """Generate i18n status report."""
        lines = []
        lines.append("=" * 50)
        lines.append("🌍 国际化支持报告")
        lines.append("=" * 50)
        
        lines.append(f"\n📊 支持语言: {len(self.translations)}")
        for lang in self.translations:
            count = len(self.translations[lang])
            icon = "✅" if lang == self.current_lang else "  "
            lines.append(f"  {icon} {lang}: {count} 条翻译")
            
        return "\n".join(lines)


# Global i18n instance
i18n = I18nManager()
