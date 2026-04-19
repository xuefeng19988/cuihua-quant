"""
Phase 108: 智能信号聚合器 (Intelligent Signal Aggregator)

多信号融合与决策引擎
"""


from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SignalType(Enum):
    """信号类型"""
    TECHNICAL = "技术信号"
    FUNDAMENTAL = "基本面信号"
    SENTIMENT = "情绪信号"
    ML_PREDICTION = "ML 预测"
    MARKET_MICROSTRUCTURE = "微观结构信号"
    EVENT_DRIVEN = "事件驱动信号"
    FACTOR_BASED = "因子信号"


class SignalStrength(Enum):
    """信号强度"""
    STRONG_BUY = "强烈买入"
    BUY = "买入"
    WEAK_BUY = "弱买入"
    NEUTRAL = "中性"
    WEAK_SELL = "弱卖出"
    SELL = "卖出"
    STRONG_SELL = "强烈卖出"


@dataclass
class TradingSignal:
    """交易信号"""
    signal_id: str
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    score: float  # -1.0 ~ 1.0
    confidence: float  # 0.0 ~ 1.0
    source: str
    timestamp: float
    metadata: Dict = None

    def to_dict(self) -> Dict:
        return {
            "signal_id": self.signal_id,
            "symbol": self.symbol,
            "type": self.signal_type.value,
            "strength": self.strength.value,
            "score": round(self.score, 4),
            "confidence": f"{self.confidence:.1%}",
            "source": self.source,
            "timestamp": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "metadata": self.metadata,
        }


@dataclass
class AggregatedSignal:
    """聚合信号"""
    symbol: str
    overall_score: float
    overall_strength: SignalStrength
    consensus_score: float
    signal_count: int
    buy_signals: int
    sell_signals: int
    neutral_signals: int
    component_signals: List[Dict]
    recommendation: str

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "overall_score": round(self.overall_score, 4),
            "overall_strength": self.overall_strength.value,
            "consensus_score": f"{self.consensus_score:.2%}",
            "signal_count": self.signal_count,
            "buy_signals": self.buy_signals,
            "sell_signals": self.sell_signals,
            "neutral_signals": self.neutral_signals,
            "component_signals": self.component_signals,
            "recommendation": self.recommendation,
        }


