"""
Phase 85: 事件研究框架 (Event Study Framework)

分析特定事件（财报、政策、黑天鹅）对市场的影响
"""


from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np


@dataclass
class EventDefinition:
    """事件定义"""
    name: str
    event_date: str  # YYYY-MM-DD
    event_type: str  # earnings, policy, black_swan, etc.
    description: str
    affected_symbols: List[str]


@dataclass
class EventStudyResult:
    """事件研究结果"""
    event_name: str
    event_date: str
    window_days: int
    cumulative_abnormal_return: float
    max_drawdown: float
    max_runup: float
    recovery_days: Optional[int]
    daily_abnormal_returns: List[float]
    statistical_significance: Dict  # t-stat, p-value

    def to_dict(self) -> Dict:
        return {
            "event": self.event_name,
            "event_date": self.event_date,
            "window_days": self.window_days,
            "car": f"{self.cumulative_abnormal_return:.2%}",
            "max_drawdown": f"{self.max_drawdown:.2%}",
            "max_runup": f"{self.max_runup:.2%}",
            "recovery_days": self.recovery_days,
            "t_stat": self.statistical_significance.get("t_stat", 0),
            "p_value": self.statistical_significance.get("p_value", 1),
            "significant": self.statistical_significance.get("significant", False),
        }


class EventStudyFramework:
    """事件研究框架"""

    def __init__(self, market_data_provider=None):
        self.market_data = market_data_provider
        self.studies = {}

    def run_event_study(
        self,
        event: EventDefinition,
        window: int = 30,  # 事件前后天数
        estimation_window: int = 120,  # 估计窗口
    ) -> EventStudyResult:
        """
        运行事件研究

        Args:
            event: 事件定义
            window: 事件窗口
            estimation_window: 估计窗口（用于计算正常收益）

        Returns:
            事件研究结果
        """
        event_date = datetime.strptime(event.event_date, "%Y-%m-%d")

        # 计算异常收益
        daily_abnormal_returns = []
        start_date = event_date - timedelta(days=window)
        end_date = event_date + timedelta(days=window)

        # 模拟异常收益（实际应从市场数据计算）
        for i in range(-window, window + 1):
            current_date = event_date + timedelta(days=i)

            # 事件日附近有显著异常收益
            if abs(i) <= 3:
                abnormal_return = np.random.normal(0.02, 0.03)  # 事件效应
            else:
                abnormal_return = np.random.normal(0, 0.01)

            daily_abnormal_returns.append(abnormal_return)

        # 计算累计异常收益 (CAR)
        car = sum(daily_abnormal_returns)

        # 计算最大回撤和上涨
        cumulative = np.cumsum(daily_abnormal_returns)
        max_drawdown = min(0, np.min(cumulative))
        max_runup = max(0, np.max(cumulative))

        # 计算恢复天数
        recovery_days = self._calculate_recovery_days(cumulative)

        # 统计显著性
        t_stat, p_value = self._calculate_significance(daily_abnormal_returns)

        result = EventStudyResult(
            event_name=event.name,
            event_date=event.event_date,
            window_days=window,
            cumulative_abnormal_return=car,
            max_drawdown=max_drawdown,
            max_runup=max_runup,
            recovery_days=recovery_days,
            daily_abnormal_returns=daily_abnormal_returns,
            statistical_significance={
                "t_stat": t_stat,
                "p_value": p_value,
                "significant": p_value < 0.05,
            },
        )

        self.studies[event.name] = result
        return result

    def compare_events(self, event_names: List[str]) -> Dict:
        """对比多个事件的影响"""
        comparison = {}

        for name in event_names:
            if name in self.studies:
                comparison[name] = self.studies[name].to_dict()

        return comparison

    def _calculate_recovery_days(self, cumulative_returns: np.ndarray) -> Optional[int]:
        """计算恢复到事件前水平所需天数"""
        if cumulative_returns[-1] >= 0:
            # 找到第一次回到 0 以上的点
            for i, ret in enumerate(cumulative_returns):
                if ret >= 0 and i > len(cumulative_returns) // 2:
                    return i
        return None

    def _calculate_significance(self, abnormal_returns: List[float]) -> Tuple[float, float]:
        """计算统计显著性"""
        if not abnormal_returns:
            return 0.0, 1.0

        arr = np.array(abnormal_returns)
        mean = np.mean(arr)
        std = np.std(arr, ddof=1)

        if std == 0:
            return 0.0, 1.0

        t_stat = mean / (std / np.sqrt(len(arr)))

        # 简化 p-value 计算
        p_value = 2 * (1 - min(abs(t_stat) / 5, 1))  # 近似

        return t_stat, p_value
