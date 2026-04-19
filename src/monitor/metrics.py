"""
Phase 11.2: System Metrics Collector
Collects and exports system metrics for Prometheus/Grafana.
"""

import os
import sys
import time
import psutil
from datetime import datetime
from typing import Dict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

class MetricsCollector:
    """
    Collects system and application metrics.
    Exports in Prometheus format for Grafana visualization.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics: Dict[str, float] = {}
        
    def collect_system_metrics(self) -> Dict:
        """Collect system-level metrics."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_gb': psutil.virtual_memory().used / 1e9,
            'memory_total_gb': psutil.virtual_memory().total / 1e9,
            'disk_percent': psutil.disk_usage('/').percent,
            'disk_used_gb': psutil.disk_usage('/').used / 1e9,
            'uptime_seconds': time.time() - self.start_time
        }
        
    def collect_process_metrics(self) -> Dict:
        """Collect process-level metrics."""
        process = psutil.Process()
        return {
            'process_cpu_percent': process.cpu_percent(interval=1),
            'process_memory_mb': process.memory_info().rss / 1e6,
            'process_threads': process.num_threads(),
            'process_fds': len(process.open_files())
        }
        
    def collect_app_metrics(self, portfolio_value: float = 0, 
                           positions_count: int = 0,
                           trades_today: int = 0) -> Dict:
        """Collect application-specific metrics."""
        return {
            'portfolio_value': portfolio_value,
            'positions_count': positions_count,
            'trades_today': trades_today,
            'signals_generated': 0,  # Would be updated from signal generator
            'api_calls_total': 0,    # Would be updated from API wrapper
            'cache_hit_rate': 0.0    # Would be updated from cache manager
        }
        
    def collect_all(self, portfolio_value: float = 0, 
                   positions_count: int = 0,
                   trades_today: int = 0) -> Dict:
        """Collect all metrics."""
        metrics = {}
        metrics.update(self.collect_system_metrics())
        metrics.update(self.collect_process_metrics())
        metrics.update(self.collect_app_metrics(portfolio_value, positions_count, trades_today))
        self.metrics = metrics
        return metrics
        
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        if not self.metrics:
            self.collect_all()
            
        lines = []
        for name, value in self.metrics.items():
            metric_name = f"cuihua_{name}"
            lines.append(f"# HELP {metric_name} {name.replace('_', ' ').title()}")
            lines.append(f"# TYPE {metric_name} gauge")
            lines.append(f"{metric_name} {value}")
            
        return "\n".join(lines)
        
    def generate_report(self) -> str:
        """Generate human-readable metrics report."""
        if not self.metrics:
            self.collect_all()
            
        lines = []
        lines.append("=" * 50)
        lines.append("📊 系统指标报告")
        lines.append("=" * 50)
        
        lines.append(f"\n🖥️  系统指标")
        lines.append(f"  CPU: {self.metrics.get('cpu_percent', 0):.1f}%")
        lines.append(f"  内存: {self.metrics.get('memory_percent', 0):.1f}% ({self.metrics.get('memory_used_gb', 0):.1f}GB / {self.metrics.get('memory_total_gb', 0):.1f}GB)")
        lines.append(f"  磁盘: {self.metrics.get('disk_percent', 0):.1f}% ({self.metrics.get('disk_used_gb', 0):.1f}GB used)")
        lines.append(f"  运行时间: {self.metrics.get('uptime_seconds', 0) / 3600:.1f} 小时")
        
        lines.append(f"\n⚙️  进程指标")
        lines.append(f"  CPU: {self.metrics.get('process_cpu_percent', 0):.1f}%")
        lines.append(f"  内存: {self.metrics.get('process_memory_mb', 0):.1f}MB")
        lines.append(f"  线程: {self.metrics.get('process_threads', 0)}")
        
        lines.append(f"\n📈 应用指标")
        lines.append(f"  投资组合: ¥{self.metrics.get('portfolio_value', 0):,.2f}")
        lines.append(f"  持仓数: {self.metrics.get('positions_count', 0)}")
        lines.append(f"  今日交易: {self.metrics.get('trades_today', 0)}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    collector = MetricsCollector()
    print(collector.generate_report())
