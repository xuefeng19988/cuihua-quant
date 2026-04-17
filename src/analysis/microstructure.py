"""
Phase 89: 市场微观结构分析 (Market Microstructure Analysis)

订单流、买卖价差、市场深度分析
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderFlowMetrics:
    """订单流指标"""
    total_volume: float
    buy_volume: float
    sell_volume: float
    order_imbalance: float  # (buy - sell) / total
    avg_trade_size: float
    trade_count: int
    large_trade_ratio: float  # 大单占比

    def to_dict(self) -> Dict:
        return {
            "total_volume": self.total_volume,
            "buy_volume": self.buy_volume,
            "sell_volume": self.sell_volume,
            "order_imbalance": f"{self.order_imbalance:.2%}",
            "avg_trade_size": f"{self.avg_trade_size:.0f}",
            "trade_count": self.trade_count,
            "large_trade_ratio": f"{self.large_trade_ratio:.2%}",
        }


@dataclass
class SpreadAnalysis:
    """价差分析"""
    quoted_spread: float  # 报价价差
    effective_spread: float  # 有效价差
    realized_spread: float  # 实现价差
    spread_pct: float  # 价差百分比
    spread_trend: str  # widening/narrowing

    def to_dict(self) -> Dict:
        return {
            "quoted_spread": f"{self.quoted_spread:.4f}",
            "effective_spread": f"{self.effective_spread:.4f}",
            "realized_spread": f"{self.realized_spread:.4f}",
            "spread_pct": f"{self.spread_pct:.2%}",
            "spread_trend": self.spread_trend,
        }


@dataclass
class MarketDepth:
    """市场深度"""
    bid_levels: int
    ask_levels: int
    total_bid_volume: float
    total_ask_volume: float
    depth_imbalance: float
    liquidity_score: float  # 0-1

    def to_dict(self) -> Dict:
        return {
            "bid_levels": self.bid_levels,
            "ask_levels": self.ask_levels,
            "total_bid_volume": self.total_bid_volume,
            "total_ask_volume": self.total_ask_volume,
            "depth_imbalance": f"{self.depth_imbalance:.2%}",
            "liquidity_score": f"{self.liquidity_score:.2f}",
        }


class MarketMicrostructureAnalyzer:
    """市场微观结构分析器"""

    def __init__(self):
        pass

    def analyze_order_flow(self, trade_data: List[Dict]) -> OrderFlowMetrics:
        """
        分析订单流

        Args:
            trade_data: 交易数据列表 [{price, volume, side, timestamp}]

        Returns:
            订单流指标
        """
        if not trade_data:
            return OrderFlowMetrics(0, 0, 0, 0, 0, 0, 0)

        total_volume = sum(t["volume"] for t in trade_data)
        buy_volume = sum(t["volume"] for t in trade_data if t.get("side") == "buy")
        sell_volume = sum(t["volume"] for t in trade_data if t.get("side") == "sell")

        order_imbalance = (buy_volume - sell_volume) / total_volume if total_volume > 0 else 0

        avg_trade_size = total_volume / len(trade_data)

        # 大单定义：超过平均 2 倍
        large_trades = sum(1 for t in trade_data if t["volume"] > avg_trade_size * 2)
        large_trade_ratio = large_trades / len(trade_data)

        return OrderFlowMetrics(
            total_volume=total_volume,
            buy_volume=buy_volume,
            sell_volume=sell_volume,
            order_imbalance=order_imbalance,
            avg_trade_size=avg_trade_size,
            trade_count=len(trade_data),
            large_trade_ratio=large_trade_ratio,
        )

    def analyze_spread(
        self,
        bid_prices: List[float],
        ask_prices: List[float],
        trade_prices: Optional[List[float]] = None,
    ) -> SpreadAnalysis:
        """
        分析买卖价差

        Args:
            bid_prices: 买价列表
            ask_prices: 卖价列表
            trade_prices: 成交价列表（可选）

        Returns:
            价差分析
        """
        if not bid_prices or not ask_prices:
            return SpreadAnalysis(0, 0, 0, 0, "unknown")

        # 报价价差
        spreads = [a - b for a, b in zip(ask_prices, bid_prices)]
        quoted_spread = sum(spreads) / len(spreads)

        # 有效价差（如果有成交价）
        if trade_prices:
            effective_spreads = [
                2 * abs(p - (a + b) / 2)
                for p, a, b in zip(trade_prices, ask_prices, bid_prices)
            ]
            effective_spread = sum(effective_spreads) / len(effective_spreads)
        else:
            effective_spread = quoted_spread

        # 实现价差（简化）
        realized_spread = effective_spread * 0.7

        # 价差百分比
        mid_price = sum(ask_prices) / len(ask_prices)
        spread_pct = quoted_spread / mid_price if mid_price > 0 else 0

        # 价差趋势
        if len(spreads) >= 2:
            first_half = sum(spreads[:len(spreads)//2]) / (len(spreads)//2)
            second_half = sum(spreads[len(spreads)//2:]) / (len(spreads) - len(spreads)//2)
            if second_half > first_half * 1.1:
                trend = "widening"
            elif second_half < first_half * 0.9:
                trend = "narrowing"
            else:
                trend = "stable"
        else:
            trend = "unknown"

        return SpreadAnalysis(
            quoted_spread=quoted_spread,
            effective_spread=effective_spread,
            realized_spread=realized_spread,
            spread_pct=spread_pct,
            spread_trend=trend,
        )

    def analyze_depth(
        self,
        order_book: Dict,
    ) -> MarketDepth:
        """
        分析市场深度

        Args:
            order_book: 订单簿 {bids: [(price, volume)], asks: [(price, volume)]}

        Returns:
            市场深度
        """
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])

        total_bid_volume = sum(v for _, v in bids)
        total_ask_volume = sum(v for _, v in asks)

        depth_imbalance = (
            (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
            if (total_bid_volume + total_ask_volume) > 0
            else 0
        )

        # 流动性评分（基于深度和平衡度）
        total_depth = total_bid_volume + total_ask_volume
        depth_score = min(total_depth / 1000000, 1.0)  # 归一化
        balance_score = 1 - abs(depth_imbalance)
        liquidity_score = (depth_score + balance_score) / 2

        return MarketDepth(
            bid_levels=len(bids),
            ask_levels=len(asks),
            total_bid_volume=total_bid_volume,
            total_ask_volume=total_ask_volume,
            depth_imbalance=depth_imbalance,
            liquidity_score=liquidity_score,
        )

    def comprehensive_analysis(
        self,
        trade_data: List[Dict],
        bid_prices: List[float],
        ask_prices: List[float],
        order_book: Dict,
    ) -> Dict:
        """综合分析市场微观结构"""
        order_flow = self.analyze_order_flow(trade_data)
        spread = self.analyze_spread(bid_prices, ask_prices)
        depth = self.analyze_depth(order_book)

        return {
            "order_flow": order_flow.to_dict(),
            "spread": spread.to_dict(),
            "depth": depth.to_dict(),
            "market_quality": self._assess_market_quality(order_flow, spread, depth),
        }

    def _assess_market_quality(
        self,
        order_flow: OrderFlowMetrics,
        spread: SpreadAnalysis,
        depth: MarketDepth,
    ) -> Dict:
        """评估市场质量"""
        # 流动性评估
        if depth.liquidity_score > 0.7 and spread.spread_pct < 0.001:
            liquidity = "excellent"
        elif depth.liquidity_score > 0.4 and spread.spread_pct < 0.005:
            liquidity = "good"
        else:
            liquidity = "poor"

        # 订单流健康度
        if abs(order_flow.order_imbalance) < 0.2:
            flow_health = "balanced"
        else:
            flow_health = "imbalanced"

        return {
            "liquidity": liquidity,
            "flow_health": flow_health,
            "overall_score": (
                depth.liquidity_score * 0.4 +
                (1 - spread.spread_pct * 100) * 0.3 +
                (1 - abs(order_flow.order_imbalance)) * 0.3
            ),
        }
