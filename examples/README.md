# 翠花量化系统 - 快速开始示例

> 本目录包含完整示例项目，帮助你快速上手翠花量化系统。

---

## 📁 示例列表

### 1. 基础示例 (examples/01_basic/)

**目标**: 学习基本用法

```python
# 同步数据
python cli_v2.py sync --pool watchlist --days 30

# 生成信号
python cli_v2.py analyze --pool watchlist --top 5

# 查看状态
python cli_v2.py status
```

### 2. 回测示例 (examples/02_backtest/)

**目标**: 学习如何运行回测

```python
from src.backtest.backtest_runner import BacktestRunner
from src.strategy.sma_cross import SmaCross

runner = BacktestRunner()
df = runner.run_batch(
    codes=['SH.600519', 'SZ.002594'],
    strategy_cls=SmaCross,
    cash=100000,
    start_date='2025-01-01'
)
print(runner.generate_report(df))
```

### 3. 策略开发示例 (examples/03_strategy/)

**目标**: 学习如何开发自定义策略

```python
from src.strategy.base import BaseStrategy, Signal
import pandas as pd

class MyStrategy(BaseStrategy):
    """自定义策略示例"""
    
    def __init__(self, params=None):
        super().__init__("MyStrategy", params)
        
    def generate_signals(self, data: dict) -> list:
        signals = []
        for code, df in data.items():
            if df.empty:
                continue
            # 你的策略逻辑
            signal = Signal(
                code=code,
                direction='BUY',
                strength=0.5,
                reason="My strategy signal"
            )
            signals.append(signal)
        return signals
```

### 4. 模拟盘示例 (examples/04_paper_trading/)

**目标**: 学习如何运行模拟盘

```python
from src.execution.paper_trading_v2 import PaperTradingSimulator

sim = PaperTradingSimulator(initial_capital=1000000)
result = sim.run_daily()
print(sim.generate_report())
```

### 5. 完整项目模板 (examples/05_project_template/)

**目标**: 完整的项目结构参考

```
my_quant_project/
├── config/
│   ├── stocks.yaml      # 股票池配置
│   ├── strategies.yaml  # 策略参数
│   └── risk.yaml        # 风控参数
├── strategies/
│   └── my_strategy.py   # 自定义策略
├── data/
│   └── my_quant.db      # 数据库
├── main.py              # 主程序
└── requirements.txt     # 依赖
```

---

## 🚀 运行示例

```bash
# 1. 克隆仓库
git clone https://github.com/xuefeng19988/cuihua-quant.git
cd cuihua-quant

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行基础示例
python cli_v2.py status

# 4. 运行回测示例
python cli_v2.py backtest --pool watchlist

# 5. 运行模拟盘
python -m src.execution.paper_trading_v2
```

---

## 📚 更多资源

- [API 文档](docs/API.md)
- [部署指南](docs/DEPLOY.md)
- [性能优化](docs/PERFORMANCE.md)
- [贡献指南](CONTRIBUTING.md)

---

*祝使用愉快！有问题请提 Issue。*
