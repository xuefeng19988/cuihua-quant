# 翠花量化系统 (Cuihua Quant System)

> **项目状态**: ✅ 核心模块开发完成
> **测试状态**: ✅ 15/15 测试通过

---

## 📁 项目结构

```
cuihua-quant/
├── main.py                     # 🚀 主入口 (CLI)
├── cli.py                      # 🔧 命令行工具
├── requirements.txt            # 📦 依赖清单
├── .env.example                # 🔐 环境变量模板
├── config/                     # ⚙️ 配置目录
│   ├── app.yaml                # App 设置
│   ├── stocks.yaml             # 股票池
│   ├── schedule.yaml           # 运行计划
│   └── strategies.yaml         # 策略参数
├── src/                        # 💻 源代码
│   ├── data/                   # 数据层
│   │   ├── futu_sync.py        # Futu 数据同步
│   │   └── akshare_sync.py     # AKShare 备用源
│   ├── analysis/               # 分析层
│   │   ├── technical.py        # 技术指标
│   │   ├── sentiment.py        # 情绪分析
│   │   └── signal_gen.py       # 信号生成
│   ├── strategy/               # 策略层
│   │   ├── base.py             # 策略基类
│   │   ├── sma_cross.py        # SMA 交叉策略
│   │   ├── multi_factor.py     # 多因子策略
│   │   ├── momentum.py         # 动量策略
│   │   └── mean_reversion.py   # 均值回归策略
│   ├── execution/              # 执行层
│   │   ├── risk_control.py     # 风控模块
│   │   ├── position_manager.py # 仓位管理
│   │   ├── futu_trader.py      # Futu 交易接口
│   │   └── pipeline.py         # 交易流水线
│   ├── backtest/               # 回测层
│   │   └── engine.py           # Backtrader 引擎
│   └── monitor/                # 监控层
│       ├── reporter.py         # 每日报告
│       └── performance.py      # 绩效分析
├── tests/                      # 🧪 单元测试
│   └── test_core.py            # 核心测试
└── data/                       # 📂 运行时数据
    ├── cuihua_quant.db         # SQLite 数据库
    └── logs/                   # 日志目录
```

---

## 🚀 快速开始

### 1. 安装依赖
```bash
cd cuihua-quant
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填写 Futu 端口和 Webhook
```

### 2. 运行 CLI
```bash
# 同步数据
python cli.py sync --pool watchlist --days 30

# 生成信号
python cli.py analyze --pool watchlist --top 5

# 回测策略
python cli.py backtest --pool csi300_top --capital 100000

# 运行流水线
python cli.py pipeline

# 查看状态
python cli.py status
```

### 3. 运行测试
```bash
python -m pytest tests/test_core.py -v
```

---

## 📊 核心模块

### 数据层 (Data Layer)
- **FutuSync**: 通过 Futu OpenD 获取实时行情和历史 K 线
- **AKShareSync**: 备用数据源，Futu 不可用时自动切换

### 分析层 (Analysis Layer)
- **Technical**: 计算 MA, RSI, MACD, Bollinger Bands
- **Sentiment**: 新闻情绪分析 (jieba 分词 + 关键词匹配)
- **SignalGenerator**: 融合技术面和情绪面信号

### 策略层 (Strategy Layer)
- **SmaCross**: 双均线交叉策略 (回测用)
- **MultiFactor**: 多因子策略 (动量 + 价值 + 技术 + 波动率)
- **Momentum**: 纯动量策略 (ROC + 成交量确认)
- **MeanReversion**: 均值回归策略 (RSI + 布林带)

### 执行层 (Execution Layer)
- **RiskManager**: 仓位控制、止损止盈、最大回撤保护
- **PositionManager**: 持仓管理、调仓逻辑
- **FutuTrader**: Futu 交易接口 (支持模拟盘)
- **TradingPipeline**: 端到端交易流水线

### 监控层 (Monitor Layer)
- **DailyReporter**: 生成每日报告并推送企业微信
- **PerformanceAnalyzer**: 计算夏普比率、最大回撤、胜率等

---

## ⚙️ 配置说明

### app.yaml
```yaml
app:
  name: "Cuihua Quant System"
  version: "0.1.0"
  
database:
  url: "sqlite:///data/cuihua_quant.db"
  
logging:
  level: "INFO"
  
integrations:
  wecom:
    enabled: true
    webhook_url_env: "WECOM_WEBHOOK"
```

### stocks.yaml
```yaml
pools:
  watchlist:
    name: "核心观察池"
    stocks:
      - "SH.600519"  # 贵州茅台
      - "SZ.002594"  # 比亚迪
      # ... 更多股票
```

---

## 📈 开发进度

| 模块 | 状态 | 测试 |
|------|------|------|
| 数据层 | ✅ 完成 | ✅ |
| 分析层 | ✅ 完成 | ✅ |
| 策略层 | ✅ 完成 | ✅ |
| 执行层 | ✅ 完成 | ✅ |
| 回测层 | ✅ 完成 | ✅ |
| 监控层 | ✅ 完成 | ✅ |
| CLI 工具 | ✅ 完成 | ✅ |
| 单元测试 | ✅ 15/15 | ✅ |

---

*最后更新：2026-04-16*
