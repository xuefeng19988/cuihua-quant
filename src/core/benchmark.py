"""
Phase 80: 性能基准测试 (Performance Benchmarking)

系统性能监控与对比分析
"""

from __future__ import annotations

import time
import psutil
import os
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    name: str
    description: str
    execution_time: float
    memory_before: float
    memory_after: float
    memory_delta: float
    cpu_percent: float
    status: str = "success"
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "execution_time": f"{self.execution_time:.4f}s",
            "memory_before_mb": f"{self.memory_before:.2f}",
            "memory_after_mb": f"{self.memory_after:.2f}",
            "memory_delta_mb": f"{self.memory_delta:.2f}",
            "cpu_percent": f"{self.cpu_percent:.1f}%",
            "status": self.status,
        }


@dataclass
class BenchmarkSuite:
    """基准测试套件"""
    suite_name: str
    start_time: float
    end_time: float
    results: List[BenchmarkResult]
    total_time: float
    system_info: Dict

    def to_dict(self) -> Dict:
        return {
            "suite": self.suite_name,
            "start_time": datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.fromtimestamp(self.end_time).strftime("%Y-%m-%d %H:%M:%S"),
            "total_time": f"{self.total_time:.2f}s",
            "results": [r.to_dict() for r in self.results],
            "system_info": self.system_info,
        }


class PerformanceBenchmark:
    """性能基准测试工具"""

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.history: List[BenchmarkSuite] = []

    def benchmark_function(
        self,
        name: str,
        func: Callable,
        description: str = "",
        *args,
        **kwargs,
    ) -> BenchmarkResult:
        """
        基准测试函数

        Args:
            name: 测试名称
            func: 要测试的函数
            description: 描述
            *args, **kwargs: 函数参数

        Returns:
            基准测试结果
        """
        # 获取系统资源初始状态
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        cpu_before = process.cpu_percent()

        start_time = time.time()
        error = None

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            error = str(e)
            result = None

        execution_time = time.time() - start_time

        # 获取系统资源结束状态
        memory_after = process.memory_info().rss / (1024 * 1024)
        cpu_after = process.cpu_percent()

        benchmark_result = BenchmarkResult(
            name=name,
            description=description or name,
            execution_time=execution_time,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_delta=memory_after - memory_before,
            cpu_percent=cpu_after - cpu_before,
            status="failed" if error else "success",
            error=error,
            metadata={"result_type": type(result).__name__ if result else None},
        )

        self.results.append(benchmark_result)
        return benchmark_result

    def run_suite(self, suite_name: str, tests: List[Dict]) -> BenchmarkSuite:
        """
        运行测试套件

        Args:
            suite_name: 套件名称
            tests: 测试列表 [{"name": str, "func": Callable, "args": tuple, "kwargs": dict}]

        Returns:
            测试套件结果
        """
        suite_start = time.time()
        results = []

        for test in tests:
            name = test["name"]
            func = test["func"]
            args = test.get("args", ())
            kwargs = test.get("kwargs", {})
            description = test.get("description", "")

            result = self.benchmark_function(name, func, description, *args, **kwargs)
            results.append(result)

        suite_end = time.time()
        total_time = suite_end - suite_start

        # 获取系统信息
        system_info = self._get_system_info()

        suite = BenchmarkSuite(
            suite_name=suite_name,
            start_time=suite_start,
            end_time=suite_end,
            results=results,
            total_time=total_time,
            system_info=system_info,
        )

        self.history.append(suite)
        return suite

    def get_system_info(self) -> Dict:
        """获取当前系统信息"""
        return self._get_system_info()

    def _get_system_info(self) -> Dict:
        """内部系统信息获取"""
        process = psutil.Process(os.getpid())

        return {
            "python_version": os.sys.version,
            "os": os.name,
            "cpu_count": psutil.cpu_count(logical=True),
            "total_memory_gb": psutil.virtual_memory().total / (1024 ** 3),
            "available_memory_gb": psutil.virtual_memory().available / (1024 ** 3),
            "process_memory_mb": process.memory_info().rss / (1024 * 1024),
            "process_threads": process.num_threads(),
            "disk_usage_gb": psutil.disk_usage("/").total / (1024 ** 3),
        }

    def compare_results(self, suite1: BenchmarkSuite, suite2: BenchmarkSuite) -> Dict:
        """对比两个测试套件的结果"""
        comparison = {
            "suite1": suite1.suite_name,
            "suite2": suite2.suite_name,
            "total_time_diff": f"{suite2.total_time - suite1.total_time:+.2f}s",
            "results": [],
        }

        # 按名称匹配结果
        results1 = {r.name: r for r in suite1.results}
        results2 = {r.name: r for r in suite2.results}

        for name in set(results1.keys()) | set(results2.keys()):
            if name in results1 and name in results2:
                r1 = results1[name]
                r2 = results2[name]

                time_diff = r2.execution_time - r1.execution_time
                memory_diff = r2.memory_delta - r1.memory_delta

                comparison["results"].append({
                    "name": name,
                    "time_diff": f"{time_diff:+.4f}s",
                    "memory_diff": f"{memory_diff:+.2f}MB",
                    "faster": "suite2" if time_diff < 0 else "suite1",
                })

        return comparison

    def get_summary(self) -> Dict:
        """获取历史测试总结"""
        if not self.history:
            return {"error": "No benchmark history"}

        total_tests = sum(len(s.results) for s in self.history)
        success_tests = sum(
            1 for s in self.history for r in s.results if r.status == "success"
        )
        failed_tests = total_tests - success_tests

        avg_time = (
            sum(s.total_time for s in self.history) / len(self.history)
            if self.history
            else 0
        )

        return {
            "total_suites": len(self.history),
            "total_tests": total_tests,
            "success_count": success_tests,
            "failed_count": failed_tests,
            "success_rate": f"{success_tests / total_tests:.1%}" if total_tests > 0 else "0%",
            "avg_suite_time": f"{avg_time:.2f}s",
        }


# 预定义基准测试
def create_data_loading_benchmark(data_source) -> Dict:
    """数据加载基准测试"""
    return {
        "name": "数据加载测试",
        "func": data_source.fetch_data,
        "args": ("000001.SZ", "2023-01-01", "2023-12-31"),
        "description": "测试数据加载性能",
    }


def create_strategy_benchmark(strategy_class, data) -> Dict:
    """策略执行基准测试"""
    return {
        "name": "策略执行测试",
        "func": lambda: strategy_class().execute(data),
        "description": "测试策略执行性能",
    }
