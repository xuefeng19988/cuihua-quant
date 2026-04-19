"""
Phase 98: 策略参数自动调优 (Strategy Parameter Auto-Optimization)

贝叶斯优化策略参数
"""


from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import random


@dataclass
class ParameterSpace:
    """参数空间"""
    name: str
    param_type: str  # int/float/categorical
    low: Optional[float] = None
    high: Optional[float] = None
    choices: Optional[List] = None
    log_scale: bool = False


@dataclass
class OptimizationResult:
    """优化结果"""
    best_params: Dict
    best_score: float
    best_trial: int
    total_trials: int
    trial_history: List[Dict]
    convergence_data: List[float]

    def to_dict(self) -> Dict:
        return {
            "best_params": self.best_params,
            "best_score": f"{self.best_score:.4f}",
            "best_trial": self.best_trial,
            "total_trials": self.total_trials,
            "convergence": self.convergence_data[-10:],
        }


class BayesianOptimizer:
    """贝叶斯优化器"""

    def __init__(
        self,
        param_space: List[ParameterSpace],
        objective_func: Callable,
        n_trials: int = 50,
    ):
        self.param_space = param_space
        self.objective_func = objective_func
        self.n_trials = n_trials
        self.trial_history = []
        self.convergence = []

    def optimize(self) -> OptimizationResult:
        """
        运行贝叶斯优化

        Returns:
            优化结果
        """
        best_params = None
        best_score = float("-inf")
        best_trial = -1

        for trial in range(self.n_trials):
            # 采样参数
            if trial < 10:
                # 前 10 次随机探索
                params = self._random_sample()
            else:
                # 后续基于历史表现采样
                params = self._smart_sample()

            # 评估
            score = self.objective_func(params)

            # 记录
            self.trial_history.append({
                "trial": trial,
                "params": params,
                "score": score,
            })
            self.convergence.append(score)

            # 更新最优
            if score > best_score:
                best_score = score
                best_params = params
                best_trial = trial

        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            best_trial=best_trial,
            total_trials=self.n_trials,
            trial_history=self.trial_history,
            convergence_data=self.convergence,
        )

    def _random_sample(self) -> Dict:
        """随机采样"""
        params = {}

        for param in self.param_space:
            if param.param_type == "int":
                params[param.name] = random.randint(int(param.low), int(param.high))
            elif param.param_type == "float":
                params[param.name] = random.uniform(param.low, param.high)
            elif param.param_type == "categorical":
                params[param.name] = random.choice(param.choices)

        return params

    def _smart_sample(self) -> Dict:
        """智能采样（简化版贝叶斯）"""
        if not self.trial_history:
            return self._random_sample()

        # 取前 20% 最优试验
        sorted_trials = sorted(self.trial_history, key=lambda x: x["score"], reverse=True)
        top_trials = sorted_trials[:max(1, len(sorted_trials) // 5)]

        params = {}
        for param in self.param_space:
            if param.param_type == "categorical":
                # 从最优试验中选择
                values = [t["params"].get(param.name) for t in top_trials]
                params[param.name] = random.choice(values) if values else random.choice(param.choices)
            else:
                # 从最优试验中采样并添加扰动
                values = [t["params"].get(param.name) for t in top_trials if param.name in t["params"]]
                if values:
                    mean_val = sum(values) / len(values)
                    std_val = max((max(values) - min(values)) * 0.2, 0.1)
                    new_val = random.gauss(mean_val, std_val)

                    if param.low is not None:
                        new_val = max(new_val, param.low)
                    if param.high is not None:
                        new_val = min(new_val, param.high)

                    params[param.name] = new_val
                else:
                    params[param.name] = self._random_sample()[param.name]

        return params


class StrategyParameterOptimizer:
    """策略参数优化器"""

    def __init__(self):
        pass

    def optimize_strategy(
        self,
        strategy_name: str,
        param_space: List[ParameterSpace],
        backtest_func: Callable,
        n_trials: int = 50,
        metric: str = "sharpe_ratio",
    ) -> OptimizationResult:
        """
        优化策略参数

        Args:
            strategy_name: 策略名称
            param_space: 参数空间
            backtest_func: 回测函数
            n_trials: 试验次数
            metric: 优化指标

        Returns:
            优化结果
        """
        def objective(params):
            result = backtest_func(strategy_name, params)
            return result.get(metric, 0)

        optimizer = BayesianOptimizer(param_space, objective, n_trials)
        return optimizer.optimize()

    def walk_forward_optimization(
        self,
        strategy_name: str,
        param_space: List[ParameterSpace],
        backtest_func: Callable,
        train_period: int = 12,
        test_period: int = 3,
        n_trials: int = 30,
    ) -> Dict:
        """
        滚动窗口优化

        Args:
            strategy_name: 策略名称
            param_space: 参数空间
            backtest_func: 回测函数
            train_period: 训练期（月）
            test_period: 测试期（月）
            n_trials: 每次试验次数

        Returns:
            滚动优化结果
        """
        results = []

        # 简化：模拟 4 个滚动窗口
        for window in range(4):
            train_start = window * (train_period + test_period)
            train_end = train_start + train_period
            test_start = train_end
            test_end = test_start + test_period

            # 优化训练期参数
            def train_objective(params):
                result = backtest_func(strategy_name, params, period=f"{train_start}-{train_end}")
                return result.get("sharpe_ratio", 0)

            optimizer = BayesianOptimizer(param_space, train_objective, n_trials)
            opt_result = optimizer.optimize()

            # 在测试期验证
            test_result = backtest_func(
                strategy_name,
                opt_result.best_params,
                period=f"{test_start}-{test_end}",
            )

            results.append({
                "window": window,
                "train_period": f"{train_start}-{train_end}",
                "test_period": f"{test_start}-{test_end}",
                "best_params": opt_result.best_params,
                "train_score": opt_result.best_score,
                "test_score": test_result.get("sharpe_ratio", 0),
            })

        return {
            "windows": results,
            "avg_train_score": sum(r["train_score"] for r in results) / len(results),
            "avg_test_score": sum(r["test_score"] for r in results) / len(results),
        }

    def parameter_sensitivity(
        self,
        strategy_name: str,
        param_space: List[ParameterSpace],
        backtest_func: Callable,
        base_params: Dict,
    ) -> Dict:
        """
        参数敏感性分析

        Args:
            strategy_name: 策略名称
            param_space: 参数空间
            backtest_func: 回测函数
            base_params: 基准参数

        Returns:
            敏感性分析结果
        """
        sensitivity = {}

        for param in param_space:
            if param.param_type == "categorical":
                continue

            # 在参数范围内采样 10 个点
            scores = []
            for i in range(10):
                test_params = base_params.copy()

                if param.param_type == "int":
                    value = int(param.low + (param.high - param.low) * i / 9)
                else:
                    value = param.low + (param.high - param.low) * i / 9

                test_params[param.name] = value

                result = backtest_func(strategy_name, test_params)
                scores.append(result.get("sharpe_ratio", 0))

            sensitivity[param.name] = {
                "values": [base_params.get(param.name)],
                "scores": scores,
                "range": f"{param.low}-{param.high}",
                "sensitivity": max(scores) - min(scores),
            }

        return sensitivity
