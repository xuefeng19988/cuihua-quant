"""
Phase 84: 策略健康度监控系统 (Strategy Health Monitor)

实时监控策略运行状态和绩效指标
"""


from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time


class StrategyStatus(Enum):
    """策略状态"""
    ACTIVE = "运行中"
    PAUSED = "已暂停"
    DISABLED = "已禁用"
    ERROR = "异常"
    DRAWDOWN = "回撤中"


class HealthLevel(Enum):
    """健康等级"""
    HEALTHY = "健康"
    WARNING = "警告"
    CRITICAL = "严重"


@dataclass
class HealthMetric:
    """健康指标"""
    name: str
    value: float
    threshold_warning: float
    threshold_critical: float
    description: str

    def check(self) -> HealthLevel:
        """检查指标状态"""
        if self.value <= self.threshold_critical:
            return HealthLevel.CRITICAL
        elif self.value <= self.threshold_warning:
            return HealthLevel.WARNING
        return HealthLevel.HEALTHY

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": round(self.value, 4),
            "status": self.check().value,
            "description": self.description,
        }


@dataclass
class StrategyHealthReport:
    """策略健康报告"""
    strategy_name: str
    status: StrategyStatus
    overall_health: HealthLevel
    metrics: List[HealthMetric]
    last_update: float
    alerts: List[str]

    def to_dict(self) -> Dict:
        return {
            "strategy": self.strategy_name,
            "status": self.status.value,
            "overall_health": self.overall_health.value,
            "metrics": [m.to_dict() for m in self.metrics],
            "last_update": datetime.fromtimestamp(self.last_update).strftime("%Y-%m-%d %H:%M:%S"),
            "alerts": self.alerts,
        }


