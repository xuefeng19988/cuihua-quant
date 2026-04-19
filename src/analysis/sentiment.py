"""
Sentiment Analysis Module
Analyzes news and social media sentiment for stocks.
Includes: StockSentimentAnalyzer, NewsSentimentFetcher, MarketSentimentAnalyzer
"""

import os
import re
import yaml
import jieba
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


# ============================================================
# Part 1: Stock-level Sentiment Analysis (from original sentiment.py)
# ============================================================

class StockSentimentAnalyzer:
    """
    Analyzes sentiment of news articles related to specific stocks.
    Uses a dictionary-based approach with keyword matching.
    """

    def __init__(self):
        # Sentiment dictionary (Positive/Negative keywords)
        self.positive_words = [
            '上涨', '突破', '利好', '增长', '盈利', '创新高', '涨停',
            '牛市', '大涨', '飙升', '爆发', '超预期', '强势', '领涨',
            '复苏', '回暖', '利好', '放量', '资金流入', '机构看好',
            '突破', '新高', '盈利', '增长', '改善', '强劲', '乐观'
        ]

        self.negative_words = [
            '下跌', '暴跌', '利空', '亏损', '跳水', '跌停', '熊市',
            '大跌', '崩盘', '下滑', '恶化', '疲软', '资金流出',
            '机构看空', '破位', '新低', '亏损', '下滑', '恶化',
            '监管', '处罚', '违规', '诉讼', '退市', '减持', '清仓'
        ]

        # Stock name to code mapping (Common names)
        self.stock_keywords = {
            '茅台': 'SH.600519',
            '五粮液': 'SZ.000858',
            '比亚迪': 'SZ.002594',
            '宁德时代': 'SZ.300750',
            '腾讯': 'HK.00700',
            '阿里巴巴': 'HK.09988',
            '美团': 'HK.03690',
            '小米': 'HK.01810',
            '平安': 'SH.601318',
            '招商': 'SH.600036',
            '东方财富': 'SZ.300059',
            '海康威视': 'SZ.002415',
            '格力': 'SZ.000651',
            '美的': 'SZ.000333',
            '中免': 'SH.601888',
            '科大讯飞': 'SZ.002230',
            '隆基': 'SH.601012',
            '亿纬锂能': 'SZ.300014',
            '京东': 'HK.09618',
            '快手': 'HK.01024',
            '百度': 'HK.09888',
            '泡泡玛特': 'HK.09992',
            '名创优品': 'HK.09896',
            '海底捞': 'HK.06862',
        }

    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment of a single text."""
        words = jieba.lcut(text)
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)

        total = pos_count + neg_count
        if total == 0:
            score = 0.0
            label = 'neutral'
        else:
            score = (pos_count - neg_count) / total
            if score > 0.2:
                label = 'positive'
            elif score < -0.2:
                label = 'negative'
            else:
                label = 'neutral'

        return {
            'score': score, 'label': label,
            'pos_count': pos_count, 'neg_count': neg_count,
            'total_keywords': total
        }

    def analyze_news_for_stocks(self, news_items: List[Dict]) -> Dict[str, List[Dict]]:
        """Analyze a list of news items and map sentiment to stocks."""
        stock_sentiments = {}
        for item in news_items:
            title = item.get('title', '')
            content = item.get('content', '')
            full_text = title + ' ' + content
            mentioned_stocks = self._find_mentioned_stocks(full_text)
            sentiment = self.analyze_text(full_text)
            for code in mentioned_stocks:
                if code not in stock_sentiments:
                    stock_sentiments[code] = []
                stock_sentiments[code].append({
                    'title': title,
                    'sentiment': sentiment,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
        return stock_sentiments

    def _find_mentioned_stocks(self, text: str) -> List[str]:
        """Find which stocks are mentioned in text."""
        return [code for keyword, code in self.stock_keywords.items() if keyword in text]

    def get_aggregate_sentiment(self, stock_sentiments: Dict[str, List[Dict]]) -> pd.DataFrame:
        """Calculate aggregate sentiment score per stock."""
        rows = []
        for code, sentiments in stock_sentiments.items():
            scores = [s['sentiment']['score'] for s in sentiments]
            avg_score = sum(scores) / len(scores) if scores else 0.0
            if avg_score > 0.2:
                label = 'positive'
            elif avg_score < -0.2:
                label = 'negative'
            else:
                label = 'neutral'
            rows.append({
                'code': code, 'avg_score': avg_score,
                'news_count': len(sentiments), 'label': label,
                'date': datetime.now().strftime('%Y-%m-%d')
            })
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values('avg_score', ascending=False).reset_index(drop=True)
        return df


# ============================================================
# Part 2: News Sentiment Fetcher (from news_sentiment.py)
# ============================================================

class NewsSentimentFetcher:
    """Fetches news from TrendRadar and generates sentiment scores for stocks."""

    def __init__(self, trendradar_dir: str = None):
        if trendradar_dir is None:
            trendradar_dir = os.path.join(project_root, '../TrendRadar/rss/news')
        self.trendradar_dir = trendradar_dir
        self.analyzer = StockSentimentAnalyzer()

    def get_latest_db(self) -> str:
        """Find latest TrendRadar DB."""
        for days in range(3):
            date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            db_path = os.path.join(self.trendradar_dir, f'{date}.db')
            if os.path.exists(db_path):
                return db_path
        return None

    def fetch_news(self, limit: int = 100) -> List[Dict]:
        """Fetch news items from TrendRadar DB."""
        db_path = self.get_latest_db()
        if not db_path:
            return []
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if not tables:
                conn.close()
                return []
            table = tables[0][0]
            cursor.execute(f"SELECT * FROM :table LIMIT :limit")
            rows = cursor.fetchall()
            if not rows:
                conn.close()
                return []
            cols = [d[0] for d in cursor.description]
            news = []
            for row in rows:
                item = dict(zip(cols, row))
                news.append({
                    'title': item.get('title', ''),
                    'content': item.get('content', item.get('summary', '')),
                    'url': item.get('url', item.get('link', '')),
                    'date': item.get('date', item.get('created_at', ''))
                })
            conn.close()
            return news
        except Exception as e:
            print(f"⚠️ News fetch error: {e}")
            return []

    def analyze_and_score(self, codes: List[str]) -> Dict[str, float]:
        """Analyze news sentiment for stocks."""
        news_items = self.fetch_news()
        if not news_items:
            return {}
        stock_sentiments = self.analyzer.analyze_news_for_stocks(news_items)
        agg = self.analyzer.get_aggregate_sentiment(stock_sentiments)
        if agg.empty:
            return {}
        return dict(zip(agg['code'], agg['avg_score']))


# ============================================================
# Part 3: Market Sentiment Indicators (from sentiment_indicators.py)
# ============================================================

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
    weight: float
    description: str

    def to_dict(self) -> Dict:
        return {
            "name": self.name, "value": round(self.value, 4),
            "weight": self.weight, "description": self.description,
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
        self.indicators[name] = {"calculator": calculator, "weight": weight}

    def analyze(self, market_data: Dict, include_context: bool = True) -> SentimentReport:
        """综合分析市场情绪"""
        indicators = []
        total_weight = 0
        weighted_sum = 0

        for name, config in self.indicators.items():
            try:
                value = config["calculator"](market_data)
                weight = config["weight"]
                indicator = SentimentIndicator(
                    name=name, value=value, weight=weight,
                    description=self._get_indicator_description(name, value),
                )
                indicators.append(indicator)
                weighted_sum += value * weight
                total_weight += weight
            except Exception:
                continue

        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        sentiment_level = self._classify_sentiment(overall_score)
        market_context = {}
        if include_context:
            market_context = self._analyze_market_context(market_data)

        return SentimentReport(
            timestamp=datetime.now().timestamp(), overall_score=overall_score,
            sentiment_level=sentiment_level, indicators=indicators,
            market_context=market_context,
        )

    def _classify_sentiment(self, score: float) -> SentimentLevel:
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
    vix = market_data.get("vix", 20)
    return (30 - vix) / 15


def put_call_ratio_calculator(market_data: Dict) -> float:
    ratio = market_data.get("put_call_ratio", 1.0)
    return (1.2 - ratio) / 0.5


def advance_decline_calculator(market_data: Dict) -> float:
    advance = market_data.get("advance", 1000)
    decline = market_data.get("decline", 1000)
    total = advance + decline
    if total == 0:
        return 0.0
    return (advance - decline) / total


def volume_ratio_calculator(market_data: Dict) -> float:
    current_volume = market_data.get("current_volume", 0)
    avg_volume = market_data.get("avg_volume", 1)
    if avg_volume == 0:
        return 0.0
    ratio = current_volume / avg_volume
    return min(max((ratio - 1.0) / 0.5, -1), 1)


def momentum_calculator(market_data: Dict) -> float:
    returns = market_data.get("recent_returns", [])
    if not returns:
        return 0.0
    avg_return = sum(returns) / len(returns)
    return min(max(avg_return * 10, -1), 1)
