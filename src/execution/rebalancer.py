"""
Phase 91: 组合再平衡引擎 (Portfolio Rebalancing Engine)

最优再平衡策略，最小化交易成本
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RebalanceTrade:
    """再平衡交易"""
    symbol: str
    side: str  # buy/sell
    quantity: int
    current_price: float
    estimated_cost: float
    tax_impact: float
    priority: float  # 0-1

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.current_price,
            "notional": self.quantity * self.current_price,
            "estimated_cost": f"¥{self.estimated_cost:.2f}",
            "tax_impact": f"¥{self.tax_impact:.2f}",
            "priority": f"{self.priority:.2f}",
        }


@dataclass
class RebalancePlan:
    """再平衡计划"""
    portfolio_id: str
    current_weights: Dict[str, float]
    target_weights: Dict[str, float]
    trades: List[RebalanceTrade]
    total_cost: float
    turnover: float
    execution_priority: str  # immediate/gradual/scheduled

    def to_dict(self) -> Dict:
        return {
            "portfolio_id": self.portfolio_id,
            "current_weights": {k: f"{v:.2%}" for k, v in self.current_weights.items()},
            "target_weights": {k: f"{v:.2%}" for k, v in self.target_weights.items()},
            "trades": [t.to_dict() for t in self.trades],
            "total_cost": f"¥{self.total_cost:.2f}",
            "turnover": f"{self.turnover:.2%}",
            "execution_priority": self.execution_priority,
            "trade_count": len(self.trades),
        }


class PortfolioRebalancer:
    """组合再平衡引擎"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.commission_rate = self.config.get("commission_rate", 0.0003)
        self.stamp_tax_rate = self.config.get("stamp_tax_rate", 0.001)
        self.threshold = self.config.get("threshold", 0.05)  # 5% 偏离阈值

    def generate_rebalance_plan(
        self,
        portfolio_id: str,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        current_prices: Dict[str, float],
        portfolio_value: float = 1_000_000,
        execution_priority: str = "gradual",
    ) -> RebalancePlan:
        """
        生成再平衡计划

        Args:
            portfolio_id: 组合 ID
            current_weights: 当前权重
            target_weights: 目标权重
            current_prices: 当前价格
            portfolio_value: 组合总价值
            execution_priority: 执行优先级

        Returns:
            再平衡计划
        """
        trades = []
        total_cost = 0

        # 找出需要调整的股票
        all_symbols = set(list(current_weights.keys()) + list(target_weights.keys()))

        for symbol in all_symbols:
            current_weight = current_weights.get(symbol, 0)
            target_weight = target_weights.get(symbol, 0)
            price = current_prices.get(symbol, 0)

            weight_diff = target_weight - current_weight

            # 检查是否超过阈值
            if abs(weight_diff) < self.threshold:
                continue

            # 计算交易数量
            notional_diff = weight_diff * portfolio_value
            quantity = int(notional_diff / price) if price > 0 else 0

            if quantity == 0:
                continue

            # 确定买卖方向
            side = "buy" if weight_diff > 0 else "sell"

            # 计算成本
            notional = abs(quantity) * price
            commission = max(notional * self.commission_rate, 5)
            tax_impact = notional * self.stamp_tax_rate if side == "sell" else 0
            cost = commission + tax_impact

            # 优先级（基于偏离程度）
            priority = min(abs(weight_diff) / 0.2, 1.0)

            trade = RebalanceTrade(
                symbol=symbol,
                side=side,
                quantity=abs(quantity),
                current_price=price,
                estimated_cost=cost,
                tax_impact=tax_impact,
                priority=priority,
            )

            trades.append(trade)
            total_cost += cost

        # 计算换手率
        turnover = sum(abs(t.quantity * t.current_price) for t in trades) / portfolio_value

        # 按优先级排序
        trades.sort(key=lambda t: t.priority, reverse=True)

        return RebalancePlan(
            portfolio_id=portfolio_id,
            current_weights=current_weights,
            target_weights=target_weights,
            trades=trades,
            total_cost=total_cost,
            turnover=turnover,
            execution_priority=execution_priority,
        )

    def optimize_execution(
        self,
        plan: RebalancePlan,
        max_daily_turnover: float = 0.1,
    ) -> List[RebalancePlan]:
        """
        优化执行计划（分批执行）

        Args:
            plan: 再平衡计划
            max_daily_turnover: 每日最大换手率

        Returns:
            分批执行计划
        """
        if plan.turnover <= max_daily_turnover:
            return [plan]

        # 分批执行
        daily_plans = []
        remaining_trades = plan.trades.copy()
        day = 1

        while remaining_trades:
            daily_trades = []
            daily_turnover = 0

            for trade in remaining_trades:
                trade_turnover = (trade.quantity * trade.current_price) / 1_000_000
                if daily_turnover + trade_turnover <= max_daily_turnover:
                    daily_trades.append(trade)
                    daily_turnover += trade_turnover

            if not daily_trades:
                break

            daily_plan = RebalancePlan(
                portfolio_id=f"{plan.portfolio_id}_day_{day}",
                current_weights=plan.current_weights,
                target_weights=plan.target_weights,
                trades=daily_trades,
                total_cost=sum(t.estimated_cost for t in daily_trades),
                turnover=daily_turnover,
                execution_priority="scheduled",
            )

            daily_plans.append(daily_plan)
            remaining_trades = [t for t in remaining_trades if t not in daily_trades]
            day += 1

        return daily_plans

    def get_rebalance_summary(self, plan: RebalancePlan) -> Dict:
        """获取再平衡总结"""
        buy_trades = [t for t in plan.trades if t.side == "buy"]
        sell_trades = [t for t in plan.trades if t.side == "sell"]

        return {
            "portfolio_id": plan.portfolio_id,
            "total_trades": len(plan.trades),
            "buy_count": len(buy_trades),
            "sell_count": len(sell_trades),
            "total_cost": f"¥{plan.total_cost:.2f}",
            "turnover": f"{plan.turnover:.2%}",
            "execution_priority": plan.execution_priority,
            "high_priority_trades": sum(1 for t in plan.trades if t.priority > 0.8),
        }
