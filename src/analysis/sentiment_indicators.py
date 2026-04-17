"""
Phase 82: 市场情绪指标系统 (Market Sentiment Indicators)

多维度市场情绪分析
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class SentimentLevel(Enum):
    """情绪等级"""
    EXTREME_FEAR = "极度恐慌"
    FEAR = "恐慌"
    NEUTRAL = "中性"
    GREED = "贪婪"
    EXTREME_GREED = "极度贪婪"


@dataclass
class SentimentIndicator:
    """情绪指标"""
    name: str
    value: float  # -1.0 ~ 1.0
    weight: float  # 权重
    description: str

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": round(self.value, 4),
            "weight": self.weight,
            "description": self.description,
        }


@dataclass
class SentimentReport:
    """情绪报告"""
    timestamp: float
    overall_score: float  # -1.0 ~ 1.0
    sentiment_level: SentimentLevel
    indicators: List[SentimentIndicator]
    market_context: Dict

    def to_dict(self) -> Dict:
        return {
            "timestamp": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "overall_score": round(self.overall_score, 4),
            "sentiment_level": self.sentiment_level.value,
            "indicators": [i.to_dict() for i in self.indicators],
            "market_context": self.market_context,
        }


class MarketSentimentAnalyzer:
    """市场情绪分析器"""

    def __init__(self):
        self.indicators = {}

    def add_indicator(self, name: str, calculator, weight: float = 1.0):
        """添加情绪指标"""
        self.indicators[name] = {
            "calculator": calculator,
            "weight": weight,
        }

    def analyze(
        self,
        market_data: Dict,
        include_context: bool = True,
    ) -> SentimentReport:
        """
        综合分析市场情绪

        Args:
            market_data: 市场数据
            include_context: 是否包含市场环境

        Returns:
            情绪报告
        """
        indicators = []
        total_weight = 0
        weighted_sum = 0

        for name, config in self.indicators.items():
            try:
                value = config["calculator"](market_data)
                weight = config["weight"]

                indicator = SentimentIndicator(
                    name=name,
                    value=value,
                    weight=weight,
                    description=self._get_indicator_description(name, value),
                )
                indicators.append(indicator)

                weighted_sum += value * weight
                total_weight += weight
            except Exception:
                continue

        # 计算综合得分
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        sentiment_level = self._classify_sentiment(overall_score)

        # 市场环境
        market_context = {}
        if include_context:
            market_context = self._analyze_market_context(market_data)

        return SentimentReport(
            timestamp=datetime.now().timestamp(),
            overall_score=overall_score,
            sentiment_level=sentiment_level,
            indicators=indicators,
            market_context=market_context,
        )

    def _classify_sentiment(self, score: float) -> SentimentLevel:
        """分类情绪等级"""
        if score <= -0.6:
            return SentimentLevel.EXTREME_FEAR
        elif score <= -0.2:
            return SentimentLevel.FEAR
        elif score <= 0.2:
            return SentimentLevel.NEUTRAL
        elif score <= 0.6:
            return SentimentLevel.GREED
        else:
            return SentimentLevel.EXTREME_GREED

    def _get_indicator_description(self, name: str, value: float) -> str:
        """获取指标描述"""
        descriptions = {
            "vix_index": f"波动率指数 {'偏高' if value > 0 else '偏低'}",
            "put_call_ratio": f"看跌/看涨比例 {'偏高' if value > 0 else '偏低'}",
            "advance_decline": f"涨跌比 {'偏强' if value > 0 else '偏弱'}",
            "volume_ratio": f"成交量比率 {'放量' if value > 0 else '缩量'}",
            "momentum_score": f"动量评分 {'偏强' if value > 0 else '偏弱'}",
            "news_sentiment": f"新闻情绪 {'偏正面' if value > 0 else '偏负面'}",
        }
        return descriptions.get(name, f"{name}: {value:.2f}")

    def _analyze_market_context(self, market_data: Dict) -> Dict:
        """分析市场环境"""
        context = {}

        if "market_return" in market_data:
            ret = market_data["market_return"]
            if ret > 0.05:
                context["trend"] = "强势上涨"
            elif ret > 0:
                context["trend"] = "温和上涨"
            elif ret > -0.05:
                context["trend"] = "温和下跌"
            else:
                context["trend"] = "强势下跌"

        if "volatility" in market_data:
            vol = market_data["volatility"]
            if vol > 0.3:
                context["volatility"] = "高波动"
            elif vol > 0.15:
                context["volatility"] = "中等波动"
            else:
                context["volatility"] = "低波动"

        return context


# 预定义指标计算器
def vix_calculator(market_data: Dict) -> float:
    """VIX 指数指标"""
    vix = market_data.get("vix", 20)
    # VIX > 30 表示恐慌，< 15 表示贪婪
    return (30 - vix) / 15  # 归一化到 -1 ~ 1


def put_call_ratio_calculator(market_data: Dict) -> float:
    """看跌/看涨比例"""
    ratio = market_data.get("put_call_ratio", 1.0)
    # PC ratio > 1.2 恐慌，< 0.7 贪婪
    return (1.2 - ratio) / 0.5


def advance_decline_calculator(market_data: Dict) -> float:
    """涨跌比指标"""
    advance = market_data.get("advance", 1000)
    decline = market_data.get("decline", 1000)
    total = advance + decline
    if total == 0:
        return 0.0
    return (advance - decline) / total


def volume_ratio_calculator(market_data: Dict) -> float:
    """成交量比率"""
    current_volume = market_data.get("current_volume", 0)
    avg_volume = market_data.get("avg_volume", 1)
    if avg_volume == 0:
        return 0.0
    ratio = current_volume / avg_volume
    # ratio > 1.5 放量，< 0.5 缩量
    return min(max((ratio - 1.0) / 0.5, -1), 1)


def momentum_calculator(market_data: Dict) -> float:
    """动量指标"""
    returns = market_data.get("recent_returns", [])
    if not returns:
        return 0.0
    avg_return = sum(returns) / len(returns)
    return min(max(avg_return * 10, -1), 1)  # 缩放
