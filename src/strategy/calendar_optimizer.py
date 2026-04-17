"""
Phase 92: 交易日历优化系统 (Trading Calendar Optimization)

利用季节性效应优化交易时机
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SeasonalEffect(Enum):
    """季节性效应"""
    JANUARY_EFFECT = "一月效应"
    SELL_IN_MAY = "五月卖出"
    YEAR_END_RALLY = "年末反弹"
    QUARTER_END = "季末效应"
    MONTHLY_REBALANCE = "月度再平衡"
    HOLIDAY_EFFECT = "假日效应"
    EXPiration_WEEK = "期权到期周"


@dataclass
class CalendarSignal:
    """日历信号"""
    date: str
    effect_type: SeasonalEffect
    expected_return: float
    confidence: float
    duration_days: int
    description: str

    def to_dict(self) -> Dict:
        return {
            "date": self.date,
            "effect": self.effect_type.value,
            "expected_return": f"{self.expected_return:.2%}",
            "confidence": f"{self.confidence:.1%}",
            "duration_days": self.duration_days,
            "description": self.description,
        }


@dataclass
class TradingDayAnalysis:
    """交易日分析"""
    date: str
    is_favorable: bool
    signals: List[CalendarSignal]
    recommended_action: str  # buy/hold/reduce
    risk_level: str  # low/medium/high

    def to_dict(self) -> Dict:
        return {
            "date": self.date,
            "is_favorable": self.is_favorable,
            "signals": [s.to_dict() for s in self.signals],
            "recommended_action": self.recommended_action,
            "risk_level": self.risk_level,
        }


class TradingCalendarOptimizer:
    """交易日历优化器"""

    def __init__(self):
        self.seasonal_patterns = self._define_seasonal_patterns()

    def _define_seasonal_patterns(self) -> Dict:
        """定义季节性模式"""
        return {
            "january_effect": {
                "type": SeasonalEffect.JANUARY_EFFECT,
                "month": 1,
                "expected_return": 0.03,
                "confidence": 0.7,
                "description": "一月效应：小盘股表现优异",
            },
            "sell_in_may": {
                "type": SeasonalEffect.SELL_IN_MAY,
                "month": 5,
                "expected_return": -0.02,
                "confidence": 0.6,
                "description": "五月卖出：夏季市场疲软",
            },
            "year_end_rally": {
                "type": SeasonalEffect.YEAR_END_RALLY,
                "month": 12,
                "expected_return": 0.02,
                "confidence": 0.65,
                "description": "年末反弹：机构建仓推升市场",
            },
            "quarter_end_rebalance": {
                "type": SeasonalEffect.QUARTER_END,
                "months": [3, 6, 9, 12],
                "expected_return": 0.01,
                "confidence": 0.55,
                "description": "季末再平衡：机构调仓效应",
            },
            "monthly_rebalance": {
                "type": SeasonalEffect.MONTHLY_REBALANCE,
                "day_of_month": [1, 15],
                "expected_return": 0.005,
                "confidence": 0.5,
                "description": "月初/月中再平衡效应",
            },
        }

    def analyze_date(self, date_str: str) -> TradingDayAnalysis:
        """
        分析指定交易日

        Args:
            date_str: 日期字符串 (YYYY-MM-DD)

        Returns:
            交易日分析
        """
        date = datetime.strptime(date_str, "%Y-%m-%d")
        signals = []

        # 检查所有季节性模式
        for pattern_name, pattern in self.seasonal_patterns.items():
            if self._check_pattern(date, pattern):
                signal = CalendarSignal(
                    date=date_str,
                    effect_type=pattern["type"],
                    expected_return=pattern["expected_return"],
                    confidence=pattern["confidence"],
                    duration_days=pattern.get("duration", 5),
                    description=pattern["description"],
                )
                signals.append(signal)

        # 综合评估
        is_favorable = any(s.expected_return > 0 for s in signals)
        total_expected_return = sum(s.expected_return * s.confidence for s in signals)

        # 推荐操作
        if total_expected_return > 0.02:
            action = "buy"
            risk = "low"
        elif total_expected_return > 0:
            action = "hold"
            risk = "medium"
        elif total_expected_return > -0.02:
            action = "hold"
            risk = "medium"
        else:
            action = "reduce"
            risk = "high"

        return TradingDayAnalysis(
            date=date_str,
            is_favorable=is_favorable,
            signals=signals,
            recommended_action=action,
            risk_level=risk,
        )

    def analyze_period(
        self,
        start_date: str,
        end_date: str,
    ) -> List[TradingDayAnalysis]:
        """
        分析时间段内的所有交易日

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            交易日分析列表
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        analyses = []
        current = start

        while current <= end:
            # 跳过周末
            if current.weekday() < 5:
                date_str = current.strftime("%Y-%m-%d")
                analysis = self.analyze_date(date_str)
                analyses.append(analysis)
            current = current.replace(day=current.day + 1)

        return analyses

    def get_favorable_dates(
        self,
        start_date: str,
        end_date: str,
        min_confidence: float = 0.6,
    ) -> List[Dict]:
        """
        获取有利交易日期

        Args:
            start_date: 开始日期
            end_date: 结束日期
            min_confidence: 最低置信度

        Returns:
            有利日期列表
        """
        analyses = self.analyze_period(start_date, end_date)

        favorable = []
        for analysis in analyses:
            if analysis.is_favorable and any(s.confidence >= min_confidence for s in analysis.signals):
                favorable.append(analysis.to_dict())

        return favorable

    def _check_pattern(self, date: datetime, pattern: Dict) -> bool:
        """检查日期是否匹配季节性模式"""
        if "month" in pattern:
            return date.month == pattern["month"]
        elif "months" in pattern:
            return date.month in pattern["months"]
        elif "day_of_month" in pattern:
            return date.day in pattern["day_of_month"]
        return False

    def get_calendar_summary(self, year: int = 2024) -> Dict:
        """获取年度日历总结"""
        favorable_count = 0
        unfavorable_count = 0
        total_days = 0

        for month in range(1, 13):
            for day in range(1, 32):
                try:
                    date = datetime(year, month, day)
                    if date.weekday() >= 5:
                        continue

                    date_str = date.strftime("%Y-%m-%d")
                    analysis = self.analyze_date(date_str)

                    total_days += 1
                    if analysis.is_favorable:
                        favorable_count += 1
                    else:
                        unfavorable_count += 1
                except ValueError:
                    break

        return {
            "year": year,
            "total_trading_days": total_days,
            "favorable_days": favorable_count,
            "unfavorable_days": unfavorable_count,
            "favorable_ratio": f"{favorable_count / total_days:.1%}" if total_days > 0 else "0%",
            "key_seasonal_events": [
                "1月：一月效应",
                "5月：五月卖出",
                "3/6/9/12月：季末再平衡",
                "12月：年末反弹",
            ],
        }
