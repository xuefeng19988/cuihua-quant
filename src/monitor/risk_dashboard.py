"""
Phase 105: 实时风险仪表板 (Real-time Risk Dashboard)

动态风险监控与可视化
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import time


class RiskLevel(Enum):
    """风险等级"""
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"
    CRITICAL = "严重风险"


@dataclass
class RiskMetric:
    """风险指标"""
    name: str
    value: float
    threshold_warning: float
    threshold_critical: float
    level: RiskLevel
    description: str

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": round(self.value, 4),
            "warning_threshold": self.threshold_warning,
            "critical_threshold": self.threshold_critical,
            "level": self.level.value,
            "description": self.description,
        }


@dataclass
class RiskExposure:
    """风险敞口"""
    asset_class: str
    exposure: float
    weight: float
    var_95: float
    contribution_to_risk: float

    def to_dict(self) -> Dict:
        return {
            "asset_class": self.asset_class,
            "exposure": f"¥{self.exposure:,.2f}",
            "weight": f"{self.weight:.2%}",
            "var_95": f"¥{self.var_95:,.2f}",
            "risk_contribution": f"{self.contribution_to_risk:.2%}",
        }


@dataclass
class RiskDashboardData:
    """风险仪表板数据"""
    timestamp: float
    overall_risk_level: RiskLevel
    risk_metrics: List[RiskMetric]
    risk_exposures: List[RiskExposure]
    concentration_risks: List[Dict]
    alerts: List[str]
    portfolio_var: float
    portfolio_cvar: float

    def to_dict(self) -> Dict:
        return {
            "timestamp": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "overall_risk_level": self.overall_risk_level.value,
            "risk_metrics": [m.to_dict() for m in self.risk_metrics],
            "risk_exposures": [e.to_dict() for e in self.risk_exposures],
            "concentration_risks": self.concentration_risks,
            "alerts": self.alerts,
            "portfolio_var_95": f"¥{self.portfolio_var:,.2f}",
            "portfolio_cvar_95": f"¥{self.portfolio_cvar:,.2f}",
        }


class RealtimeRiskDashboard:
    """实时风险仪表板"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.history = []

    def update_dashboard(
        self,
        portfolio_data: Dict,
        market_data: Optional[Dict] = None,
    ) -> RiskDashboardData:
        """
        更新风险仪表板

        Args:
            portfolio_data: 组合数据
            market_data: 市场数据

        Returns:
            仪表板数据
        """
        metrics = []
        alerts = []
        overall_level = RiskLevel.LOW

        # 1. VaR 指标
        var_95 = portfolio_data.get("var_95", 0)
        var_threshold = self.config.get("var_warning", 50000)
        var_critical = self.config.get("var_critical", 100000)

        var_level = self._determine_risk_level(var_95, var_threshold, var_critical)
        metrics.append(RiskMetric(
            name="VaR (95%)",
            value=var_95,
            threshold_warning=var_threshold,
            threshold_critical=var_critical,
            level=var_level,
            description=f"95% 置信度下的最大日亏损",
        ))

        if var_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            alerts.append(f"🚨 VaR 超过{var_level.value}阈值: ¥{var_95:,.0f}")

        # 2. 最大回撤
        max_dd = portfolio_data.get("max_drawdown", 0)
        dd_warning = self.config.get("drawdown_warning", -0.1)
        dd_critical = self.config.get("drawdown_critical", -0.2)

        dd_level = self._determine_risk_level(abs(max_dd), abs(dd_warning), abs(dd_critical))
        metrics.append(RiskMetric(
            name="最大回撤",
            value=max_dd,
            threshold_warning=dd_warning,
            threshold_critical=dd_critical,
            level=dd_level,
            description=f"历史最大峰值到当前谷值的跌幅",
        ))

        if dd_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            alerts.append(f"🚨 回撤超过{dd_level.value}阈值: {max_dd:.2%}")

        # 3. 杠杆率
        leverage = portfolio_data.get("leverage", 1.0)
        lev_warning = self.config.get("leverage_warning", 1.5)
        lev_critical = self.config.get("leverage_critical", 2.0)

        lev_level = self._determine_risk_level(leverage, lev_warning, lev_critical)
        metrics.append(RiskMetric(
            name="杠杆率",
            value=leverage,
            threshold_warning=lev_warning,
            threshold_critical=lev_critical,
            level=lev_level,
            description=f"总持仓与净值的比率",
        ))

        # 4. 集中度
        max_position = portfolio_data.get("max_position_weight", 0)
        conc_warning = self.config.get("concentration_warning", 0.2)
        conc_critical = self.config.get("concentration_critical", 0.3)

        conc_level = self._determine_risk_level(max_position, conc_warning, conc_critical)
        metrics.append(RiskMetric(
            name="持仓集中度",
            value=max_position,
            threshold_warning=conc_warning,
            threshold_critical=conc_critical,
            level=conc_level,
            description=f"最大单一持仓占比",
        ))

        # 5. 波动率
        volatility = portfolio_data.get("volatility", 0.15)
        vol_warning = self.config.get("volatility_warning", 0.25)
        vol_critical = self.config.get("volatility_critical", 0.4)

        vol_level = self._determine_risk_level(volatility, vol_warning, vol_critical)
        metrics.append(RiskMetric(
            name="组合波动率",
            value=volatility,
            threshold_warning=vol_warning,
            threshold_critical=vol_critical,
            level=vol_level,
            description=f"年化波动率",
        ))

        # 确定整体风险等级
        all_levels = [m.level for m in metrics]
        if RiskLevel.CRITICAL in all_levels:
            overall_level = RiskLevel.CRITICAL
        elif RiskLevel.HIGH in all_levels:
            overall_level = RiskLevel.HIGH
        elif RiskLevel.MEDIUM in all_levels:
            overall_level = RiskLevel.MEDIUM

        # 风险敞口
        exposures = self._calculate_risk_exposures(portfolio_data)

        # 集中度风险
        concentration_risks = self._identify_concentration_risks(portfolio_data)

        # CVaR
        cvar = portfolio_data.get("cvar_95", var_95 * 1.3)

        dashboard = RiskDashboardData(
            timestamp=time.time(),
            overall_risk_level=overall_level,
            risk_metrics=metrics,
            risk_exposures=exposures,
            concentration_risks=concentration_risks,
            alerts=alerts,
            portfolio_var=var_95,
            portfolio_cvar=cvar,
        )

        self.history.append(dashboard)
        return dashboard

    def _determine_risk_level(self, value: float, warning: float, critical: float) -> RiskLevel:
        """确定风险等级"""
        if value >= critical:
            return RiskLevel.CRITICAL
        elif value >= warning:
            return RiskLevel.HIGH
        elif value >= warning * 0.7:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _calculate_risk_exposures(self, portfolio_data: Dict) -> List[RiskExposure]:
        """计算风险敞口"""
        exposures = portfolio_data.get("sector_exposures", {})
        total_value = portfolio_data.get("total_value", 1)

        result = []
        for sector, data in exposures.items():
            exposure = data.get("value", 0)
            weight = data.get("weight", 0)
            var = data.get("var", 0)
            contribution = data.get("risk_contribution", 0)

            result.append(RiskExposure(
                asset_class=sector,
                exposure=exposure,
                weight=weight,
                var_95=var,
                contribution_to_risk=contribution,
            ))

        return result

    def _identify_concentration_risks(self, portfolio_data: Dict) -> List[Dict]:
        """识别集中度风险"""
        positions = portfolio_data.get("positions", {})
        total_value = portfolio_data.get("total_value", 1)
        risks = []

        for symbol, pos in positions.items():
            weight = pos.get("weight", 0)
            if weight > 0.2:
                risks.append({
                    "symbol": symbol,
                    "weight": f"{weight:.2%}",
                    "risk": "超过 20% 集中度限制",
                })

        return risks

    def get_risk_history(self, limit: int = 24) -> List[Dict]:
        """获取风险历史"""
        return [d.to_dict() for d in self.history[-limit:]]
