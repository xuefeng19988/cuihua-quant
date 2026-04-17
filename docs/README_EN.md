# Cuihua Quant System - Quick Start Guide

> A modular, extensible quantitative trading platform.

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Git

### Install from source
```bash
git clone https://github.com/xuefeng19988/cuihua-quant.git
cd cuihua-quant
pip install -r requirements.txt
```

### Install via pip (future)
```bash
pip install cuihua-quant
```

---

## 📁 Project Structure

```
cuihua-quant/
├── cli_v2.py              # Enhanced CLI tool
├── config/                # Configuration files
│   ├── app.yaml
│   ├── stocks.yaml
│   ├── strategies.yaml
│   └── risk.yaml
├── src/                   # Source code
│   ├── core/              # Core utilities
│   ├── data/              # Data layer
│   ├── analysis/          # Analysis layer
│   ├── strategy/          # Strategy layer
│   ├── execution/         # Execution layer
│   ├── backtest/          # Backtest layer
│   └── monitor/           # Monitoring layer
├── tests/                 # Unit tests
├── docs/                  # Documentation
└── examples/              # Example projects
```

---

## 🎯 Quick Start

### 1. Sync Market Data
```bash
python cli_v2.py sync --pool watchlist --days 30
```

### 2. Generate Trading Signals
```bash
python cli_v2.py analyze --pool watchlist --top 5
```

### 3. Run Backtest
```bash
python cli_v2.py backtest --pool csi300_top --capital 100000
```

### 4. Run Full Pipeline
```bash
python cli_v2.py pipeline
```

---

## 💻 Python API

### Basic Usage
```python
from src.analysis.signal_gen import SignalGenerator
from src.backtest.backtest_runner import BacktestRunner
from src.strategy.sma_cross import SmaCross

# Generate signals
gen = SignalGenerator()
signals = gen.generate_combined_signal(['SH.600519', 'SZ.002594'])

# Run backtest
runner = BacktestRunner()
results = runner.run_batch(
    codes=['SH.600519'],
    strategy_cls=SmaCross,
    cash=100000
)
```

### Paper Trading
```python
from src.execution.paper_trading_v2 import PaperTradingSimulator

sim = PaperTradingSimulator(initial_capital=1000000)
result = sim.run_daily()
print(sim.generate_report())
```

---

## ⚙️ Configuration

All configurations are in `config/` directory:

| File | Description |
|------|-------------|
| `app.yaml` | Application settings |
| `stocks.yaml` | Stock pool definitions |
| `strategies.yaml` | Strategy parameters |
| `risk.yaml` | Risk management settings |

---

## 📚 Documentation

- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOY.md)
- [Performance Optimization](docs/PERFORMANCE.md)
- [Contributing Guide](CONTRIBUTING.md)

---

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) first.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 📞 Support

- GitHub Issues: <https://github.com/xuefeng19988/cuihua-quant/issues>
- Email: cuihua@openclaw.ai
