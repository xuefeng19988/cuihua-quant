"""
Phase 95: 交易行为分析系统 (Trading Behavior Analysis)

分析投资者行为偏差，优化交易决策
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class BehaviorBias(Enum):
    """行为偏差"""
    OVERCONFIDENCE = "过度自信"
    LOSS_AVERSION = "损失厌恶"
    HERDING = "羊群效应"
    ANCHORING = "锚定效应"
    RECENCY = "近因效应"
    DISPOSITION_EFFECT = "处置效应"
    GAMBLING_FALLACY = "赌徒谬误"


@dataclass
BehaviorPattern:
    """行为模式"""
    bias_type: BehaviorBias
    description: str
    severity: float  # 0-1
    examples: List[str]
    recommendation: str

    def to_dict(self) -> Dict:
        return {
            "bias": self.bias_type.value,
            "description": self.description,
            "severity": f"{self.severity:.1%}",
            "examples": self.examples,
            "recommendation": self.recommendation,
        }


@dataclass
class TradingBehaviorReport:
    """交易行为报告"""
    trader_id: str
    period: str
    total_trades: int
    win_rate: float
    avg_holding_period: float
    behavior_patterns: List[BehaviorPattern]
    overall_risk_score: float  # 0-1
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            "trader_id": self.trader_id,
            "period": self.period,
            "total_trades": self.total_trades,
            "win_rate": f"{self.win_rate:.2%}",
            "avg_holding_period": f"{self.avg_holding_period:.1f}天",
            "behavior_patterns": [p.to_dict() for p in self.behavior_patterns],
            "overall_risk_score": f"{self.overall_risk_score:.2f}",
            "recommendations": self.recommendations,
        }


class TradingBehaviorAnalyzer:
    """交易行为分析器"""

    def __init__(self):
        pass

    def analyze_behavior(
        self,
        trader_id: str,
        trade_history: List[Dict],
        period: str = "2024-Q1",
    ) -> TradingBehaviorReport:
        """
        分析交易行为

        Args:
            trader_id: 交易者 ID
            trade_history: 交易历史
            period: 时间段

        Returns:
            行为报告
        """
        if not trade_history:
            return TradingBehaviorReport(
                trader_id=trader_id,
                period=period,
                total_trades=0,
                win_rate=0,
                avg_holding_period=0,
                behavior_patterns=[],
                overall_risk_score=0,
                recommendations=[],
            )

        total_trades = len(trade_history)
        winning_trades = sum(1 for t in trade_history if t.get("pnl", 0) > 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        avg_holding_period = sum(
            t.get("holding_days", 0) for t in trade_history
        ) / total_trades

        # 检测行为模式
        patterns = []
        patterns.extend(self._detect_disposition_effect(trade_history))
        patterns.extend(self._detect_overconfidence(trade_history, win_rate))
        patterns.extend(self._detect_herding(trade_history))
        patterns.extend(self._detect_loss_aversion(trade_history))

        # 计算整体风险分数
        risk_score = sum(p.severity for p in patterns) / len(patterns) if patterns else 0

        # 生成建议
        recommendations = self._generate_recommendations(patterns)

        return TradingBehaviorReport(
            trader_id=trader_id,
            period=period,
            total_trades=total_trades,
            win_rate=win_rate,
            avg_holding_period=avg_holding_period,
            behavior_patterns=patterns,
            overall_risk_score=risk_score,
            recommendations=recommendations,
        )

    def _detect_disposition_effect(self, trades: List[Dict]) -> List[BehaviorPattern]:
        """检测处置效应（过早获利了结，过晚止损）"""
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in trades if t.get("pnl", 0) < 0]

        if not winning_trades or not losing_trades:
            return []

        avg_win_holding = sum(t.get("holding_days", 0) for t in winning_trades) / len(winning_trades)
        avg_lose_holding = sum(t.get("holding_days", 0) for t in losing_trades) / len(losing_trades)

        # 处置效应：获利持仓时间短于亏损
        if avg_lose_holding > avg_win_holding * 1.5:
            severity = min((avg_lose_holding - avg_win_holding) / avg_win_holding, 1.0)
            return [
                BehaviorPattern(
                    bias_type=BehaviorBias.DISPOSITION_EFFECT,
                    description="处置效应：持有亏损头寸时间过长，过早获利了结",
                    severity=severity,
                    examples=[
                        f"平均获利持仓：{avg_win_holding:.1f}天",
                        f"平均亏损持仓：{avg_lose_holding:.1f}天",
                    ],
                    recommendation="设定固定持仓时间限制，避免情绪化决策",
                )
            ]

        return []

    def _detect_overconfidence(self, trades: List[Dict], win_rate: float) -> List[BehaviorPattern]:
        """检测过度自信"""
        if len(trades) < 10:
            return []

        # 高胜率 + 高交易频率 = 可能过度自信
        trade_frequency = len(trades) / 30  # 每月交易次数

        if win_rate > 0.7 and trade_frequency > 10:
            return [
                BehaviorPattern(
                    bias_type=BehaviorBias.OVERCONFIDENCE,
                    description="过度自信：高胜率导致交易过于频繁",
                    severity=min(win_rate - 0.7, 0.5) * 2,
                    examples=[
                        f"胜率：{win_rate:.1%}",
                        f"月交易频率：{trade_frequency:.0f}次",
                    ],
                    recommendation="降低交易频率，等待高确定性机会",
                )
            ]

        return []

    def _detect_herding(self, trades: List[Dict]) -> List[BehaviorPattern]:
        """检测羊群效应"""
        # 简化：检测是否集中交易热门股票
        symbol_counts = {}
        for t in trades:
            symbol = t.get("symbol", "")
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

        if not symbol_counts:
            return []

        max_concentration = max(symbol_counts.values()) / len(trades)

        if max_concentration > 0.5:
            return [
                BehaviorPattern(
                    bias_type=BehaviorBias.HERDING,
                    description="羊群效应：过度集中于少数股票",
                    severity=max_concentration - 0.5,
                    examples=[
                        f"最集中股票占比：{max_concentration:.1%}",
                    ],
                    recommendation="分散投资，避免过度集中",
                )
            ]

        return []

    def _detect_loss_aversion(self, trades: List[Dict]) -> List[BehaviorPattern]:
        """检测损失厌恶"""
        losing_trades = [t for t in trades if t.get("pnl", 0) < 0]

        if not losing_trades:
            return []

        # 检测是否在亏损后减少交易
        avg_loss_size = sum(abs(t.get("pnl", 0)) for t in losing_trades) / len(losing_trades)

        if avg_loss_size > 0.1:  # 平均亏损超过 10%
            return [
                BehaviorPattern(
                    bias_type=BehaviorBias.LOSS_AVERSION,
                    description="损失厌恶：对亏损过度敏感",
                    severity=min(avg_loss_size / 0.2, 1.0),
                    examples=[
                        f"平均亏损幅度：{avg_loss_size:.1%}",
                    ],
                    recommendation="接受合理亏损，严格执行止损",
                )
            ]

        return []

    def _generate_recommendations(self, patterns: List[BehaviorPattern]) -> List[str]:
        """生成综合建议"""
        recommendations = []

        if any(p.bias_type == BehaviorBias.DISPOSITION_EFFECT for p in patterns):
            recommendations.append("📊 实施固定持仓时间规则")

        if any(p.bias_type == BehaviorBias.OVERCONFIDENCE for p in patterns):
            recommendations.append("🎯 降低交易频率，提高筛选标准")

        if any(p.bias_type == BehaviorBias.HERDING for p in patterns):
            recommendations.append("🔄 增加持仓分散度")

        if any(p.bias_type == BehaviorBias.LOSS_AVERSION for p in patterns):
            recommendations.append("💪 接受亏损是交易的一部分")

        if not recommendations:
            recommendations.append("✅ 交易行为健康，继续保持")

        return recommendations
