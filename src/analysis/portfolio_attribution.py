"""
Phase 86: 组合归因分析系统 (Portfolio Attribution Analysis)

Brinson 归因模型：资产配置、个股选择、交互效应
"""


from typing import Dict, List
from dataclasses import dataclass


@dataclass
class AttributionResult:
    """归因结果"""
    period: str
    total_return: float
    benchmark_return: float
    active_return: float

    # Brinson 归因
    allocation_effect: float  # 资产配置效应
    selection_effect: float  # 个股选择效应
    interaction_effect: float  # 交互效应

    # 详细分解
    sector_allocation: Dict[str, float]
    security_selection: Dict[str, float]

    def to_dict(self) -> Dict:
        return {
            "period": self.period,
            "total_return": f"{self.total_return:.2%}",
            "benchmark_return": f"{self.benchmark_return:.2%}",
            "active_return": f"{self.active_return:.2%}",
            "allocation_effect": f"{self.allocation_effect:.2%}",
            "selection_effect": f"{self.selection_effect:.2%}",
            "interaction_effect": f"{self.interaction_effect:.2%}",
            "total_attribution": f"{self.allocation_effect + self.selection_effect + self.interaction_effect:.2%}",
            "sector_allocation": {k: f"{v:.2%}" for k, v in self.sector_allocation.items()},
            "security_selection": {k: f"{v:.2%}" for k, v in self.security_selection.items()},
        }


class PortfolioAttributionAnalyzer:
    """组合归因分析器"""

    def __init__(self):
        pass

    def brinson_attribution(
        self,
        portfolio_weights: Dict[str, float],
        portfolio_returns: Dict[str, float],
        benchmark_weights: Dict[str, float],
        benchmark_returns: Dict[str, float],
        period: str = "2024-Q1",
    ) -> AttributionResult:
        """
        Brinson 归因分析

        Args:
            portfolio_weights: 组合各板块权重
            portfolio_returns: 组合各板块收益
            benchmark_weights: 基准各板块权重
            benchmark_returns: 基准各板块收益
            period: 时间段

        Returns:
            归因结果
        """
        all_sectors = set(list(portfolio_weights.keys()) + list(benchmark_weights.keys()))

        # 计算总收益
        total_return = sum(
            portfolio_weights.get(s, 0) * portfolio_returns.get(s, 0)
            for s in all_sectors
        )
        benchmark_return = sum(
            benchmark_weights.get(s, 0) * benchmark_returns.get(s, 0)
            for s in all_sectors
        )
        active_return = total_return - benchmark_return

        # Brinson 归因分解
        allocation_effect = 0
        selection_effect = 0
        interaction_effect = 0

        sector_allocation = {}
        security_selection = {}

        for sector in all_sectors:
            wp = portfolio_weights.get(sector, 0)
            wb = benchmark_weights.get(sector, 0)
            rp = portfolio_returns.get(sector, 0)
            rb = benchmark_returns.get(sector, 0)

            # 资产配置效应: (wp - wb) * rb
            alloc = (wp - wb) * rb
            allocation_effect += alloc
            sector_allocation[sector] = alloc

            # 个股选择效应: wb * (rp - rb)
            select = wb * (rp - rb)
            selection_effect += select
            security_selection[sector] = select

            # 交互效应: (wp - wb) * (rp - rb)
            interact = (wp - wb) * (rp - rb)
            interaction_effect += interact

        result = AttributionResult(
            period=period,
            total_return=total_return,
            benchmark_return=benchmark_return,
            active_return=active_return,
            allocation_effect=allocation_effect,
            selection_effect=selection_effect,
            interaction_effect=interaction_effect,
            sector_allocation=sector_allocation,
            security_selection=security_selection,
        )

        return result

    def multi_period_attribution(
        self,
        periods_data: List[Dict],
    ) -> List[AttributionResult]:
        """
        多期归因分析

        Args:
            periods_data: 每期数据列表

        Returns:
            多期归因结果
        """
        results = []

        for data in periods_data:
            result = self.brinson_attribution(
                portfolio_weights=data["portfolio_weights"],
                portfolio_returns=data["portfolio_returns"],
                benchmark_weights=data["benchmark_weights"],
                benchmark_returns=data["benchmark_returns"],
                period=data.get("period", "Unknown"),
            )
            results.append(result)

        return results

    def summarize_attribution(self, results: List[AttributionResult]) -> Dict:
        """
        总结归因分析结果

        Args:
            results: 多期归因结果

        Returns:
            总结报告
        """
        if not results:
            return {"error": "No attribution results"}

        avg_total = sum(r.total_return for r in results) / len(results)
        avg_benchmark = sum(r.benchmark_return for r in results) / len(results)
        avg_active = sum(r.active_return for r in results) / len(results)

        avg_allocation = sum(r.allocation_effect for r in results) / len(results)
        avg_selection = sum(r.selection_effect for r in results) / len(results)
        avg_interaction = sum(r.interaction_effect for r in results) / len(results)

        return {
            "periods": len(results),
            "avg_total_return": f"{avg_total:.2%}",
            "avg_benchmark_return": f"{avg_benchmark:.2%}",
            "avg_active_return": f"{avg_active:.2%}",
            "avg_allocation_effect": f"{avg_allocation:.2%}",
            "avg_selection_effect": f"{avg_selection:.2%}",
            "avg_interaction_effect": f"{avg_interaction:.2%}",
            "attribution_breakdown": {
                "allocation_pct": f"{avg_allocation / avg_active:.1%}" if avg_active != 0 else "N/A",
                "selection_pct": f"{avg_selection / avg_active:.1%}" if avg_active != 0 else "N/A",
                "interaction_pct": f"{avg_interaction / avg_active:.1%}" if avg_active != 0 else "N/A",
            },
        }
