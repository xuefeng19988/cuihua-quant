"""
Phase 87: 压力测试系统 (Stress Testing System)

极端场景模拟与组合韧性评估
"""


from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class StressScenario(Enum):
    """压力场景"""
    MARKET_CRASH = "市场崩盘"
    FLASH_CRASH = "闪崩"
    PANDEMIC = "疫情爆发"
    FINANCIAL_CRISIS = "金融危机"
    INTEREST_RATE_SHOCK = "利率冲击"
    CURRENCY_CRISIS = "货币危机"
    SECTOR_ROTATION = "板块轮动"
    LIQUIDITY_CRISIS = "流动性危机"


@dataclass
class StressScenarioDef:
    """压力场景定义"""
    name: str
    description: str
    market_shock: float  # 市场整体跌幅
    sector_shocks: Dict[str, float]  # 各板块跌幅
    volatility_multiplier: float  # 波动率倍数
    correlation_increase: float  # 相关性增加
    duration_days: int  # 持续天数


@dataclass
class StressTestResult:
    """压力测试结果"""
    scenario: str
    portfolio_loss: float
    worst_drawdown: float
    recovery_time_days: Optional[int]
    var_95: float
    var_99: float
    liquidity_impact: float
    margin_call_risk: bool
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            "scenario": self.scenario,
            "portfolio_loss": f"{self.portfolio_loss:.2%}",
            "worst_drawdown": f"{self.worst_drawdown:.2%}",
            "recovery_time_days": self.recovery_time_days,
            "var_95": f"{self.var_95:.2%}",
            "var_99": f"{self.var_99:.2%}",
            "liquidity_impact": f"{self.liquidity_impact:.2%}",
            "margin_call_risk": self.margin_call_risk,
            "recommendations": self.recommendations,
        }


