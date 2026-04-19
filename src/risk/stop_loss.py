"""
Phase 93: 智能止损系统 (Intelligent Stop-Loss System)

动态止损策略，保护组合收益
"""


from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class StopLossType(Enum):
    """止损类型"""
    FIXED_PERCENTAGE = "固定百分比"
    TRAILING_STOP = "追踪止损"
    VOLATILITY_BASED = "波动率止损"
    SUPPORT_RESISTANCE = "支撑阻力止损"
    TIME_BASED = "时间止损"
    CORRELATION_BASED = "相关性止损"


@dataclass
class StopLossRule:
    """止损规则"""
    name: str
    stop_type: StopLossType
    threshold: float
    enabled: bool = True
    description: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.stop_type.value,
            "threshold": f"{self.threshold:.2%}",
            "enabled": self.enabled,
            "description": self.description,
        }


@dataclass
class PositionStatus:
    """持仓状态"""
    symbol: str
    entry_price: float
    current_price: float
    entry_date: str
    pnl_pct: float
    high_water_mark: float  # 最高价
    days_held: int
    stop_loss_triggered: bool
    stop_loss_price: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "entry_date": self.entry_date,
            "pnl_pct": f"{self.pnl_pct:.2%}",
            "high_water_mark": self.high_water_mark,
            "days_held": self.days_held,
            "stop_loss_triggered": self.stop_loss_triggered,
            "stop_loss_price": self.stop_loss_price,
        }


@dataclass
class StopLossAlert:
    """止损警报"""
    symbol: str
    alert_type: str  # warning/trigger
    current_price: float
    stop_loss_price: float
    distance_pct: float
    recommendation: str

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "type": self.alert_type,
            "current_price": self.current_price,
            "stop_loss_price": self.stop_loss_price,
            "distance_pct": f"{self.distance_pct:.2%}",
            "recommendation": self.recommendation,
        }


class IntelligentStopLossSystem:
    """智能止损系统"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.rules: List[StopLossRule] = []
        self.position_history: Dict[str, List[float]] = {}  # 价格历史

        # 默认规则
        self._setup_default_rules()

    def _setup_default_rules(self):
        """设置默认止损规则"""
        self.rules = [
            StopLossRule(
                name="固定百分比止损",
                stop_type=StopLossType.FIXED_PERCENTAGE,
                threshold=-0.10,  # -10%
                description="亏损超过 10% 止损",
            ),
            StopLossRule(
                name="追踪止损",
                stop_type=StopLossType.TRAILING_STOP,
                threshold=-0.05,  # 从最高点回撤 5%
                description="从最高点回撤 5% 止损",
            ),
            StopLossRule(
                name="波动率止损",
                stop_type=StopLossType.VOLATILITY_BASED,
                threshold=2.0,  # 2 倍波动率
                description="价格跌破 2 倍波动率止损",
            ),
        ]

    def add_rule(self, rule: StopLossRule):
        """添加止损规则"""
        self.rules.append(rule)

    def check_positions(
        self,
        positions: List[Dict],
        market_data: Optional[Dict] = None,
    ) -> List[StopLossAlert]:
        """
        检查所有持仓的止损状态

        Args:
            positions: 持仓列表
            market_data: 市场数据（波动率等）

        Returns:
            止损警报列表
        """
        alerts = []

        for pos in positions:
            symbol = pos["symbol"]
            entry_price = pos["entry_price"]
            current_price = pos["current_price"]
            high_water_mark = pos.get("high_water_mark", entry_price)
            days_held = pos.get("days_held", 0)

            # 更新价格历史
            if symbol not in self.position_history:
                self.position_history[symbol] = []
            self.position_history[symbol].append(current_price)

            # 检查所有规则
            for rule in self.rules:
                if not rule.enabled:
                    continue

                triggered = self._check_rule(
                    rule, current_price, entry_price, high_water_mark, days_held, market_data
                )

                if triggered:
                    stop_loss_price = self._calculate_stop_price(
                        rule, current_price, entry_price, high_water_mark, market_data
                    )

                    distance_pct = (current_price - stop_loss_price) / current_price

                    alert = StopLossAlert(
                        symbol=symbol,
                        alert_type="trigger",
                        current_price=current_price,
                        stop_loss_price=stop_loss_price,
                        distance_pct=distance_pct,
                        recommendation=f"建议卖出 {symbol}，触发{rule.name}",
                    )
                    alerts.append(alert)
                    break  # 一个持仓只触发一次
                else:
                    # 检查是否接近止损
                    warning_price = self._calculate_stop_price(
                        rule, current_price, entry_price, high_water_mark, market_data
                    )
                    distance = (current_price - warning_price) / current_price

                    if distance < 0.03:  # 距离止损 3% 以内
                        alert = StopLossAlert(
                            symbol=symbol,
                            alert_type="warning",
                            current_price=current_price,
                            stop_loss_price=warning_price,
                            distance_pct=distance,
                            recommendation=f"⚠️ {symbol} 接近止损，注意风险",
                        )
                        alerts.append(alert)

        return alerts

    def _check_rule(
        self,
        rule: StopLossRule,
        current_price: float,
        entry_price: float,
        high_water_mark: float,
        days_held: int,
        market_data: Optional[Dict],
    ) -> bool:
        """检查单个规则是否触发"""
        if rule.stop_type == StopLossType.FIXED_PERCENTAGE:
            pnl = (current_price - entry_price) / entry_price
            return pnl <= rule.threshold

        elif rule.stop_type == StopLossType.TRAILING_STOP:
            drawdown = (current_price - high_water_mark) / high_water_mark
            return drawdown <= rule.threshold

        elif rule.stop_type == StopLossType.VOLATILITY_BASED:
            if not market_data or "volatility" not in market_data:
                return False
            vol = market_data["volatility"]
            drop = (entry_price - current_price) / entry_price
            return drop > rule.threshold * vol

        elif rule.stop_type == StopLossType.TIME_BASED:
            return days_held > rule.threshold  # threshold = max days

        return False

    def _calculate_stop_price(
        self,
        rule: StopLossRule,
        current_price: float,
        entry_price: float,
        high_water_mark: float,
        market_data: Optional[Dict],
    ) -> float:
        """计算止损价格"""
        if rule.stop_type == StopLossType.FIXED_PERCENTAGE:
            return entry_price * (1 + rule.threshold)
        elif rule.stop_type == StopLossType.TRAILING_STOP:
            return high_water_mark * (1 + rule.threshold)
        elif rule.stop_type == StopLossType.VOLATILITY_BASED:
            vol = market_data.get("volatility", 0.2) if market_data else 0.2
            return entry_price * (1 - rule.threshold * vol)
        return current_price

    def get_position_summary(self, positions: List[Dict]) -> Dict:
        """获取持仓止损总结"""
        total_positions = len(positions)
        at_risk = 0
        triggered = 0

        for pos in positions:
            pnl = (pos["current_price"] - pos["entry_price"]) / pos["entry_price"]
            if pnl < -0.05:  # 亏损超过 5%
                at_risk += 1
            if pnl < -0.10:  # 亏损超过 10%
                triggered += 1

        return {
            "total_positions": total_positions,
            "healthy_positions": total_positions - at_risk,
            "at_risk_positions": at_risk,
            "triggered_positions": triggered,
            "risk_rate": f"{at_risk / total_positions:.1%}" if total_positions > 0 else "0%",
        }
