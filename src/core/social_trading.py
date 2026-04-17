"""
Phase 102: 社交交易系统 (Social Trading System)

跟单/分享/社区功能
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time


class TraderTier(Enum):
    """交易员等级"""
    BEGINNER = "新手"
    INTERMEDIATE = "中级"
    EXPERT = "专家"
    MASTER = "大师"


class CopyMode(Enum):
    """跟单模式"""
    FIXED_AMOUNT = "固定金额"
    FIXED_RATIO = "固定比例"
    PROPORTIONAL = "等比例"


@dataclass
class TraderProfile:
    """交易员档案"""
    trader_id: str
    name: str
    tier: TraderTier
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trading_days: int
    followers_count: int
    assets_under_management: float
    risk_score: float  # 1-10
    strategies: List[str]
    bio: str = ""
    verified: bool = False

    def to_dict(self) -> Dict:
        return {
            "trader_id": self.trader_id,
            "name": self.name,
            "tier": self.tier.value,
            "total_return": f"{self.total_return:.2%}",
            "sharpe_ratio": f"{self.sharpe_ratio:.2f}",
            "max_drawdown": f"{self.max_drawdown:.2%}",
            "win_rate": f"{self.win_rate:.2%}",
            "trading_days": self.trading_days,
            "followers": self.followers_count,
            "aum": f"¥{self.assets_under_management:,.0f}",
            "risk_score": f"{self.risk_score}/10",
            "strategies": self.strategies,
            "verified": self.verified,
        }


@dataclass
class CopyTradeConfig:
    """跟单配置"""
    follower_id: str
    master_trader_id: str
    mode: CopyMode
    amount: float  # 跟单金额或比例
    max_position_size: float  # 最大单笔仓位
    stop_loss_pct: float  # 止损比例
    take_profit_pct: float  # 止盈比例
    active: bool = True
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        return {
            "follower": self.follower_id,
            "master": self.master_trader_id,
            "mode": self.mode.value,
            "amount": f"¥{self.amount:,.2f}",
            "max_position": f"¥{self.max_position_size:,.2f}",
            "stop_loss": f"{self.stop_loss_pct:.2%}",
            "take_profit": f"{self.take_profit_pct:.2%}",
            "active": self.active,
        }


@dataclass
class SocialSignal:
    """社交信号"""
    signal_id: str
    trader_id: str
    symbol: str
    action: str  # buy/sell/hold
    price: float
    confidence: float
    reason: str
    timestamp: float
    likes: int = 0
    comments: int = 0

    def to_dict(self) -> Dict:
        return {
            "signal_id": self.signal_id,
            "trader": self.trader_id,
            "symbol": self.symbol,
            "action": self.action,
            "price": self.price,
            "confidence": f"{self.confidence:.1%}",
            "reason": self.reason,
            "timestamp": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "likes": self.likes,
            "comments": self.comments,
        }


class SocialTradingSystem:
    """社交交易系统"""

    def __init__(self):
        self.traders: Dict[str, TraderProfile] = {}
        self.copy_configs: List[CopyTradeConfig] = []
        self.signals: List[SocialSignal] = []

    def register_trader(self, profile: TraderProfile):
        """注册交易员"""
        self.traders[profile.trader_id] = profile

    def setup_copy_trade(self, config: CopyTradeConfig):
        """设置跟单"""
        self.copy_configs.append(config)

    def publish_signal(self, signal: SocialSignal):
        """发布交易信号"""
        self.signals.append(signal)

    def get_top_traders(
        self,
        metric: str = "total_return",
        limit: int = 10,
        min_trading_days: int = 30,
    ) -> List[TraderProfile]:
        """获取顶级交易员"""
        qualified = [t for t in self.traders.values() if t.trading_days >= min_trading_days]

        metric_map = {
            "total_return": lambda t: t.total_return,
            "sharpe_ratio": lambda t: t.sharpe_ratio,
            "win_rate": lambda t: t.win_rate,
            "followers": lambda t: t.followers_count,
        }

        sort_func = metric_map.get(metric, lambda t: t.total_return)
        sorted_traders = sorted(qualified, key=sort_func, reverse=True)

        return sorted_traders[:limit]

    def get_copy_trading_performance(self, follower_id: str) -> Dict:
        """获取跟单绩效"""
        follower_configs = [c for c in self.copy_configs if c.follower_id == follower_id and c.active]

        if not follower_configs:
            return {"error": "No active copy trades"}

        total_aum = sum(c.amount for c in follower_configs)

        return {
            "follower_id": follower_id,
            "active_copies": len(follower_configs),
            "total_aum": f"¥{total_aum:,.2f}",
            "masters": [
                {
                    "trader_id": c.master_trader_id,
                    "mode": c.mode.value,
                    "amount": f"¥{c.amount:,.2f}",
                }
                for c in follower_configs
            ],
        }

    def get_signal_feed(
        self,
        trader_id: Optional[str] = None,
        symbol: Optional[str] = None,
        limit: int = 20,
    ) -> List[SocialSignal]:
        """获取信号流"""
        signals = self.signals

        if trader_id:
            signals = [s for s in signals if s.trader_id == trader_id]
        if symbol:
            signals = [s for s in signals if s.symbol == symbol]

        # 按时间倒序
        signals = sorted(signals, key=lambda s: s.timestamp, reverse=True)

        return signals[:limit]

    def generate_leaderboard(self) -> Dict:
        """生成排行榜"""
        top_return = self.get_top_traders("total_return", 5)
        top_sharpe = self.get_top_traders("sharpe_ratio", 5)
        top_winrate = self.get_top_traders("win_rate", 5)
        top_followed = self.get_top_traders("followers", 5)

        return {
            "top_return": [t.to_dict() for t in top_return],
            "top_sharpe": [t.to_dict() for t in top_sharpe],
            "top_winrate": [t.to_dict() for t in top_winrate],
            "top_followed": [t.to_dict() for t in top_followed],
        }

    def get_trader_statistics(self, trader_id: str) -> Dict:
        """获取交易员统计数据"""
        if trader_id not in self.traders:
            return {"error": "Trader not found"}

        trader = self.traders[trader_id]
        trader_signals = [s for s in self.signals if s.trader_id == trader_id]

        return {
            "profile": trader.to_dict(),
            "total_signals": len(trader_signals),
            "avg_confidence": sum(s.confidence for s in trader_signals) / len(trader_signals) if trader_signals else 0,
            "recent_signals": [s.to_dict() for s in trader_signals[-5:]],
        }
