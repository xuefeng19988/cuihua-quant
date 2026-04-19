"""
Phase 104: 策略市场框架 (Strategy Marketplace)

插件化策略生态系统
"""


from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time


class StrategyCategory(Enum):
    """策略类别"""
    TREND = "趋势跟踪"
    MEAN_REVERSION = "均值回归"
    MOMENTUM = "动量策略"
    ARBITRAGE = "套利策略"
    MARKET_MAKING = "做市策略"
    EVENT_DRIVEN = "事件驱动"
    ML_BASED = "机器学习"
    HYBRID = "混合策略"


class StrategyDifficulty(Enum):
    """策略难度"""
    BEGINNER = "入门"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"
    EXPERT = "专家"


@dataclass
class StrategyPlugin:
    """策略插件"""
    plugin_id: str
    name: str
    description: str
    category: StrategyCategory
    difficulty: StrategyDifficulty
    author: str
    version: str
    created_at: float
    updated_at: float
    downloads: int = 0
    rating: float = 0.0  # 1-5
    tags: List[str] = field(default_factory=list)
    parameters: Dict = field(default_factory=dict)
    expected_return: float = 0.0
    expected_sharpe: float = 0.0
    max_drawdown: float = 0.0
    min_capital: float = 100000

    def to_dict(self) -> Dict:
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "difficulty": self.difficulty.value,
            "author": self.author,
            "version": self.version,
            "downloads": self.downloads,
            "rating": f"{self.rating:.1f}/5",
            "tags": self.tags,
            "parameters": self.parameters,
            "expected_return": f"{self.expected_return:.2%}",
            "expected_sharpe": f"{self.expected_sharpe:.2f}",
            "max_drawdown": f"{self.max_drawdown:.2%}",
            "min_capital": f"¥{self.min_capital:,.0f}",
        }


@dataclass
class PluginReview:
    """插件评价"""
    reviewer_id: str
    plugin_id: str
    rating: int  # 1-5
    comment: str
    timestamp: float

    def to_dict(self) -> Dict:
        return {
            "reviewer": self.reviewer_id,
            "plugin": self.plugin_id,
            "rating": f"{self.rating}/5",
            "comment": self.comment,
            "timestamp": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        }


class StrategyMarketplace:
    """策略市场"""

    def __init__(self):
        self.plugins: Dict[str, StrategyPlugin] = {}
        self.reviews: List[PluginReview] = []
        self.installed_plugins: List[str] = []

    def publish_plugin(self, plugin: StrategyPlugin):
        """发布策略插件"""
        self.plugins[plugin.plugin_id] = plugin

    def install_plugin(self, plugin_id: str) -> Optional[StrategyPlugin]:
        """安装策略插件"""
        if plugin_id not in self.plugins:
            return None

        plugin = self.plugins[plugin_id]
        plugin.downloads += 1
        self.installed_plugins.append(plugin_id)

        return plugin

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """卸载策略插件"""
        if plugin_id in self.installed_plugins:
            self.installed_plugins.remove(plugin_id)
            return True
        return False

    def search_plugins(
        self,
        category: Optional[StrategyCategory] = None,
        difficulty: Optional[StrategyDifficulty] = None,
        min_rating: float = 0,
        tags: Optional[List[str]] = None,
    ) -> List[StrategyPlugin]:
        """搜索策略插件"""
        results = list(self.plugins.values())

        if category:
            results = [p for p in results if p.category == category]
        if difficulty:
            results = [p for p in results if p.difficulty == difficulty]
        if min_rating > 0:
            results = [p for p in results if p.rating >= min_rating]
        if tags:
            results = [p for p in results if any(t in p.tags for t in tags)]

        # 按评分排序
        results.sort(key=lambda p: p.rating, reverse=True)

        return results

    def add_review(self, review: PluginReview):
        """添加评价"""
        self.reviews.append(review)

        # 更新插件评分
        plugin_id = review.plugin_id
        if plugin_id in self.plugins:
            plugin_reviews = [r for r in self.reviews if r.plugin_id == plugin_id]
            avg_rating = sum(r.rating for r in plugin_reviews) / len(plugin_reviews)
            self.plugins[plugin_id].rating = avg_rating

    def get_plugin_details(self, plugin_id: str) -> Dict:
        """获取插件详情"""
        if plugin_id not in self.plugins:
            return {"error": "Plugin not found"}

        plugin = self.plugins[plugin_id]
        plugin_reviews = [r for r in self.reviews if r.plugin_id == plugin_id]

        return {
            "plugin": plugin.to_dict(),
            "reviews": [r.to_dict() for r in plugin_reviews[-5:]],
            "total_reviews": len(plugin_reviews),
        }

    def get_marketplace_stats(self) -> Dict:
        """获取市场统计"""
        total_plugins = len(self.plugins)
        total_downloads = sum(p.downloads for p in self.plugins.values())
        avg_rating = sum(p.rating for p in self.plugins.values()) / total_plugins if total_plugins > 0 else 0

        # 按类别统计
        by_category = {}
        for p in self.plugins.values():
            cat = p.category.value
            if cat not in by_category:
                by_category[cat] = 0
            by_category[cat] += 1

        return {
            "total_plugins": total_plugins,
            "total_downloads": total_downloads,
            "avg_rating": f"{avg_rating:.1f}/5",
            "by_category": by_category,
            "installed_count": len(self.installed_plugins),
        }

    def get_recommended_plugins(self, user_profile: Dict) -> List[StrategyPlugin]:
        """推荐策略插件"""
        difficulty = user_profile.get("difficulty", StrategyDifficulty.BEGINNER)
        category = user_profile.get("category")

        # 基于用户画像推荐
        plugins = self.search_plugins(
            category=category,
            difficulty=difficulty,
            min_rating=3.5,
        )

        return plugins[:10]
