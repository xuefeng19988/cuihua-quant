"""
Phase 79: 自动化回测流水线 (Automated Backtesting Pipeline)

一键回测所有策略，自动生成对比报告
"""


import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class BacktestResult:
    """回测结果"""
    strategy_name: str
    start_date: str
    end_date: str
    total_return: float
    annual_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    execution_time: float
    status: str = "success"
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "strategy": self.strategy_name,
            "period": f"{self.start_date} ~ {self.end_date}",
            "total_return": f"{self.total_return:.2%}",
            "annual_return": f"{self.annual_return:.2%}",
            "volatility": f"{self.volatility:.2%}",
            "sharpe_ratio": f"{self.sharpe_ratio:.2f}",
            "max_drawdown": f"{self.max_drawdown:.2%}",
            "win_rate": f"{self.win_rate:.2%}",
            "profit_factor": f"{self.profit_factor:.2f}",
            "total_trades": self.total_trades,
            "execution_time": f"{self.execution_time:.2f}s",
            "status": self.status,
        }


@dataclass
class PipelineReport:
    """流水线报告"""
    pipeline_id: str
    start_time: float
    end_time: float
    total_strategies: int
    success_count: int
    failed_count: int
    results: List[BacktestResult]
    best_strategy: Optional[str] = None
    worst_strategy: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "pipeline_id": self.pipeline_id,
            "start_time": datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.fromtimestamp(self.end_time).strftime("%Y-%m-%d %H:%M:%S"),
            "duration": f"{self.end_time - self.start_time:.2f}s",
            "total_strategies": self.total_strategies,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "best_strategy": self.best_strategy,
            "worst_strategy": self.worst_strategy,
            "results": [r.to_dict() for r in self.results],
        }


class BacktestingPipeline:
    """自动化回测流水线"""

    def __init__(self, data_source=None, max_workers: int = 4):
        self.data_source = data_source
        self.max_workers = max_workers
        self.strategies = {}
        self.history: List[PipelineReport] = []

    def register_strategy(self, name: str, strategy_class, params: Dict = None):
        """注册策略"""
        self.strategies[name] = {
            "class": strategy_class,
            "params": params or {},
        }

    def run(
        self,
        start_date: str = "2023-01-01",
        end_date: str = "2024-12-31",
        initial_capital: float = 1_000_000,
        strategy_filter: List[str] = None,
        parallel: bool = True,
    ) -> PipelineReport:
        """
        运行回测流水线

        Args:
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
            strategy_filter: 策略过滤器（只运行指定策略）
            parallel: 是否并行执行

        Returns:
            流水线报告
        """
        pipeline_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = time.time()

        # 确定要运行的策略
        strategies_to_run = strategy_filter or list(self.strategies.keys())

        results = []
        success_count = 0
        failed_count = 0

        if parallel and len(strategies_to_run) > 1:
            # 并行执行
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(
                        self._run_single_strategy,
                        name,
                        self.strategies[name],
                        start_date,
                        end_date,
                        initial_capital,
                    ): name
                    for name in strategies_to_run
                    if name in self.strategies
                }

                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    if result.status == "success":
                        success_count += 1
                    else:
                        failed_count += 1
        else:
            # 串行执行
            for name in strategies_to_run:
                if name not in self.strategies:
                    continue
                result = self._run_single_strategy(
                    name, self.strategies[name], start_date, end_date, initial_capital
                )
                results.append(result)
                if result.status == "success":
                    success_count += 1
                else:
                    failed_count += 1

        end_time = time.time()

        # 找出最好和最差策略
        successful_results = [r for r in results if r.status == "success"]
        best_strategy = None
        worst_strategy = None

        if successful_results:
            best = max(successful_results, key=lambda x: x.sharpe_ratio)
            worst = min(successful_results, key=lambda x: x.sharpe_ratio)
            best_strategy = best.strategy_name
            worst_strategy = worst.strategy_name

        report = PipelineReport(
            pipeline_id=pipeline_id,
            start_time=start_time,
            end_time=end_time,
            total_strategies=len(strategies_to_run),
            success_count=success_count,
            failed_count=failed_count,
            results=results,
            best_strategy=best_strategy,
            worst_strategy=worst_strategy,
        )

        self.history.append(report)
        return report

    def _run_single_strategy(
        self,
        name: str,
        strategy_config: Dict,
        start_date: str,
        end_date: str,
        initial_capital: float,
    ) -> BacktestResult:
        """运行单个策略回测"""
        strategy_start = time.time()

        try:
            # 这里应该调用实际的回测引擎
            # 简化示例：返回模拟结果
            import random

            total_return = random.uniform(-0.2, 0.5)
            annual_return = total_return / 2
            volatility = random.uniform(0.1, 0.3)
            sharpe_ratio = annual_return / volatility if volatility > 0 else 0
            max_drawdown = random.uniform(-0.3, 0)
            win_rate = random.uniform(0.4, 0.6)
            profit_factor = random.uniform(0.8, 1.5)
            total_trades = random.randint(50, 200)

            execution_time = time.time() - strategy_start

            return BacktestResult(
                strategy_name=name,
                start_date=start_date,
                end_date=end_date,
                total_return=total_return,
                annual_return=annual_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                total_trades=total_trades,
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - strategy_start
            return BacktestResult(
                strategy_name=name,
                start_date=start_date,
                end_date=end_date,
                total_return=0,
                annual_return=0,
                volatility=0,
                sharpe_ratio=0,
                max_drawdown=0,
                win_rate=0,
                profit_factor=0,
                total_trades=0,
                execution_time=execution_time,
                status="failed",
                error_message=str(e),
            )

    def get_comparison(self, pipeline_report: PipelineReport) -> Dict:
        """生成策略对比报告"""
        results = [r for r in pipeline_report.results if r.status == "success"]

        if not results:
            return {"error": "No successful results"}

        # 按夏普比率排序
        sorted_by_sharpe = sorted(results, key=lambda x: x.sharpe_ratio, reverse=True)
        # 按收益率排序
        sorted_by_return = sorted(results, key=lambda x: x.total_return, reverse=True)
        # 按最大回撤排序
        sorted_by_drawdown = sorted(results, key=lambda x: x.max_drawdown, reverse=True)

        return {
            "by_sharpe": [r.to_dict() for r in sorted_by_sharpe],
            "by_return": [r.to_dict() for r in sorted_by_return],
            "by_drawdown": [r.to_dict() for r in sorted_by_drawdown],
        }
