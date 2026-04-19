"""
Phase 81: 智能仓位管理系统 (Intelligent Position Sizing)

基于多维度信号的动态仓位调整
"""


from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum


class PositionMethod(Enum):
    """仓位计算方法"""
    KELLY = "kelly"  # 凯利公式
    OPTIMAL_F = "optimal_f"  # 最优 f
    RISK_PARITY = "risk_parity"  # 风险平价
    VOLATILITY_TARGET = "volatility_target"  # 波动率目标
    FIXED_FRACTION = "fixed_fraction"  # 固定比例


@dataclass
class PositionSignal:
    """仓位信号"""
    symbol: str
    signal_strength: float  # -1.0 ~ 1.0
    confidence: float  # 0.0 ~ 1.0
    volatility: float  # 年化波动率
    correlation: float = 0.0  # 与组合的相关性
    liquidity_score: float = 1.0  # 流动性评分


class IntelligentPositionSizer:
    """智能仓位管理器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.max_position = self.config.get("max_position", 0.2)  # 单票最大 20%
        self.max_portfolio_risk = self.config.get("max_portfolio_risk", 0.15)  # 组合最大风险 15%
        self.target_volatility = self.config.get("target_volatility", 0.15)  # 目标波动率 15%
        self.risk_free_rate = self.config.get("risk_free_rate", 0.03)  # 无风险利率 3%

    def calculate_position(
        self,
        signal: PositionSignal,
        method: PositionMethod = PositionMethod.KELLY,
        portfolio_value: float = 1_000_000,
        current_positions: Optional[Dict] = None,
    ) -> float:
        """
        计算仓位大小

        Args:
            signal: 仓位信号
            method: 计算方法
            portfolio_value: 组合总价值
            current_positions: 当前持仓

        Returns:
            建议仓位比例 (0.0 ~ max_position)
        """
        if method == PositionMethod.KELLY:
            position = self._kelly_criterion(signal, portfolio_value)
        elif method == PositionMethod.OPTIMAL_F:
            position = self._optimal_f(signal, portfolio_value)
        elif method == PositionMethod.RISK_PARITY:
            position = self._risk_parity(signal, portfolio_value, current_positions)
        elif method == PositionMethod.VOLATILITY_TARGET:
            position = self._volatility_target(signal, portfolio_value)
        else:  # FIXED_FRACTION
            position = self._fixed_fraction(signal, portfolio_value)

        # 应用限制
        position = min(position, self.max_position)
        position = max(position, 0.0)

        return position

    def _kelly_criterion(self, signal: PositionSignal, portfolio_value: float) -> float:
        """
        凯利公式：f* = (bp - q) / b
        b: 盈亏比
        p: 胜率
        q: 1 - p
        """
        # 从信号强度和置信度估算胜率和盈亏比
        win_rate = 0.5 + signal.signal_strength * 0.2 * signal.confidence
        win_rate = max(0.5, min(0.8, win_rate))  # 限制在 50%~80%

        avg_win = signal.volatility * 0.8
        avg_loss = signal.volatility * 0.6
        odds = avg_win / avg_loss if avg_loss > 0 else 1.5

        # 凯利公式
        kelly_fraction = ((odds * win_rate) - (1 - win_rate)) / odds

        # 半凯利（更保守）
        return kelly_fraction * 0.5

    def _optimal_f(self, signal: PositionSignal, portfolio_value: float) -> float:
        """
        最优 f 方法
        基于历史交易记录寻找最优固定分数
        """
        # 简化实现：基于信号调整
        base_fraction = 0.1
        adjustment = signal.signal_strength * signal.confidence * 0.1
        return base_fraction + adjustment

    def _risk_parity(
        self,
        signal: PositionSignal,
        portfolio_value: float,
        current_positions: Optional[Dict],
    ) -> float:
        """
        风险平价方法
        使每个资产对组合的风险贡献相等
        """
        if current_positions is None or len(current_positions) == 0:
            # 无持仓时，基于波动率倒数加权
            inv_vol = 1.0 / signal.volatility if signal.volatility > 0 else 1.0
            return inv_vol * 0.1  # 缩放因子

        # 计算当前组合风险
        total_risk = sum(
            pos.get("volatility", 0.15) * pos.get("weight", 0.1)
            for pos in current_positions.values()
        )

        # 新资产的风险贡献
        new_risk = signal.volatility * (1 - signal.correlation)

        # 风险平价权重
        target_weight = total_risk / (len(current_positions) + 1) / signal.volatility
        return target_weight

    def _volatility_target(self, signal: PositionSignal, portfolio_value: float) -> float:
        """
        波动率目标方法
        调整仓位使组合波动率达到目标值
        """
        if signal.volatility <= 0:
            return 0.0

        # 目标仓位 = 目标波动率 / 资产波动率
        target_weight = self.target_volatility / signal.volatility

        # 根据信号强度调整
        target_weight *= abs(signal.signal_strength)

        return target_weight

    def _fixed_fraction(self, signal: PositionSignal, portfolio_value: float) -> float:
        """固定比例方法"""
        base_fraction = 0.05  # 基础 5%
        adjustment = signal.signal_strength * signal.confidence * 0.1
        return base_fraction + adjustment

    def calculate_portfolio_positions(
        self,
        signals: List[PositionSignal],
        portfolio_value: float = 1_000_000,
        method: PositionMethod = PositionMethod.KELLY,
    ) -> Dict[str, float]:
        """
        计算整个组合的仓位分配

        Args:
            signals: 所有资产信号
            portfolio_value: 组合总价值
            method: 计算方法

        Returns:
            {symbol: weight}
        """
        positions = {}
        total_weight = 0.0

        for signal in signals:
            weight = self.calculate_position(signal, method, portfolio_value)
            positions[signal.symbol] = weight
            total_weight += weight

        # 归一化（如果总权重超过 1）
        if total_weight > 1.0:
            for symbol in positions:
                positions[symbol] /= total_weight

        return positions
