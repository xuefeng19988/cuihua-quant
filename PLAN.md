# 📋 翠花量化系统 - 开发路线图 (Roadmap)

> **项目**: Cuihua Quant System  
> **启动日期**: 2026-04-16  
> **当前版本**: v0.2.0  
> **状态**: ✅ Phase 1-3 核心开发完成

---

## 🏗️ 已完成模块 ✅

### Phase 1: 核心框架
| 层级 | 模块 | 文件 | 状态 |
|------|------|------|------|
| **数据层** | Futu 同步 | `src/data/futu_sync.py` | ✅ |
| | AKShare 备用 | `src/data/akshare_sync.py` | ✅ |
| | SQLite 数据库 | `src/data/database.py` | ✅ |
| | 数据工具 | `src/data/data_utils.py` | ✅ |
| | 交易日志 | `src/data/trade_logger.py` | ✅ |
| **分析层** | 技术指标 | `src/analysis/technical.py` | ✅ |
| | 情绪分析 | `src/analysis/sentiment.py` | ✅ |
| | 信号生成 | `src/analysis/signal_gen.py` | ✅ |
| | 新闻情绪 | `src/analysis/news_sentiment.py` | ✅ |
| | ML 模型适配 | `src/analysis/ml_model.py` | ✅ |
| **策略层** | 策略基类 | `src/strategy/base.py` | ✅ |
| | SMA 交叉 | `src/strategy/sma_cross.py` | ✅ |
| | 多因子策略 | `src/strategy/multi_factor.py` | ✅ |
| | 动量策略 | `src/strategy/momentum.py` | ✅ |
| | 均值回归 | `src/strategy/mean_reversion.py` | ✅ |
| | 策略运行器 | `src/strategy/runner.py` | ✅ |
| | 组合再平衡 | `src/strategy/rebalancer.py` | ✅ |
| **执行层** | 风控模块 | `src/execution/risk_control.py` | ✅ |
| | 仓位管理 | `src/execution/position_manager.py` | ✅ |
| | Futu 交易 | `src/execution/futu_trader.py` | ✅ |
| | 交易流水线 | `src/execution/pipeline.py` | ✅ |
| | 流水线 v2 | `src/execution/pipeline_v2.py` | ✅ |
| **回测层** | Backtrader 引擎 | `src/backtest/engine.py` | ✅ |
| | 回测运行器 | `src/backtest/backtest_runner.py` | ✅ |
| **监控层** | 每日报告 | `src/monitor/reporter.py` | ✅ |
| | 绩效分析 | `src/monitor/performance.py` | ✅ |
| | 报告生成器 | `src/monitor/report_generator.py` | ✅ |
| | 盘中监控 | `src/monitor/intraday_monitor.py` | ✅ |
| **工具** | CLI | `cli.py` | ✅ |
| | CLI v2 | `cli_v2.py` | ✅ |
| | 单元测试 | `tests/test_core.py` | ✅ |

### Phase 2: 配置与日志
- [x] 策略参数配置化 (`config/strategies.yaml`)
- [x] 风控参数配置化 (`config/risk.yaml`)
- [x] 交易日志系统 (`trade_logger.py`)

### Phase 3: 集成与验证
- [x] 情绪数据源扩展 (`news_sentiment.py`)
- [x] ML 模型集成 (`ml_model.py`)
- [x] 流水线 v2 全流程 (`pipeline_v2.py`)
- [x] CLI v2 增强 (`cli_v2.py`)

---

## 📊 CLI v2 命令

```bash
# 同步数据
python cli_v2.py sync --pool watchlist --days 30

# 分析信号
python cli_v2.py analyze --pool watchlist --top 5

# 回测
python cli_v2.py backtest --pool csi300_top

# 运行完整流水线
python cli_v2.py pipeline --ml

# 组合再平衡
python cli_v2.py rebalance --method risk_parity

# 绩效报告
python cli_v2.py report --weekly

# 系统状态
python cli_v2.py status
```

---

## ⚙️ 配置文件

| 文件 | 说明 |
|------|------|
| `config/app.yaml` | 应用设置 (DB, 日志, 集成) |
| `config/stocks.yaml` | 股票池定义 |
| `config/schedule.yaml` | 运行计划 |
| `config/strategies.yaml` | 策略参数 |
| `config/risk.yaml` | 风控参数 |

---

## 🔮 未来规划

| 阶段 | 任务 | 优先级 |
|------|------|--------|
| Phase 4 | 绩效追踪面板 | ⭐⭐ |
| Phase 4 | 自动调参 | ⭐⭐ |
| Phase 4 | Web 监控面板 | ⭐ |
| Phase 4 | 多市场支持 (美股) | ⭐ |

---

*最后更新：2026-04-16*