class SignalAggregator:
    """智能信号聚合器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

        # 信号权重
        self.weights = self.config.get("weights", {
            SignalType.TECHNICAL: 0.20,
            SignalType.FUNDAMENTAL: 0.15,
            SignalType.SENTIMENT: 0.15,
            SignalType.ML_PREDICTION: 0.25,
            SignalType.MARKET_MICROSTRUCTURE: 0.10,
            SignalType.EVENT_DRIVEN: 0.10,
            SignalType.FACTOR_BASED: 0.05,
        })

        # 最低共识阈值
        self.min_consensus = self.config.get("min_consensus", 0.6)

    def aggregate_signals(
        self,
        symbol: str,
        signals: List[TradingSignal],
    ) -> AggregatedSignal:
        """
        聚合多个信号

        Args:
            symbol: 股票代码
            signals: 信号列表

        Returns:
            聚合信号
        """
        if not signals:
            return AggregatedSignal(
                symbol=symbol,
                overall_score=0,
                overall_strength=SignalStrength.NEUTRAL,
                consensus_score=0,
                signal_count=0,
                buy_signals=0,
                sell_signals=0,
                neutral_signals=0,
                component_signals=[],
                recommendation="HOLD",
            )

        # 计算加权得分
        weighted_score = 0
        total_weight = 0
        component_signals = []

        buy_count = 0
        sell_count = 0
        neutral_count = 0

        for signal in signals:
            weight = self.weights.get(signal.signal_type, 0.1)
            confidence_weight = weight * signal.confidence

            weighted_score += signal.score * confidence_weight
            total_weight += confidence_weight

            # 分类统计
            if signal.score > 0.2:
                buy_count += 1
            elif signal.score < -0.2:
                sell_count += 1
            else:
                neutral_count += 1

            component_signals.append({
                "type": signal.signal_type.value,
                "score": signal.score,
                "weight": weight,
                "confidence": signal.confidence,
            })

        # 归一化得分
        overall_score = weighted_score / total_weight if total_weight > 0 else 0

        # 计算共识度
        consensus_score = self._calculate_consensus(signals)

        # 确定信号强度
        overall_strength = self._score_to_strength(overall_score)

        # 生成建议
        recommendation = self._generate_recommendation(overall_score, consensus_score, len(signals))

        return AggregatedSignal(
            symbol=symbol,
            overall_score=overall_score,
            overall_strength=overall_strength,
            consensus_score=consensus_score,
            signal_count=len(signals),
            buy_signals=buy_count,
            sell_signals=sell_count,
            neutral_signals=neutral_count,
            component_signals=component_signals,
            recommendation=recommendation,
        )

    def _calculate_consensus(self, signals: List[TradingSignal]) -> float:
        """计算共识度"""
        if not signals:
            return 0.0

        # 计算信号间的一致性
        scores = [s.score for s in signals]
        avg_score = sum(scores) / len(scores)

        # 一致性 = 1 - 标准差
        import statistics
        if len(scores) > 1:
            std_dev = statistics.stdev(scores)
            consensus = max(0, 1 - std_dev)
        else:
            consensus = 1.0

        return consensus

    def _score_to_strength(self, score: float) -> SignalStrength:
        """将得分转换为信号强度"""
        if score > 0.7:
            return SignalStrength.STRONG_BUY
        elif score > 0.4:
            return SignalStrength.BUY
        elif score > 0.1:
            return SignalStrength.WEAK_BUY
        elif score > -0.1:
            return SignalStrength.NEUTRAL
        elif score > -0.4:
            return SignalStrength.WEAK_SELL
        elif score > -0.7:
            return SignalStrength.SELL
        else:
            return SignalStrength.STRONG_SELL

    def _generate_recommendation(
        self,
        score: float,
        consensus: float,
        signal_count: int,
    ) -> str:
        """生成交易建议"""
        if consensus < self.min_consensus:
            return "HOLD - 信号分歧较大"

        if score > 0.5 and signal_count >= 3:
            return "BUY - 强烈看多"
        elif score > 0.2:
            return "BUY - 温和看多"
        elif score > 0:
            return "HOLD - 略偏多"
        elif score > -0.2:
            return "HOLD - 略偏空"
        elif score > -0.5:
            return "SELL - 温和看空"
        else:
            return "SELL - 强烈看空"

    def get_signal_summary(self, symbol: str, signals: List[TradingSignal]) -> Dict:
        """获取信号总结"""
        aggregated = self.aggregate_signals(symbol, signals)

        return {
            "symbol": symbol,
            "aggregated_signal": aggregated.to_dict(),
            "signal_breakdown": {
                "by_type": self._group_by_type(signals),
                "by_strength": self._group_by_strength(signals),
            },
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _group_by_type(self, signals: List[TradingSignal]) -> Dict:
        """按类型分组"""
        groups = {}
        for signal in signals:
            type_name = signal.signal_type.value
            if type_name not in groups:
                groups[type_name] = {"count": 0, "avg_score": 0}
            groups[type_name]["count"] += 1
            groups[type_name]["avg_score"] += signal.score

        for type_name in groups:
            groups[type_name]["avg_score"] /= groups[type_name]["count"]

        return groups

    def _group_by_strength(self, signals: List[TradingSignal]) -> Dict:
        """按强度分组"""
        groups = {
            "buy": 0,
            "sell": 0,
            "neutral": 0,
        }

        for signal in signals:
            if signal.score > 0.2:
                groups["buy"] += 1
            elif signal.score < -0.2:
                groups["sell"] += 1
            else:
                groups["neutral"] += 1

        return groups
