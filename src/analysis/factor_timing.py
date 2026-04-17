"""
Phase 90: 因子择时系统 (Factor Timing System)

动态因子权重调整，捕捉因子轮动机会
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class FactorRegime(Enum):
    """因子状态"""
    OUTPERFORMING = "表现优异"
    UNDERPERFORMING = "表现不佳"
    NEUTRAL = "中性"
    TRANSITIONING = "转换中"


@dataclass
class FactorSignal:
    """因子信号"""
    factor_name: str
    current_return: float
    momentum_1m: float
    momentum_3m: float
    momentum_6m: float
    volatility: float
    sharpe_ratio: float
    regime: FactorRegime
    timing_score: float  # -1 ~ 1

    def to_dict(self) -> Dict:
        return {
            "factor": self.factor_name,
            "current_return": f"{self.current_return:.2%}",
            "momentum_1m": f"{self.momentum_1m:.2%}",
            "momentum_3m": f"{self.momentum_3m:.2%}",
            "momentum_6m": f"{self.momentum_6m:.2%}",
            "volatility": f"{self.volatility:.2%}",
            "sharpe_ratio": f"{self.sharpe_ratio:.2f}",
            "regime": self.regime.value,
            "timing_score": f"{self.timing_score:.2f}",
        }


@dataclass
class FactorAllocation:
    """因子配置"""
    factor_name: str
    target_weight: float
    current_weight: float
    rebalance_needed: bool
    signal_strength: float

    def to_dict(self) -> Dict:
        return {
            "factor": self.factor_name,
            "target_weight": f"{self.target_weight:.2%}",
            "current_weight": f"{self.current_weight:.2%}",
            "rebalance_needed": self.rebalance_needed,
            "signal_strength": f"{self.signal_strength:.2f}",
        }


class FactorTimingSystem:
    """因子择时系统"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.lookback_period = self.config.get("lookback_period", 12)  # 月
        self.rebalance_threshold = self.config.get("rebalance_threshold", 0.05)  # 5%

    def analyze_factors(
        self,
        factor_returns: Dict[str, List[float]],  # {factor: [monthly_returns]}
    ) -> List[FactorSignal]:
        """
        分析所有因子信号

        Args:
            factor_returns: 因子收益数据

        Returns:
            因子信号列表
        """
        signals = []

        for factor_name, returns in factor_returns.items():
            if len(returns) < 3:
                continue

            # 计算动量
            momentum_1m = returns[-1] if len(returns) >= 1 else 0
            momentum_3m = sum(returns[-3:]) / 3 if len(returns) >= 3 else 0
            momentum_6m = sum(returns[-6:]) / 6 if len(returns) >= 6 else 0

            # 计算波动率和夏普
            import statistics
            volatility = statistics.stdev(returns) if len(returns) > 1 else 0
            avg_return = sum(returns) / len(returns)
            sharpe = avg_return / volatility if volatility > 0 else 0

            # 判断因子状态
            regime = self._determine_regime(momentum_1m, momentum_3m, momentum_6m)

            # 计算择时得分
            timing_score = self._calculate_timing_score(
                momentum_1m, momentum_3m, momentum_6m, sharpe
            )

            signal = FactorSignal(
                factor_name=factor_name,
                current_return=returns[-1],
                momentum_1m=momentum_1m,
                momentum_3m=momentum_3m,
                momentum_6m=momentum_6m,
                volatility=volatility,
                sharpe_ratio=sharpe,
                regime=regime,
                timing_score=timing_score,
            )
            signals.append(signal)

        return signals

    def allocate_factors(
        self,
        signals: List[FactorSignal],
        current_weights: Dict[str, float],
    ) -> List[FactorAllocation]:
        """
        配置因子权重

        Args:
            signals: 因子信号
            current_weights: 当前权重

        Returns:
            因子配置建议
        """
        allocations = []

        # 基于择时得分计算目标权重
        positive_signals = [s for s in signals if s.timing_score > 0]
        negative_signals = [s for s in signals if s.timing_score <= 0]

        total_positive_score = sum(s.timing_score for s in positive_signals)

        for signal in signals:
            current_weight = current_weights.get(signal.factor_name, 0)

            if signal.timing_score > 0 and total_positive_score > 0:
                # 正向信号：按得分比例分配
                target_weight = (signal.timing_score / total_positive_score) * 0.8
            else:
                # 负向信号：降低权重
                target_weight = 0.05  # 最低配置

            # 检查是否需要再平衡
            rebalance_needed = abs(target_weight - current_weight) > self.rebalance_threshold

            allocation = FactorAllocation(
                factor_name=signal.factor_name,
                target_weight=target_weight,
                current_weight=current_weight,
                rebalance_needed=rebalance_needed,
                signal_strength=signal.timing_score,
            )
            allocations.append(allocation)

        return allocations

    def _determine_regime(
        self,
        momentum_1m: float,
        momentum_3m: float,
        momentum_6m: float,
    ) -> FactorRegime:
        """判断因子状态"""
        if momentum_1m > 0.05 and momentum_3m > 0:
            return FactorRegime.OUTPERFORMING
        elif momentum_1m < -0.05 and momentum_3m < 0:
            return FactorRegime.UNDERPERFORMING
        elif abs(momentum_1m) < 0.02:
            return FactorRegime.NEUTRAL
        else:
            return FactorRegime.TRANSITIONING

    def _calculate_timing_score(
        self,
        momentum_1m: float,
        momentum_3m: float,
        momentum_6m: float,
        sharpe: float,
    ) -> float:
        """计算择时得分"""
        # 动量加权平均
        momentum_score = (
            momentum_1m * 0.5 +
            momentum_3m * 0.3 +
            momentum_6m * 0.2
        )

        # 风险调整
        risk_adjustment = sharpe * 0.1

        # 综合得分
        score = momentum_score + risk_adjustment

        # 归一化到 -1 ~ 1
        return max(-1, min(1, score))

    def generate_report(
        self,
        signals: List[FactorSignal],
        allocations: List[FactorAllocation],
    ) -> Dict:
        """生成因子择时报告"""
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "factor_signals": [s.to_dict() for s in signals],
            "factor_allocations": [a.to_dict() for a in allocations],
            "summary": {
                "total_factors": len(signals),
                "outperforming": sum(1 for s in signals if s.regime == FactorRegime.OUTPERFORMING),
                "underperforming": sum(1 for s in signals if s.regime == FactorRegime.UNDERPERFORMING),
                "rebalance_needed": sum(1 for a in allocations if a.rebalance_needed),
                "avg_timing_score": sum(s.timing_score for s in signals) / len(signals) if signals else 0,
            },
        }