class StressTestingSystem:
    """压力测试系统"""

    def __init__(self):
        self.scenarios = self._define_scenarios()
        self.results = []

    def _define_scenarios(self) -> Dict[str, StressScenarioDef]:
        """定义压力场景"""
        return {
            "market_crash": StressScenarioDef(
                name="市场崩盘",
                description="类似 2008 年金融危机",
                market_shock=-0.40,
                sector_shocks={"金融": -0.50, "科技": -0.35, "消费": -0.30, "能源": -0.45},
                volatility_multiplier=2.5,
                correlation_increase=0.3,
                duration_days=180,
            ),
            "flash_crash": StressScenarioDef(
                name="闪崩",
                description="类似 2010 年闪崩",
                market_shock=-0.10,
                sector_shocks={"科技": -0.15, "金融": -0.12, "消费": -0.08},
                volatility_multiplier=4.0,
                correlation_increase=0.4,
                duration_days=5,
            ),
            "pandemic": StressScenarioDef(
                name="疫情爆发",
                description="类似 2020 年新冠疫情",
                market_shock=-0.30,
                sector_shocks={"消费": -0.40, "能源": -0.50, "科技": -0.20, "医疗": +0.10},
                volatility_multiplier=3.0,
                correlation_increase=0.25,
                duration_days=90,
            ),
            "interest_rate_shock": StressScenarioDef(
                name="利率冲击",
                description="央行突然加息 200bps",
                market_shock=-0.15,
                sector_shocks={"金融": +0.10, "地产": -0.25, "科技": -0.20, "公用事业": -0.15},
                volatility_multiplier=1.8,
                correlation_increase=0.15,
                duration_days=60,
            ),
            "liquidity_crisis": StressScenarioDef(
                name="流动性危机",
                description="市场流动性枯竭",
                market_shock=-0.25,
                sector_shocks={"金融": -0.35, "科技": -0.30, "消费": -0.20},
                volatility_multiplier=3.5,
                correlation_increase=0.5,
                duration_days=30,
            ),
        }

    def run_stress_test(
        self,
        portfolio: Dict,
        scenario_name: str,
    ) -> StressTestResult:
        """
        运行压力测试

        Args:
            portfolio: 组合信息 {weights, sectors, leverage, cash}
            scenario_name: 场景名称

        Returns:
            压力测试结果
        """
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        scenario = self.scenarios[scenario_name]

        # 计算组合损失
        portfolio_loss = self._calculate_portfolio_loss(portfolio, scenario)

        # 计算最大回撤
        worst_drawdown = portfolio_loss * 1.2  # 简化：峰值到谷底

        # 计算 VaR
        var_95 = portfolio_loss * 0.8
        var_99 = portfolio_loss * 1.2

        # 流动性冲击
        liquidity_impact = portfolio_loss * 0.15

        # 保证金追缴风险
        leverage = portfolio.get("leverage", 1.0)
        margin_call_risk = leverage > 2.0 and portfolio_loss < -0.20

        # 恢复时间估算
        recovery_time = self._estimate_recovery_time(scenario, portfolio_loss)

        # 建议
        recommendations = self._generate_recommendations(scenario, portfolio_loss, leverage)

        result = StressTestResult(
            scenario=scenario.name,
            portfolio_loss=portfolio_loss,
            worst_drawdown=worst_drawdown,
            recovery_time_days=recovery_time,
            var_95=var_95,
            var_99=var_99,
            liquidity_impact=liquidity_impact,
            margin_call_risk=margin_call_risk,
            recommendations=recommendations,
        )

        self.results.append(result)
        return result

    def run_all_scenarios(self, portfolio: Dict) -> List[StressTestResult]:
        """运行所有压力场景"""
        results = []
        for scenario_name in self.scenarios:
            result = self.run_stress_test(portfolio, scenario_name)
            results.append(result)
        return results

    def _calculate_portfolio_loss(
        self,
        portfolio: Dict,
        scenario: StressScenarioDef,
    ) -> float:
        """计算组合损失"""
        weights = portfolio.get("weights", {})
        sectors = portfolio.get("sectors", {})

        total_loss = 0

        for sector, weight in weights.items():
            sector_shock = scenario.sector_shocks.get(sector, scenario.market_shock)
            total_loss += weight * sector_shock

        # 相关性增加导致分散化失效
        correlation_penalty = scenario.correlation_increase * 0.1
        total_loss *= (1 + correlation_penalty)

        return total_loss

    def _estimate_recovery_time(
        self,
        scenario: StressScenarioDef,
        portfolio_loss: float,
    ) -> int:
        """估算恢复时间"""
        base_recovery = scenario.duration_days
        loss_factor = abs(portfolio_loss) * 10
        return int(base_recovery * loss_factor)

    def _generate_recommendations(
        self,
        scenario: StressScenarioDef,
        portfolio_loss: float,
        leverage: float,
    ) -> List[str]:
        """生成应对建议"""
        recommendations = []

        if portfolio_loss < -0.30:
            recommendations.append("🚨 考虑降低仓位至 50% 以下")
        elif portfolio_loss < -0.20:
            recommendations.append("⚠️ 考虑减仓至 70%")

        if leverage > 2.0:
            recommendations.append("🔴 高杠杆风险，建议降杠杆至 1.5x 以下")

        if scenario.correlation_increase > 0.3:
            recommendations.append("📊 分散化失效，增加非相关资产")

        if scenario.volatility_multiplier > 2.5:
            recommendations.append("📈 波动率激增，考虑对冲策略")

        recommendations.append("💰 保持充足现金储备（至少 20%）")

        return recommendations

    def get_worst_case(self) -> Optional[StressTestResult]:
        """获取最坏场景"""
        if not self.results:
            return None
        return min(self.results, key=lambda x: x.portfolio_loss)

    def get_summary(self) -> Dict:
        """获取压力测试总结"""
        if not self.results:
            return {"error": "No stress test results"}

        avg_loss = sum(r.portfolio_loss for r in self.results) / len(self.results)
        worst = self.get_worst_case()

        return {
            "scenarios_tested": len(self.results),
            "avg_loss": f"{avg_loss:.2%}",
            "worst_scenario": worst.scenario if worst else "N/A",
            "worst_loss": f"{worst.portfolio_loss:.2%}" if worst else "N/A",
            "margin_call_risk_count": sum(1 for r in self.results if r.margin_call_risk),
        }
