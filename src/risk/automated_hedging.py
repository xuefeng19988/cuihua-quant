"""
Phase 106: 自动对冲系统 (Automated Hedging System)

智能对冲策略
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class HedgeType(Enum):
    """对冲类型"""
    INDEX_HEDGE = "指数对冲"
    SECTOR_HEDGE = "板块对冲"
    BETA_HEDGE = "Beta 对冲"
    OPTIONS_HEDGE = "期权对冲"
    PAIRS_HEDGE = "配对对冲"
    VOLATILITY_HEDGE = "波动率对冲"


class HedgeStrategy(Enum):
    """对冲策略"""
    MINIMUM_VARIANCE = "最小方差"
    DELTA_NEUTRAL = "Delta 中性"
    RISK_PARITY = "风险平价"
    CORRELATION_BASED = "相关性对冲"


@dataclass
class HedgePosition:
    """对冲头寸"""
    hedge_id: str
    hedge_type: HedgeType
    strategy: HedgeStrategy
    original_position: str
    hedge_instrument: str
    hedge_ratio: float
    original_exposure: float
    hedge_exposure: float
    net_exposure: float
    cost: float
    created_at: float

    def to_dict(self) -> Dict:
        return {
            "hedge_id": self.hedge_id,
            "type": self.hedge_type.value,
            "strategy": self.strategy.value,
            "original": self.original_position,
            "hedge_instrument": self.hedge_instrument,
            "hedge_ratio": f"{self.hedge_ratio:.2f}",
            "original_exposure": f"¥{self.original_exposure:,.2f}",
            "hedge_exposure": f"¥{self.hedge_exposure:,.2f}",
            "net_exposure": f"¥{self.net_exposure:,.2f}",
            "cost": f"¥{self.cost:,.2f}",
        }


@dataclass
class HedgeRecommendation:
    """对冲建议"""
    recommendation_id: str
    hedge_type: HedgeType
    instrument: str
    hedge_ratio: float
    expected_cost: float
    expected_risk_reduction: float
    confidence: float
    reason: str

    def to_dict(self) -> Dict:
        return {
            "recommendation_id": self.recommendation_id,
            "type": self.hedge_type.value,
            "instrument": self.instrument,
            "hedge_ratio": f"{self.hedge_ratio:.2f}",
            "cost": f"¥{self.expected_cost:,.2f}",
            "risk_reduction": f"{self.expected_risk_reduction:.2%}",
            "confidence": f"{self.confidence:.1%}",
            "reason": self.reason,
        }


class AutomatedHedgingSystem:
    """自动对冲系统"""

    def __init__(self):
        self.hedge_positions: List[HedgePosition] = []
        self.hedge_history = []

    def analyze_portfolio_risk(
        self,
        portfolio: Dict,
        market_data: Optional[Dict] = None,
    ) -> List[HedgeRecommendation]:
        """
        分析组合风险，生成对冲建议

        Args:
            portfolio: 组合信息
            market_data: 市场数据

        Returns:
            对冲建议列表
        """
        recommendations = []

        total_exposure = portfolio.get("total_exposure", 0)
        net_exposure = portfolio.get("net_exposure", total_exposure)
        beta = portfolio.get("beta", 1.0)
        max_position = portfolio.get("max_position_weight", 0)

        # 1. Beta 对冲建议
        if abs(beta - 1.0) > 0.2:
            hedge_ratio = beta * net_exposure
            recommendations.append(HedgeRecommendation(
                recommendation_id=f"hedge_beta_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                hedge_type=HedgeType.BETA_HEDGE,
                instrument="股指期货",
                hedge_ratio=hedge_ratio,
                expected_cost=hedge_ratio * 0.001,
                expected_risk_reduction=min(abs(beta - 1.0) * 0.5, 0.5),
                confidence=0.8,
                reason=f"组合 Beta {beta:.2f} 偏离 1.0，建议对冲",
            ))

        # 2. 集中度对冲
        if max_position > 0.2:
            hedge_amount = max_position * total_exposure * 0.5
            recommendations.append(HedgeRecommendation(
                recommendation_id=f"hedge_conc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                hedge_type=HedgeType.PAIRS_HEDGE,
                instrument="配对股票",
                hedge_ratio=hedge_amount / total_exposure if total_exposure > 0 else 0,
                expected_cost=hedge_amount * 0.002,
                expected_risk_reduction=(max_position - 0.2) * 0.3,
                confidence=0.7,
                reason=f"最大持仓集中度 {max_position:.2%} 过高",
            ))

        # 3. 波动率对冲
        volatility = portfolio.get("volatility", 0.15)
        if volatility > 0.25:
            hedge_amount = total_exposure * 0.1
            recommendations.append(HedgeRecommendation(
                recommendation_id=f"hedge_vol_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                hedge_type=HedgeType.VOLATILITY_HEDGE,
                instrument="VIX 期权",
                hedge_ratio=0.1,
                expected_cost=hedge_amount * 0.05,
                expected_risk_reduction=0.2,
                confidence=0.6,
                reason=f"组合波动率 {volatility:.2%} 偏高",
            ))

        return recommendations

    def execute_hedge(
        self,
        recommendation: HedgeRecommendation,
        portfolio: Dict,
    ) -> HedgePosition:
        """
        执行对冲

        Args:
            recommendation: 对冲建议
            portfolio: 组合信息

        Returns:
            对冲头寸
        """
        hedge_position = HedgePosition(
            hedge_id=recommendation.recommendation_id,
            hedge_type=recommendation.hedge_type,
            strategy=HedgeStrategy.MINIMUM_VARIANCE,
            original_position=portfolio.get("main_position", "unknown"),
            hedge_instrument=recommendation.instrument,
            hedge_ratio=recommendation.hedge_ratio,
            original_exposure=portfolio.get("total_exposure", 0),
            hedge_exposure=recommendation.hedge_ratio * portfolio.get("total_exposure", 0),
            net_exposure=portfolio.get("total_exposure", 0) * (1 - recommendation.hedge_ratio),
            cost=recommendation.expected_cost,
            created_at=datetime.now().timestamp(),
        )

        self.hedge_positions.append(hedge_position)
        self.hedge_history.append({
            "action": "open",
            "position": hedge_position.to_dict(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        return hedge_position

    def close_hedge(self, hedge_id: str) -> Dict:
        """关闭对冲"""
        for i, pos in enumerate(self.hedge_positions):
            if pos.hedge_id == hedge_id:
                self.hedge_positions.pop(i)
                self.hedge_history.append({
                    "action": "close",
                    "hedge_id": hedge_id,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                return {"status": "closed", "hedge_id": hedge_id}

        return {"error": "Hedge not found"}

    def get_active_hedges(self) -> List[Dict]:
        """获取活跃对冲"""
        return [pos.to_dict() for pos in self.hedge_positions]

    def get_hedge_effectiveness(self) -> Dict:
        """获取对冲效果"""
        if not self.hedge_positions:
            return {"error": "No active hedges"}

        total_hedged = sum(pos.hedge_exposure for pos in self.hedge_positions)
        total_original = sum(pos.original_exposure for pos in self.hedge_positions)
        total_cost = sum(pos.cost for pos in self.hedge_positions)

        hedge_ratio = total_hedged / total_original if total_original > 0 else 0

        return {
            "total_hedged": f"¥{total_hedged:,.2f}",
            "total_original": f"¥{total_original:,.2f}",
            "hedge_ratio": f"{hedge_ratio:.2%}",
            "total_cost": f"¥{total_cost:,.2f}",
            "active_hedges": len(self.hedge_positions),
        }
