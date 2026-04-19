"""
Phase 78: AI 策略助手 (AI Strategy Advisor)

基于规则和市场状态的自动策略推荐系统
"""


from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class MarketRegime(Enum):
    """市场状态"""
    BULL = "牛市"
    BEAR = "熊市"
    SIDEWAY = "震荡市"
    HIGH_VOL = "高波动"
    LOW_VOL = "低波动"


class RiskTolerance(Enum):
    """风险偏好"""
    CONSERVATIVE = "保守"
    MODERATE = "稳健"
    AGGRESSIVE = "激进"


@dataclass
class StrategyRecommendation:
    """策略推荐"""
    strategy_name: str
    confidence: float
    reason: str
    expected_return: float
    expected_risk: float
    suitable_regimes: List[MarketRegime]
    parameters: Dict

    def to_dict(self) -> Dict:
        return {
            "strategy": self.strategy_name,
            "confidence": f"{self.confidence:.1%}",
            "reason": self.reason,
            "expected_annual_return": f"{self.expected_return:.1%}",
            "expected_volatility": f"{self.expected_risk:.1%}",
            "suitable_for": [r.value for r in self.suitable_regimes],
            "parameters": self.parameters,
        }


class StrategyAdvisor:
    """AI 策略助手"""

    def __init__(self):
        # 策略特征库
        self.strategy_profiles = {
            "动量策略": {
                "regimes": [MarketRegime.BULL, MarketRegime.BEAR],
                "volatility": "medium",
                "risk": "medium",
                "expected_return": 0.15,
                "expected_risk": 0.20,
                "description": "适合趋势明显的市场",
                "params": {"momentum_window": 20, "threshold": 0.02},
            },
            "均值回归策略": {
                "regimes": [MarketRegime.SIDEWAY, MarketRegime.LOW_VOL],
                "volatility": "low",
                "risk": "low",
                "expected_return": 0.10,
                "expected_risk": 0.12,
                "description": "适合震荡市场",
                "params": {"lookback_window": 30, "entry_threshold": 2.0},
            },
            "统计套利": {
                "regimes": [MarketRegime.SIDEWAY, MarketRegime.LOW_VOL],
                "volatility": "low",
                "risk": "low",
                "expected_return": 0.12,
                "expected_risk": 0.08,
                "description": "适合配对交易",
                "params": {"correlation_threshold": 0.8, "zscore_entry": 2.0},
            },
            "波动率策略": {
                "regimes": [MarketRegime.HIGH_VOL],
                "volatility": "high",
                "risk": "high",
                "expected_return": 0.20,
                "expected_risk": 0.30,
                "description": "适合高波动市场",
                "params": {"vol_window": 20, "entry_threshold": 1.5},
            },
            "事件驱动策略": {
                "regimes": [MarketRegime.BULL, MarketRegime.HIGH_VOL],
                "volatility": "medium",
                "risk": "medium",
                "expected_return": 0.18,
                "expected_risk": 0.22,
                "description": "适合事件驱动机会",
                "params": {"event_types": ["earnings", "dividend"]},
            },
            "风险平价策略": {
                "regimes": [MarketRegime.BULL, MarketRegime.BEAR, MarketRegime.SIDEWAY],
                "volatility": "low",
                "risk": "low",
                "expected_return": 0.08,
                "expected_risk": 0.10,
                "description": "适合稳健配置",
                "params": {"risk_budget": "equal"},
            },
        }

    def recommend(
        self,
        market_regime: MarketRegime,
        risk_tolerance: RiskTolerance = RiskTolerance.MODERATE,
        current_volatility: Optional[float] = None,
        min_confidence: float = 0.6,
    ) -> List[StrategyRecommendation]:
        """
        根据市场状态和风险偏好推荐策略

        Args:
            market_regime: 当前市场状态
            risk_tolerance: 风险偏好
            current_volatility: 当前波动率（可选）
            min_confidence: 最低置信度阈值

        Returns:
            策略推荐列表（按置信度排序）
        """
        recommendations = []

        for strategy_name, profile in self.strategy_profiles.items():
            # 检查市场状态匹配度
            regime_match = market_regime in profile["regimes"]
            if not regime_match:
                continue

            # 计算置信度
            confidence = self._calculate_confidence(
                profile, market_regime, risk_tolerance, current_volatility
            )

            if confidence < min_confidence:
                continue

            # 调整预期收益和风险
            adj_return, adj_risk = self._adjust_for_risk_tolerance(
                profile["expected_return"],
                profile["expected_risk"],
                risk_tolerance,
            )

            rec = StrategyRecommendation(
                strategy_name=strategy_name,
                confidence=confidence,
                reason=profile["description"],
                expected_return=adj_return,
                expected_risk=adj_risk,
                suitable_regimes=profile["regimes"],
                parameters=profile["params"],
            )
            recommendations.append(rec)

        # 按置信度排序
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        return recommendations

    def detect_regime(
        self,
        market_return: float,
        volatility: float,
        trend_strength: Optional[float] = None,
    ) -> MarketRegime:
        """
        检测市场状态

        Args:
            market_return: 市场收益率
            volatility: 波动率
            trend_strength: 趋势强度（可选）

        Returns:
            市场状态
        """
        # 高波动判断
        if volatility > 0.30:
            return MarketRegime.HIGH_VOL
        if volatility < 0.10:
            return MarketRegime.LOW_VOL

        # 牛熊判断
        if trend_strength is not None:
            if trend_strength > 0.5 and market_return > 0:
                return MarketRegime.BULL
            if trend_strength < -0.5 and market_return < 0:
                return MarketRegime.BEAR

        # 默认震荡市
        return MarketRegime.SIDEWAY

    def _calculate_confidence(
        self,
        profile: Dict,
        market_regime: MarketRegime,
        risk_tolerance: RiskTolerance,
        current_volatility: Optional[float],
    ) -> float:
        """计算策略置信度"""
        confidence = 0.5

        # 市场状态匹配 (+0.3)
        if market_regime in profile["regimes"]:
            confidence += 0.3

        # 风险偏好匹配
        risk_level = profile["risk"]
        if (risk_tolerance == RiskTolerance.CONSERVATIVE and risk_level == "low") or \
           (risk_tolerance == RiskTolerance.MODERATE and risk_level == "medium") or \
           (risk_tolerance == RiskTolerance.AGGRESSIVE and risk_level == "high"):
            confidence += 0.2

        # 波动率匹配
        if current_volatility:
            vol_level = profile["volatility"]
            if (vol_level == "low" and current_volatility < 0.15) or \
               (vol_level == "medium" and 0.15 <= current_volatility <= 0.25) or \
               (vol_level == "high" and current_volatility > 0.25):
                confidence += 0.1

        return min(confidence, 1.0)

    def _adjust_for_risk_tolerance(
        self,
        base_return: float,
        base_risk: float,
        risk_tolerance: RiskTolerance,
    ) -> Tuple[float, float]:
        """根据风险偏好调整预期收益和风险"""
        if risk_tolerance == RiskTolerance.CONSERVATIVE:
            return base_return * 0.8, base_risk * 0.7
        elif risk_tolerance == RiskTolerance.AGGRESSIVE:
            return base_return * 1.2, base_risk * 1.3
        return base_return, base_risk
