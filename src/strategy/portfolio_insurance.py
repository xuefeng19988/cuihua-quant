"""
Phase 94: 组合保险策略 (Portfolio Insurance Strategies)

CPPI/TIPP 保本策略，保护组合本金
"""


from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class CPPIConfig:
    """CPPI 配置"""
    floor_rate: float = 0.9  # 保本线 90%
    multiplier: float = 3.0  # 乘数
    rebalance_frequency: str = "daily"  # 再平衡频率


@dataclass
class PortfolioInsuranceResult:
    """组合保险结果"""
    strategy: str  # CPPI/TIPP
    portfolio_value: float
    floor_value: float
    cushion: float  # 缓冲垫
    risky_allocation: float  # 风险资产比例
    risk_free_allocation: float  # 无风险资产比例
    target_exposure: float
    current_exposure: float
    rebalance_needed: bool

    def to_dict(self) -> Dict:
        return {
            "strategy": self.strategy,
            "portfolio_value": f"¥{self.portfolio_value:.2f}",
            "floor_value": f"¥{self.floor_value:.2f}",
            "cushion": f"¥{self.cushion:.2f}",
            "risky_allocation_pct": f"{self.risky_allocation:.2%}",
            "risk_free_allocation_pct": f"{self.risk_free_allocation:.2%}",
            "target_exposure": f"¥{self.target_exposure:.2f}",
            "current_exposure": f"¥{self.current_exposure:.2f}",
            "rebalance_needed": self.rebalance_needed,
        }


class PortfolioInsuranceStrategy:
    """组合保险策略"""

    def __init__(self, config: Optional[CPPIConfig] = None):
        self.config = config or CPPIConfig()

    def calculate_cppi(
        self,
        portfolio_value: float,
        initial_value: float,
        current_risky_exposure: float,
        risk_free_rate: float = 0.03,
    ) -> PortfolioInsuranceResult:
        """
        CPPI 策略（Constant Proportion Portfolio Insurance）

        Args:
            portfolio_value: 当前组合价值
            initial_value: 初始价值
            current_risky_exposure: 当前风险资产敞口
            risk_free_rate: 无风险利率

        Returns:
            保险结果
        """
        # 计算保本线
        floor_value = initial_value * self.config.floor_rate

        # 计算缓冲垫
        cushion = portfolio_value - floor_value

        # 计算风险资产配置
        target_exposure = cushion * self.config.multiplier
        target_exposure = max(0, min(target_exposure, portfolio_value))

        # 风险资产比例
        risky_allocation = target_exposure / portfolio_value if portfolio_value > 0 else 0
        risk_free_allocation = 1 - risky_allocation

        # 检查是否需要再平衡
        rebalance_needed = abs(target_exposure - current_risky_exposure) > portfolio_value * 0.05

        return PortfolioInsuranceResult(
            strategy="CPPI",
            portfolio_value=portfolio_value,
            floor_value=floor_value,
            cushion=cushion,
            risky_allocation=risky_allocation,
            risk_free_allocation=risk_free_allocation,
            target_exposure=target_exposure,
            current_exposure=current_risky_exposure,
            rebalance_needed=rebalance_needed,
        )

    def calculate_tipp(
        self,
        portfolio_value: float,
        initial_value: float,
        highest_value: float,
        current_risky_exposure: float,
        risk_free_rate: float = 0.03,
    ) -> PortfolioInsuranceResult:
        """
        TIPP 策略（Time Invariant Portfolio Protection）
        CPPI 的改进版，保本线随组合价值上涨而提高

        Args:
            portfolio_value: 当前组合价值
            initial_value: 初始价值
            highest_value: 历史最高价值
            current_risky_exposure: 当前风险资产敞口
            risk_free_rate: 无风险利率

        Returns:
            保险结果
        """
        # TIPP 保本线：历史最高价值的一定比例
        floor_value = max(
            initial_value * self.config.floor_rate,
            highest_value * self.config.floor_rate
        )

        # 计算缓冲垫
        cushion = portfolio_value - floor_value

        # 风险资产配置
        target_exposure = cushion * self.config.multiplier
        target_exposure = max(0, min(target_exposure, portfolio_value))

        risky_allocation = target_exposure / portfolio_value if portfolio_value > 0 else 0
        risk_free_allocation = 1 - risky_allocation

        rebalance_needed = abs(target_exposure - current_risky_exposure) > portfolio_value * 0.05

        return PortfolioInsuranceResult(
            strategy="TIPP",
            portfolio_value=portfolio_value,
            floor_value=floor_value,
            cushion=cushion,
            risky_allocation=risky_allocation,
            risk_free_allocation=risk_free_allocation,
            target_exposure=target_exposure,
            current_exposure=current_risky_exposure,
            rebalance_needed=rebalance_needed,
        )

    def compare_strategies(
        self,
        portfolio_value: float,
        initial_value: float,
        highest_value: float,
        current_risky_exposure: float,
    ) -> Dict:
        """对比 CPPI 和 TIPP 策略"""
        cppi_result = self.calculate_cppi(
            portfolio_value, initial_value, current_risky_exposure
        )
        tipp_result = self.calculate_tipp(
            portfolio_value, initial_value, highest_value, current_risky_exposure
        )

        return {
            "cppi": cppi_result.to_dict(),
            "tipp": tipp_result.to_dict(),
            "recommendation": "TIPP" if tipp_result.floor_value > cppi_result.floor_value else "CPPI",
            "reason": "TIPP 提供更好的保本" if tipp_result.floor_value > cppi_result.floor_value else "CPPI 更灵活",
        }

    def simulate_cppi(
        self,
        initial_value: float,
        returns: list,
        risk_free_rate: float = 0.03,
    ) -> Dict:
        """
        模拟 CPPI 策略表现

        Args:
            initial_value: 初始价值
            returns: 风险资产收益率序列
            risk_free_rate: 无风险利率

        Returns:
            模拟结果
        """
        portfolio = initial_value
        highest = initial_value
        floor = initial_value * self.config.floor_rate

        values = [portfolio]
        allocations = []

        for ret in returns:
            cushion = max(0, portfolio - floor)
            exposure = cushion * self.config.multiplier
            exposure = max(0, min(exposure, portfolio))

            risky_weight = exposure / portfolio if portfolio > 0 else 0
            risk_free_weight = 1 - risky_weight

            # 更新组合价值
            portfolio = (
                exposure * (1 + ret) +
                (portfolio - exposure) * (1 + risk_free_rate / 252)
            )

            highest = max(highest, portfolio)
            floor = max(floor, initial_value * self.config.floor_rate)

            values.append(portfolio)
            allocations.append(risky_weight)

        total_return = (values[-1] - values[0]) / values[0]

        return {
            "initial_value": initial_value,
            "final_value": values[-1],
            "total_return": f"{total_return:.2%}",
            "max_value": max(values),
            "min_value": min(values),
            "final_allocation": f"{allocations[-1]:.2%}" if allocations else "0%",
            "values": values,
            "allocations": allocations,
        }
