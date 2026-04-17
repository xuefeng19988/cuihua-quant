"""
Phase 83: 交易成本优化系统 (Transaction Cost Optimization)

滑点、手续费、市场冲击成本优化
"""

from __future__ import annotations

from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum


class OrderType(Enum):
    """订单类型"""
    MARKET = "市价单"
    LIMIT = "限价单"
    VWAP = "成交量加权平均价"
    TWAP = "时间加权平均价"
    PEGGED = "挂单"


class UrgencyLevel(Enum):
    """紧急程度"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"


@dataclass
class CostEstimate:
    """成本估算"""
    symbol: str
    side: str  # "buy" or "sell"
    quantity: int
    price: float
    commission: float  # 手续费
    stamp_tax: float  # 印花税
    slippage: float  # 滑点
    market_impact: float  # 市场冲击
    total_cost: float
    cost_bps: float  # 成本（基点）

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "notional": self.quantity * self.price,
            "commission": f"¥{self.commission:.2f}",
            "stamp_tax": f"¥{self.stamp_tax:.2f}",
            "slippage": f"¥{self.slippage:.2f}",
            "market_impact": f"¥{self.market_impact:.2f}",
            "total_cost": f"¥{self.total_cost:.2f}",
            "cost_bps": f"{self.cost_bps:.1f}bps",
        }


@dataclass
class ExecutionStrategy:
    """执行策略"""
    order_type: OrderType
    urgency: UrgencyLevel
    time_horizon: str  # 执行时间窗口
    expected_cost_bps: float
    description: str

    def to_dict(self) -> Dict:
        return {
            "order_type": self.order_type.value,
            "urgency": self.urgency.value,
            "time_horizon": self.time_horizon,
            "expected_cost_bps": f"{self.expected_cost_bps:.1f}",
            "description": self.description,
        }


class TransactionCostOptimizer:
    """交易成本优化器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

        # 默认费率
        self.commission_rate = self.config.get("commission_rate", 0.0003)  # 万三
        self.min_commission = self.config.get("min_commission", 5.0)  # 最低 5 元
        self.stamp_tax_rate = self.config.get("stamp_tax_rate", 0.001)  # 印花税千一（仅卖出）
        self.slippage_rate = self.config.get("slippage_rate", 0.001)  # 滑点千一

        # 市场冲击模型参数
        self.impact_factor = self.config.get("impact_factor", 0.1)  # 冲击因子

    def estimate_cost(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        daily_volume: Optional[int] = None,
        volatility: Optional[float] = None,
    ) -> CostEstimate:
        """
        估算交易成本

        Args:
            symbol: 股票代码
            side: 买卖方向
            quantity: 数量
            price: 价格
            daily_volume: 日成交量
            volatility: 波动率

        Returns:
            成本估算
        """
        notional = quantity * price

        # 1. 手续费
        commission = max(notional * self.commission_rate, self.min_commission)

        # 2. 印花税（仅卖出）
        stamp_tax = notional * self.stamp_tax_rate if side == "sell" else 0.0

        # 3. 滑点
        slippage = notional * self.slippage_rate

        # 4. 市场冲击
        market_impact = self._calculate_market_impact(
            quantity, daily_volume or 10_000_000, volatility or 0.2
        )

        total_cost = commission + stamp_tax + slippage + market_impact
        cost_bps = (total_cost / notional) * 10000 if notional > 0 else 0

        return CostEstimate(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            commission=commission,
            stamp_tax=stamp_tax,
            slippage=slippage,
            market_impact=market_impact,
            total_cost=total_cost,
            cost_bps=cost_bps,
        )

    def optimize_execution(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        urgency: UrgencyLevel = UrgencyLevel.MEDIUM,
        daily_volume: Optional[int] = None,
    ) -> ExecutionStrategy:
        """
        优化执行策略

        Args:
            symbol: 股票代码
            side: 买卖方向
            quantity: 数量
            price: 价格
            urgency: 紧急程度
            daily_volume: 日成交量

        Returns:
            执行策略
        """
        daily_vol = daily_volume or 10_000_000
        participation_rate = quantity / daily_vol if daily_vol > 0 else 0

        # 根据参与率和紧急程度选择策略
        if participation_rate < 0.01 or urgency == UrgencyLevel.HIGH:
            # 小单或紧急：市价单
            return ExecutionStrategy(
                order_type=OrderType.MARKET,
                urgency=urgency,
                time_horizon="立即",
                expected_cost_bps=self._estimate_cost_bps(quantity, price, urgency),
                description="市价单快速成交，适合小单或紧急情况",
            )
        elif participation_rate < 0.05 or urgency == UrgencyLevel.MEDIUM:
            # 中单：VWAP
            return ExecutionStrategy(
                order_type=OrderType.VWAP,
                urgency=urgency,
                time_horizon="全天",
                expected_cost_bps=self._estimate_cost_bps(quantity, price, urgency) * 0.8,
                description="VWAP 算法单，跟踪成交量加权平均价",
            )
        else:
            # 大单：TWAP 或挂单
            return ExecutionStrategy(
                order_type=OrderType.TWAP,
                urgency=UrgencyLevel.LOW,
                time_horizon="2-4 小时",
                expected_cost_bps=self._estimate_cost_bps(quantity, price, UrgencyLevel.LOW) * 0.6,
                description="TWAP 算法单，时间加权平均价，适合大单",
            )

    def _calculate_market_impact(
        self,
        quantity: int,
        daily_volume: int,
        volatility: float,
    ) -> float:
        """
        计算市场冲击成本
        简化模型：冲击 = 参与率 * 波动率 * 冲击因子 * 名义价值
        """
        if daily_volume == 0:
            return 0.0

        participation_rate = quantity / daily_volume
        impact = participation_rate * volatility * self.impact_factor

        return impact * quantity * 100  # 假设价格 100 元

    def _estimate_cost_bps(
        self,
        quantity: int,
        price: float,
        urgency: UrgencyLevel,
    ) -> float:
        """估算成本（基点）"""
        base_cost = 5.0  # 基础 5bps

        # 紧急程度调整
        urgency_multiplier = {
            UrgencyLevel.LOW: 0.8,
            UrgencyLevel.MEDIUM: 1.0,
            UrgencyLevel.HIGH: 1.5,
        }

        return base_cost * urgency_multiplier.get(urgency, 1.0)

    def compare_strategies(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        daily_volume: Optional[int] = None,
    ) -> List[Dict]:
        """对比不同执行策略的成本"""
        strategies = []

        for urgency in UrgencyLevel:
            execution = self.optimize_execution(
                symbol, side, quantity, price, urgency, daily_volume
            )
            cost = self.estimate_cost(
                symbol, side, quantity, price, daily_volume
            )

            strategies.append({
                "strategy": execution.to_dict(),
                "cost": cost.to_dict(),
            })

        return strategies