class StrategyHealthMonitor:
    """策略健康度监控器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.reports: Dict[str, StrategyHealthReport] = {}
        self.history: List[StrategyHealthReport] = []

        # 默认阈值
        self.max_drawdown_warning = self.config.get("max_drawdown_warning", -0.1)  # -10%
        self.max_drawdown_critical = self.config.get("max_drawdown_critical", -0.2)  # -20%
        self.min_sharpe_warning = self.config.get("min_sharpe_warning", 0.5)
        self.min_sharpe_critical = self.config.get("min_sharpe_critical", 0.0)
        self.max_correlation_warning = self.config.get("max_correlation_warning", 0.7)

    def check_strategy(
        self,
        strategy_name: str,
        performance_data: Dict,
    ) -> StrategyHealthReport:
        """
        检查策略健康度

        Args:
            strategy_name: 策略名称
            performance_data: 绩效数据

        Returns:
            健康报告
        """
        metrics = []
        alerts = []
        overall_health = HealthLevel.HEALTHY

        # 1. 最大回撤指标
        max_drawdown = performance_data.get("max_drawdown", 0)
        drawdown_metric = HealthMetric(
            name="最大回撤",
            value=max_drawdown,
            threshold_warning=self.max_drawdown_warning,
            threshold_critical=self.max_drawdown_critical,
            description=f"当前回撤: {max_drawdown:.2%}",
        )
        metrics.append(drawdown_metric)

        drawdown_status = drawdown_metric.check()
        if drawdown_status == HealthLevel.CRITICAL:
            alerts.append(f"🚨 回撤超过临界值 ({self.max_drawdown_critical:.0%})")
            overall_health = HealthLevel.CRITICAL
        elif drawdown_status == HealthLevel.WARNING and overall_health != HealthLevel.CRITICAL:
            alerts.append(f"⚠️ 回撤超过警告值 ({self.max_drawdown_warning:.0%})")
            if overall_health == HealthLevel.HEALTHY:
                overall_health = HealthLevel.WARNING

        # 2. 夏普比率指标
        sharpe = performance_data.get("sharpe_ratio", 0)
        sharpe_metric = HealthMetric(
            name="夏普比率",
            value=sharpe,
            threshold_warning=self.min_sharpe_warning,
            threshold_critical=self.min_sharpe_critical,
            description=f"当前夏普: {sharpe:.2f}",
        )
        metrics.append(sharpe_metric)

        sharpe_status = sharpe_metric.check()
        if sharpe_status == HealthLevel.CRITICAL:
            alerts.append(f"🚨 夏普比率低于临界值 ({self.min_sharpe_critical:.1f})")
            overall_health = HealthLevel.CRITICAL
        elif sharpe_status == HealthLevel.WARNING and overall_health != HealthLevel.CRITICAL:
            alerts.append(f"⚠️ 夏普比率低于警告值 ({self.min_sharpe_warning:.1f})")
            if overall_health == HealthLevel.HEALTHY:
                overall_health = HealthLevel.WARNING

        # 3. 胜率指标
        win_rate = performance_data.get("win_rate", 0.5)
        winrate_metric = HealthMetric(
            name="胜率",
            value=win_rate,
            threshold_warning=0.45,
            threshold_critical=0.40,
            description=f"当前胜率: {win_rate:.2%}",
        )
        metrics.append(winrate_metric)

        # 4. 盈亏比指标
        profit_factor = performance_data.get("profit_factor", 1.0)
        pf_metric = HealthMetric(
            name="盈亏比",
            value=profit_factor,
            threshold_warning=1.0,
            threshold_critical=0.8,
            description=f"当前盈亏比: {profit_factor:.2f}",
        )
        metrics.append(pf_metric)

        # 5. 策略相关性
        correlation = performance_data.get("correlation", 0)
        corr_metric = HealthMetric(
            name="策略相关性",
            value=correlation,
            threshold_warning=self.max_correlation_warning,
            threshold_critical=0.9,
            description=f"与其他策略相关性: {correlation:.2f}",
        )
        metrics.append(corr_metric)

        # 确定策略状态
        status = StrategyStatus.ACTIVE
        if overall_health == HealthLevel.CRITICAL:
            status = StrategyStatus.DRAWDOWN

        report = StrategyHealthReport(
            strategy_name=strategy_name,
            status=status,
            overall_health=overall_health,
            metrics=metrics,
            last_update=time.time(),
            alerts=alerts,
        )

        self.reports[strategy_name] = report
        self.history.append(report)

        return report

    def check_all_strategies(self, strategies_data: Dict[str, Dict]) -> Dict[str, StrategyHealthReport]:
        """
        批量检查所有策略

        Args:
            strategies_data: {strategy_name: performance_data}

        Returns:
            {strategy_name: health_report}
        """
        results = {}
        for name, data in strategies_data.items():
            results[name] = self.check_strategy(name, data)
        return results

    def get_portfolio_health(self) -> Dict:
        """获取组合整体健康状况"""
        if not self.reports:
            return {"error": "No strategy reports available"}

        total_strategies = len(self.reports)
        healthy_count = sum(1 for r in self.reports.values() if r.overall_health == HealthLevel.HEALTHY)
        warning_count = sum(1 for r in self.reports.values() if r.overall_health == HealthLevel.WARNING)
        critical_count = sum(1 for r in self.reports.values() if r.overall_health == HealthLevel.CRITICAL)

        # 找出最不健康的策略
        worst_strategy = min(
            self.reports.values(),
            key=lambda r: {"healthy": 2, "warning": 1, "critical": 0}[r.overall_health.value],
        )

        return {
            "total_strategies": total_strategies,
            "healthy_count": healthy_count,
            "warning_count": warning_count,
            "critical_count": critical_count,
            "health_rate": f"{healthy_count / total_strategies:.1%}",
            "worst_strategy": worst_strategy.strategy_name,
            "worst_health": worst_strategy.overall_health.value,
            "alerts": [alert for r in self.reports.values() for alert in r.alerts],
        }

    def get_history(self, strategy_name: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """获取历史健康报告"""
        filtered = self.history
        if strategy_name:
            filtered = [r for r in filtered if r.strategy_name == strategy_name]
        return [r.to_dict() for r in filtered[-limit:]]
