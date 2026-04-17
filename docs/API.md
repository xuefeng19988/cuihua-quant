# Cuihua Quant System API Documentation

> Version: v0.5.0  
> Last Updated: 2026-04-17

---

## 📚 Overview

Cuihua Quant System provides a modular, extensible quantitative trading platform with the following API layers:

1. **CLI API** - Command-line interface for all operations
2. **Python API** - Direct module imports for programmatic access
3. **Web API** - REST endpoints via Flask dashboard
4. **Data API** - Database access patterns

---

## 🔧 CLI API

```bash
# Base command
python cli_v2.py <command> [options]
```

### Commands

| Command | Description | Options |
|---------|-------------|---------|
| `sync` | Sync market data | `--pool`, `--days` |
| `analyze` | Generate trading signals | `--pool`, `--top` |
| `backtest` | Run backtest | `--pool`, `--capital`, `--start-date` |
| `pipeline` | Run full pipeline | `--execute`, `--ml` |
| `rebalance` | Portfolio rebalancing | `--pool`, `--capital`, `--method` |
| `report` | Generate report | `--date`, `--weekly` |
| `status` | System status | - |

### Examples

```bash
# Sync 30 days of data
python cli_v2.py sync --pool watchlist --days 30

# Analyze top 10 signals
python cli_v2.py analyze --pool watchlist --top 10

# Run backtest with 1M capital
python cli_v2.py backtest --pool csi300_top --capital 1000000

# Run full pipeline with ML
python cli_v2.py pipeline --ml

# Risk parity rebalancing
python cli_v2.py rebalance --method risk_parity

# Weekly performance report
python cli_v2.py report --weekly
```

---

## 🐍 Python API

### Data Layer

```python
from src.data.futu_sync import FutuSync
from src.data.akshare_sync import AKShareSync
from src.data.trade_logger import TradeLogger

# Sync data
syncer = FutuSync()
if syncer.connect():
    syncer.run(pool_name='watchlist', days_back=30)
    syncer.close()

# Trade logging
logger = TradeLogger()
logger.log_signal('SH.600519', 'multi_factor', 'BUY', score=0.7)
summary = logger.get_summary()
```

### Analysis Layer

```python
from src.analysis.signal_gen import SignalGenerator
from src.analysis.sentiment import StockSentimentAnalyzer
from src.analysis.feature_engineering import FeatureEngineer

# Generate signals
gen = SignalGenerator()
df = gen.generate_combined_signal(['SH.600519', 'SZ.002594'])

# Sentiment analysis
analyzer = StockSentimentAnalyzer()
result = analyzer.analyze_text("比亚迪今日大涨，突破新高")

# Feature engineering
fe = FeatureEngineer()
features = fe.extract_features('SH.600519')
```

### Strategy Layer

```python
from src.strategy.momentum import MomentumStrategy
from src.strategy.rebalancer import PortfolioRebalancer

# Momentum strategy
strategy = MomentumStrategy({'roc_period': 20})
signals = strategy.generate_signals(data)

# Portfolio rebalancing
rebalancer = PortfolioRebalancer()
weights = rebalancer.risk_parity(['SH.600519', 'SZ.002594'])
```

### Execution Layer

```python
from src.execution.risk_control import RiskManager
from src.execution.paper_trading import PaperTrader

# Risk management
risk = RiskManager()
order = risk.generate_order('SH.600519', 1500.0, 0.7)

# Paper trading
trader = PaperTrader(initial_capital=1000000)
result = trader.run_daily()
print(trader.get_pnl())
```

### Backtest Layer

```python
from src.backtest.backtest_runner import BacktestRunner
from src.strategy.sma_cross import SmaCross

runner = BacktestRunner()
df = runner.run_batch(['SH.600519'], SmaCross, cash=100000)
print(runner.generate_report(df))
```

### Monitor Layer

```python
from src.monitor.report_generator import PerformanceReporter
from src.monitor.risk_alert import RiskAlertMonitor

# Reports
reporter = PerformanceReporter()
print(reporter.daily_report())
print(reporter.weekly_report())

# Risk alerts
monitor = RiskAlertMonitor()
alerts = monitor.check_positions(current_prices)
```

---

## 🌐 Web API

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard HTML |
| `/api/status` | GET | System status JSON |

### Example

```bash
curl http://localhost:5000/api/status
```

```json
{
  "futu": "OK",
  "data_freshness": "38/38 stocks recent",
  "disk": "68% used"
}
```

---

## 💾 Data API

### Database Schema

```sql
CREATE TABLE stock_daily (
    code TEXT NOT NULL,          -- e.g., 'SH.600519', 'HK.00700', 'US.AAPL'
    date DATE NOT NULL,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume REAL,
    turnover REAL,
    change_pct REAL,
    pe_ratio REAL,
    turnover_rate REAL,
    updated_at DATETIME,
    PRIMARY KEY (code, date)
);
```

### Query Examples

```python
import pandas as pd
from src.data.database import get_db_engine

engine = get_db_engine()

# Get single stock history
df = pd.read_sql(
    "SELECT * FROM stock_daily WHERE code='SH.600519' ORDER BY date DESC LIMIT 30",
    engine
)

# Get latest prices for all stocks
df = pd.read_sql(
    "SELECT code, close_price, date FROM stock_daily s1 WHERE date = (SELECT MAX(date) FROM stock_daily s2 WHERE s1.code = s2.code)",
    engine
)
```

---

## ⚙️ Configuration

### Config Files

| File | Purpose |
|------|---------|
| `config/app.yaml` | Application settings |
| `config/stocks.yaml` | Stock pool definitions |
| `config/strategies.yaml` | Strategy parameters |
| `config/risk.yaml` | Risk management settings |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FUTU_HOST` | Futu OpenD host | `127.0.0.1` |
| `FUTU_PORT` | Futu OpenD port | `11112` |
| `WECOM_WEBHOOK` | WeCom webhook URL | - |
| `DB_PATH` | SQLite database path | `data/cuihua_quant.db` |
| `ALPHA_VANTAGE_KEY` | US stock API key | `demo` |

---

## 🔐 Security Notes

1. **Never commit `.env` file** - Contains API keys and secrets
2. **Use environment variables** for sensitive configuration
3. **Paper trading first** - Test thoroughly before real trading
4. **Rate limits** - Respect API rate limits (Alpha Vantage: 5/min free tier)

---

## 📝 Error Handling

All modules follow consistent error handling:

```python
try:
    result = some_operation()
except Exception as e:
    print(f"❌ Error: {e}")
    return {'status': 'ERROR', 'message': str(e)}
```

---

## 🚀 Deployment

### Docker

```bash
docker-compose up -d
```

### Manual

```bash
pip install -r requirements.txt
python cli_v2.py sync
python src/web/dashboard.py
```

---

*For more details, see [PLAN.md](PLAN.md) and [README.md](README.md)*
