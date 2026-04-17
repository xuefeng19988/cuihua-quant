"""
Phase 103: 回测可视化器 (Backtest Visualizer)

交互式回测结果展示
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BacktestMetrics:
    """回测指标"""
    total_return: float
    annual_return: float
    annual_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_win: float
    avg_loss: float
    avg_trade_duration: float

    def to_dict(self) -> Dict:
        return {
            "total_return": f"{self.total_return:.2%}",
            "annual_return": f"{self.annual_return:.2%}",
            "volatility": f"{self.annual_volatility:.2%}",
            "sharpe_ratio": f"{self.sharpe_ratio:.2f}",
            "sortino_ratio": f"{self.sortino_ratio:.2f}",
            "max_drawdown": f"{self.max_drawdown:.2%}",
            "max_drawdown_days": self.max_drawdown_duration,
            "calmar_ratio": f"{self.calmar_ratio:.2f}",
            "win_rate": f"{self.win_rate:.2%}",
            "profit_factor": f"{self.profit_factor:.2f}",
            "total_trades": self.total_trades,
            "avg_win": f"{self.avg_win:.2%}",
            "avg_loss": f"{self.avg_loss:.2%}",
            "avg_duration": f"{self.avg_trade_duration:.1f}天",
        }


@dataclass
class BacktestEquityCurve:
    """权益曲线"""
    dates: List[str]
    values: List[float]
    benchmark_values: Optional[List[float]] = None

    def to_dict(self) -> Dict:
        return {
            "dates": self.dates,
            "values": self.values,
            "benchmark_values": self.benchmark_values,
        }


@dataclass
class TradeRecord:
    """交易记录"""
    entry_date: str
    exit_date: str
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    quantity: int
    pnl: float
    pnl_pct: float
    holding_days: int

    def to_dict(self) -> Dict:
        return {
            "entry": self.entry_date,
            "exit": self.exit_date,
            "symbol": self.symbol,
            "side": self.side,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "pnl": f"¥{self.pnl:.2f}",
            "pnl_pct": f"{self.pnl_pct:.2%}",
            "holding_days": self.holding_days,
        }


class BacktestVisualizer:
    """回测可视化器"""

    def __init__(self):
        pass

    def generate_summary(
        self,
        metrics: BacktestMetrics,
        equity_curve: BacktestEquityCurve,
        trades: List[TradeRecord],
    ) -> Dict:
        """生成回测总结"""
        return {
            "metrics": metrics.to_dict(),
            "equity_curve": equity_curve.to_dict(),
            "trades_summary": {
                "total_trades": len(trades),
                "winning_trades": sum(1 for t in trades if t.pnl > 0),
                "losing_trades": sum(1 for t in trades if t.pnl < 0),
                "avg_holding_days": sum(t.holding_days for t in trades) / len(trades) if trades else 0,
                "largest_win": max((t.pnl for t in trades), default=0),
                "largest_loss": min((t.pnl for t in trades), default=0),
            },
            "trades": [t.to_dict() for t in trades[:20]],  # 最近 20 笔
        }

    def generate_monthly_returns(self, equity_curve: BacktestEquityCurve) -> List[Dict]:
        """生成月度收益表"""
        if not equity_curve.dates:
            return []

        monthly_returns = {}

        for i, date_str in enumerate(equity_curve.dates):
            date = datetime.strptime(date_str, "%Y-%m-%d")
            key = date.strftime("%Y-%m")

            if key not in monthly_returns:
                monthly_returns[key] = {"start": equity_curve.values[i], "end": equity_curve.values[i]}
            else:
                monthly_returns[key]["end"] = equity_curve.values[i]

        result = []
        for month, values in sorted(monthly_returns.items()):
            ret = (values["end"] - values["start"]) / values["start"] if values["start"] > 0 else 0
            result.append({
                "month": month,
                "return": f"{ret:.2%}",
                "start_value": f"¥{values['start']:,.2f}",
                "end_value": f"¥{values['end']:,.2f}",
            })

        return result

    def generate_drawdown_analysis(self, equity_curve: BacktestEquityCurve) -> List[Dict]:
        """生成回撤分析"""
        if not equity_curve.values:
            return []

        drawdowns = []
        peak = equity_curve.values[0]
        peak_date = equity_curve.dates[0]
        drawdown_start = None

        for i, value in enumerate(equity_curve.values):
            if value > peak:
                # 新的峰值
                if drawdown_start is not None:
                    drawdowns.append({
                        "start_date": drawdown_start,
                        "end_date": equity_curve.dates[i],
                        "peak_value": peak,
                        "trough_value": min(equity_curve.values[equity_curve.dates.index(drawdown_start):i]) if i > equity_curve.dates.index(drawdown_start) else peak,
                        "drawdown_pct": f"{(min(equity_curve.values[equity_curve.dates.index(drawdown_start):i]) - peak) / peak:.2%}" if i > equity_curve.dates.index(drawdown_start) else "0%",
                        "duration_days": i - equity_curve.dates.index(drawdown_start),
                    })
                peak = value
                peak_date = equity_curve.dates[i]
                drawdown_start = None
            elif value < peak and drawdown_start is None:
                drawdown_start = equity_curve.dates[i]

        return drawdowns

    def generate_trade_analysis(self, trades: List[TradeRecord]) -> Dict:
        """生成交易分析"""
        if not trades:
            return {"error": "No trades"}

        winning = [t for t in trades if t.pnl > 0]
        losing = [t for t in trades if t.pnl < 0]

        return {
            "total_trades": len(trades),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": f"{len(winning) / len(trades):.2%}",
            "avg_win": f"¥{sum(t.pnl for t in winning) / len(winning):.2f}" if winning else "N/A",
            "avg_loss": f"¥{sum(t.pnl for t in losing) / len(losing):.2f}" if losing else "N/A",
            "profit_factor": f"{abs(sum(t.pnl for t in winning) / sum(t.pnl for t in losing)):.2f}" if losing and sum(t.pnl for t in losing) != 0 else "N/A",
            "avg_holding_days": f"{sum(t.holding_days for t in trades) / len(trades):.1f}",
            "by_symbol": self._group_trades_by_symbol(trades),
            "by_month": self._group_trades_by_month(trades),
        }

    def _group_trades_by_symbol(self, trades: List[TradeRecord]) -> Dict:
        """按股票分组"""
        groups = {}
        for t in trades:
            if t.symbol not in groups:
                groups[t.symbol] = {"trades": 0, "pnl": 0}
            groups[t.symbol]["trades"] += 1
            groups[t.symbol]["pnl"] += t.pnl

        return {k: {"trades": v["trades"], "pnl": f"¥{v['pnl']:.2f}"} for k, v in groups.items()}

    def _group_trades_by_month(self, trades: List[TradeRecord]) -> Dict:
        """按月份分组"""
        groups = {}
        for t in trades:
            month = t.entry_date[:7]  # YYYY-MM
            if month not in groups:
                groups[month] = {"trades": 0, "pnl": 0}
            groups[month]["trades"] += 1
            groups[month]["pnl"] += t.pnl

        return {k: {"trades": v["trades"], "pnl": f"¥{v['pnl']:.2f}"} for k, v in sorted(groups.items())}
