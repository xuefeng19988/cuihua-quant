# 🦜 翠花量化系统 (Cuihua Quant System)

> **模块化、可扩展的量化交易平台**  
> **版本**: v3.0.0 | **状态**: ✅ Phase 1-100 全部完成 🎉

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Size](https://img.shields.io/github/languages/code-size/xuefeng19988/cuihua-quant)](https://github.com/xuefeng19988/cuihua-quant)
[![Stars](https://img.shields.io/github/stars/xuefeng19988/cuihua-quant?style=social)](https://github.com/xuefeng19988/cuihua-quant/stargazers)

---

## 📊 项目统计

| 指标 | 数据 |
|------|------|
| **总文件数** | 157+ |
| **代码行数** | ~35,000+ |
| **模块数** | 100+ 🎯 |
| **策略数** | 30+ |
| **因子数** | 25+ |
| **测试覆盖** | 45+ 测试用例 |
| **开发阶段** | Phase 1-100 (全部完成) |

---

## ✨ 核心特性

### 🔄 数据处理
- **双数据源**: Futu OpenD 实时行情 + AKShare 备用源
- **数据质量检查**: 完整性/一致性/时效性/异常值检测
- **多级缓存**: 内存缓存 + 文件缓存，智能 TTL 管理
- **统一数据访问层**: 内置缓存、重试、查询优化

### 📈 策略系统 (30+ 策略)
- **30+ 内置策略**: SMA 交叉、多因子、动量、均值回归、期权、新闻交易、配对交易、波动率交易、统计套利、行业轮动、季节性策略、突破策略等
- **AI 策略助手**: 基于市场状态的自动策略推荐
- **策略生命周期管理**: 研究→模拟→小资金→全仓→衰退→退役
- **策略参数自动调优**: 贝叶斯优化、滚动窗口优化、敏感性分析
- **交易日历优化**: 季节性效应识别与利用
- **组合保险策略**: CPPI/TIPP 保本策略
- **策略组合管理**: 动态权重分配、性能加权、风险调整
- **策略轮动引擎**: 基于夏普比率的自动策略选择
- **自定义策略框架**: 易于扩展的策略基类

### 🧠 分析与因子 (25+ 因子)
- **技术指标**: MA/RSI/MACD/布林带/ATR 等 20+ 指标
- **Alpha101 因子库**: WorldQuant 101 alpha 因子实现
- **25+ 高级因子**: 质量/价值/成长/情绪/微观结构/流动性/动量反转/波动率风险溢价
- **因子研究平台**: IC/ICIR 分析、分组收益、单调性检验
- **因子择时系统**: 动态因子权重调整，捕捉因子轮动
- **市场状态检测**: GMM 聚类识别牛/熊/震荡市
- **情绪分析**: 新闻情绪、社交媒体情绪映射
- **事件研究框架**: 财报/政策/黑天鹅事件影响分析
- **组合归因分析**: Brinson 模型（配置/选择/交互效应）
- **市场微观结构**: 订单流/价差/深度分析
- **交易行为分析**: 7 种行为偏差检测（处置效应/过度自信等）

### 🎯 交易执行
- **多层风控**: 止损/止盈/最大回撤/日亏损限制/紧急平仓
- **智能止损系统**: 6 种止损类型（固定/追踪/波动率/支撑阻力/时间/相关性）
- **高级风险管理**: VaR/CVaR 计算、压力测试、风险指标
- **智能仓位管理**: Kelly 公式、最优 f、风险平价、波动率目标、自适应仓位
- **组合再平衡引擎**: 偏离阈值检测、分批执行计划
- **交易成本优化**: 滑点/手续费优化、执行策略对比
- **多资产支持**: 股票/债券/加密货币/商品
- **智能订单路由**: 多经纪商最佳执行
- **市场冲击模型**: Almgren-Chriss 最优执行调度 (TWAP/VWAP)
- **交易成本分析**: 佣金/滑点/印花税综合成本分析
- **交易合规检查**: 10 种合规规则、实时检查、审计日志

### 📊 回测验证
- **多引擎回测**: Backtrader 引擎 + 事件驱动回测
- **自动化回测流水线**: 一键回测所有策略，并行执行，自动对比报告
- **Walk-Forward 分析**: 滚动训练测试，防止过拟合
- **蒙特卡洛模拟**: 收益/回撤分布模拟
- **综合绩效分析**: 夏普/索提诺/卡尔马/Alpha/Beta/信息比率
- **策略绩效归因**: 月度收益/滚动指标/相对基准分析

### 🤖 机器学习
- **ML 交易流水线**: 端到端 ML 流程
- **模型支持**: LightGBM、RandomForest、集成学习
- **特征工程**: 自动特征生成、选择、重要性分析
- **时间序列交叉验证**: 防止数据泄漏
- **贝叶斯优化**: 策略参数自动调优
- **遗传算法优化**: 策略参数自动优化
- **网格/随机搜索**: 多参数优化

### 🌐 Web 界面
- **8 功能页面**: 仪表板/股票池/分组/查询/筛选/图表/导出/报告
- **响应式设计**: 桌面/平板/手机自适应
- **暗色主题**: 专业交易界面风格
- **PWA 支持**: 离线缓存、添加到主屏幕
- **交互式图表**: Plotly K 线图/技术指标/散点图/雷达图/树图/热力图
- **实时数据推送**: WebSocket 实时更新

### 📤 数据导出
- **多格式导出**: CSV/Excel/PDF/HTML
- **报告生成**: 每日绩效/投资组合/股票分析 PDF 报告
- **图表导出**: PNG/PDF 格式

### 🔒 安全与用户
- **用户认证**: 注册/登录/Session 管理
- **操作审计**: 完整操作日志记录
- **权限管理**: 角色基础访问控制

### 🌍 国际化
- **中英文双语**: 完整中英文支持
- **多语言 CLI**: 一键切换语言

### ⚡ 性能优化
- **向量化计算**: NumPy/Pandas 向量化操作
- **异步处理**: 并发数据获取与信号生成
- **数据库索引**: 复合索引优化查询
- **代码优化**: 记忆化缓存、内存优化、并行处理
- **性能基准测试**: 函数级性能测试、内存/CPU 监控、测试套件对比

### 📋 系统管理
- **自动报告生成**: 日/周/月/季/年报自动生成，Markdown/HTML 导出
- **多账户管理**: 个人/机构/模拟/家族账户统一管理，跨账户分析
- **系统健康检查**: 5 大检查（资源/数据库/数据/策略/风险），自动故障诊断
- **策略健康度监控**: 实时策略状态监控，3 级健康评估
- **告警系统**: 多渠道告警（控制台/邮件/Webhook/自定义），冷却时间管理
- **市场情绪指标**: 6 维度情绪分析，5 级情绪分类

### 🔄 自动化
- **工作流引擎**: 依赖管理、自动重试、超时控制
- **定时任务**: 数据同步、信号生成、报告推送
- **策略轮动**: 自动选择最佳策略

---

## 📁 项目结构

```
cuihua-quant/
├── cli.py                      # CLI v1 入口
├── cli_v2.py                   # CLI v2 增强版
├── cli_i18n.py                 # 多语言 CLI
├── main.py                     # 主入口
├── setup.py                    # PyPI 打包配置
├── requirements.txt            # 依赖清单
├── Dockerfile                  # Docker 配置
├── docker-compose.yml          # Docker Compose
├── docker-compose.prod.yml     # 生产环境配置
│
├── config/                     # ⚙️ 配置目录
│   ├── app.yaml                # 应用设置
│   ├── stocks.yaml             # 股票池定义
│   ├── strategies.yaml         # 策略参数
│   ├── risk.yaml               # 风控参数
│   ├── schedule.yaml           # 运行计划
│   ├── logging.yaml            # 日志配置
│   └── notifications.yaml      # 通知模板
│
├── src/                        # 💻 源代码
│   ├── core/                   # 核心模块
│   │   ├── config.py           # 统一配置管理器
│   │   ├── exceptions.py       # 异常体系
│   │   ├── error_handler.py    # 错误处理与重试
│   │   ├── cache.py            # 查询缓存系统
│   │   ├── data_access.py      # 统一数据访问层
│   │   ├── di_container.py     # 依赖注入容器
│   │   ├── interfaces.py       # 核心接口定义
│   │   ├── types.py            # 类型定义
│   │   ├── logging_config.py   # 结构化日志
│   │   ├── auth.py             # 用户认证
│   │   ├── audit_logger.py     # 审计日志
│   │   ├── websocket_manager.py# WebSocket 管理
│   │   ├── workflow.py         # 工作流引擎
│   │   ├── optimizer.py        # 代码优化工具
│   │   └── enhanced_features.py# 增强功能
│   │
│   ├── data/                   # 数据层
│   │   ├── futu_sync.py        # Futu 数据同步
│   │   ├── akshare_sync.py     # AKShare 备用源
│   │   ├── database.py         # 数据库模型
│   │   ├── trade_logger.py     # 交易日志
│   │   ├── data_utils.py       # 数据工具
│   │   ├── data_export.py      # 数据导出
│   │   ├── stock_groups.py     # 股票分组管理
│   │   ├── quality_checker.py  # 数据质量检查
│   │   ├── us_stocks.py        # 美股数据
│   │   └── crypto.py           # 加密货币数据
│   │
│   ├── analysis/               # 分析层
│   │   ├── technical.py        # 技术指标计算
│   │   ├── sentiment.py        # 情绪分析
│   │   ├── signal_gen.py       # 信号生成引擎
│   │   ├── news_sentiment.py   # 新闻情绪集成
│   │   ├── ml_model.py         # ML 模型适配器
│   │   ├── ml_adapter.py       # ML 模型接口
│   │   ├── ml_trainer.py       # ML 训练器
│   │   ├── ml_trainer_v2.py    # ML 训练器 v2
│   │   ├── ml_pipeline.py      # ML 交易流水线
│   │   ├── feature_engineering.py # 特征工程
│   │   ├── alpha101.py         # Alpha101 因子库
│   │   ├── fama_french.py      # Fama-French 模型
│   │   ├── factor_analysis.py  # 因子分析面板
│   │   ├── factor_research.py  # 因子研究平台
│   │   ├── regime_detector.py  # 市场状态检测
│   │   ├── sector_heatmap.py   # 板块热力图
│   │   ├── extended_sentiment.py # 扩展情绪分析
│   │   ├── alternative_data.py # 另类数据
│   │   ├── new_factors.py      # 新 Alpha 因子
│   │   └── lstm_model.py       # LSTM 模型
│   │
│   ├── strategy/               # 策略层
│   │   ├── base.py             # 策略基类
│   │   ├── sma_cross.py        # SMA 交叉策略
│   │   ├── multi_factor.py     # 多因子策略
│   │   ├── momentum.py         # 动量策略
│   │   ├── mean_reversion.py   # 均值回归策略
│   │   ├── runner.py           # 策略运行器
│   │   ├── rebalancer.py       # 组合再平衡
│   │   ├── ensemble.py         # 集成学习策略
│   │   ├── options_strategy.py # 期权策略
│   │   ├── param_optimizer.py  # 参数优化器
│   │   ├── auto_tuner.py       # 自动调参
│   │   ├── optimizer.py        # 遗传算法优化
│   │   ├── news_trading.py     # 新闻交易策略
│   │   ├── new_strategies.py   # 新策略集合
│   │   └── ensemble_manager.py # 策略组合管理
│   │
│   ├── execution/              # 执行层
│   │   ├── risk_control.py     # 风控模块
│   │   ├── position_manager.py # 仓位管理
│   │   ├── futu_trader.py      # Futu 交易接口
│   │   ├── pipeline.py         # 交易流水线 v1
│   │   ├── pipeline_v2.py      # 交易流水线 v2
│   │   ├── pipeline_validator.py # 流水线验证器
│   │   ├── paper_trading.py    # 模拟盘 v1
│   │   ├── paper_trading_v2.py # 模拟盘 v2
│   │   ├── real_trading.py     # 实盘环境管理
│   │   ├── advanced_risk.py    # 高级风险管理
│   │   ├── multi_asset.py      # 多资产投资组合
│   │   ├── order_router.py     # 智能订单路由
│   │   └── portfolio_optimizer.py # 投资组合优化
│   │
│   ├── backtest/               # 回测层
│   │   ├── engine.py           # Backtrader 引擎
│   │   ├── backtest_runner.py  # 回测运行器
│   │   ├── advanced_backtest.py# 高级回测分析
│   │   └── event_driven.py     # 事件驱动回测
│   │
│   ├── monitor/                # 监控层
│   │   ├── reporter.py         # 每日报告
│   │   ├── performance.py      # 绩效分析
│   │   ├── report_generator.py # 报告生成器
│   │   ├── performance_dashboard.py # 绩效看板
│   │   ├── intraday_monitor.py # 盘中监控
│   │   ├── risk_alert.py       # 风险预警
│   │   ├── charts.py           # 交互式图表
│   │   ├── advanced_charts.py  # 高级图表生成器
│   │   ├── strategy_comparison.py # 策略对比
│   │   ├── metrics.py          # 系统指标
│   │   ├── notifications.py    # 通知系统
│   │   ├── pdf_report.py       # PDF 报告生成
│   │   ├── live_monitor.py     # 实盘监控
│   │   ├── performance_analyzer.py # 绩效分析器
│   │   └── advanced_viz.py     # 高级可视化
│   │
│   ├── web/                    # Web 界面
│   │   ├── dashboard.py        # Web 看板 v1
│   │   ├── dashboard_v2.py     # Web 看板 v2 (增强版)
│   │   ├── wsgi.py             # WSGI 入口
│   │   └── pwa.py              # PWA 支持
│   │
│   ├── system/                 # 系统集成
│   │   └── complete_system.py  # 完整交易系统
│   │
│   ├── plugins/                # 插件系统
│   │   ├── manager.py          # 插件管理器
│   │   └── __init__.py
│   │
│   └── modules/                # 高级模块
│       ├── phase54_58.py       # Phase 54-58 模块
│       └── phase59_62.py       # Phase 59-62 模块
│
├── tests/                      # 🧪 测试
│   ├── test_core.py            # 核心测试
│   ├── test_extended.py        # 扩展测试
│   ├── test_phase16_21.py      # Phase 16-21 测试
│   └── mock_data.py            # Mock 数据生成器
│
├── docs/                       # 📚 文档
│   ├── API.md                  # API 文档
│   ├── DEPLOY.md               # 部署指南
│   ├── PERFORMANCE.md          # 性能优化
│   └── README_EN.md            # 英文文档
│
├── examples/                   # 📖 示例
│   └── README.md               # 示例说明
│
├── monitoring/                 # 📊 监控配置
│   ├── prometheus.yml          # Prometheus 配置
│   └── grafana-dashboard.json  # Grafana 仪表板
│
├── data/                       # 💾 运行时数据
│   ├── cuihua_quant.db         # SQLite 数据库
│   ├── cache/                  # 缓存目录
│   ├── exports/                # 导出文件
│   ├── reports/                # 报告文件
│   ├── logs/                   # 日志目录
│   └── audit/                  # 审计日志
│
└── config/                     # (详见上方)
```

---

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Git

### 安装

```bash
# 克隆仓库
git clone https://github.com/xuefeng19988/cuihua-quant.git
cd cuihua-quant

# 安装依赖
pip install -r requirements.txt

# 可选：安装完整功能依赖
pip install -e ".[full]"

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写你的配置
```

### Docker 部署

```bash
# 开发环境
docker-compose up -d

# 生产环境 (高可用)
docker-compose -f docker-compose.prod.yml up -d
```

### 使用 CLI

```bash
# 同步数据
python cli_v2.py sync --pool watchlist --days 30

# 生成信号
python cli_v2.py analyze --pool watchlist --top 10

# 回测策略
python cli_v2.py backtest --pool csi300_top --capital 100000

# 运行完整流水线
python cli_v2.py pipeline --ml

# 组合再平衡
python cli_v2.py rebalance --method risk_parity

# 查看绩效报告
python cli_v2.py report --weekly

# 查看系统状态
python cli_v2.py status
```

### 启动 Web 看板

```bash
python src/web/dashboard_v2.py
# 访问 http://localhost:5000
```

---

## 📈 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Web 界面 (Flask + Plotly)                 │
│  仪表板 | 股票池 | 分组 | 查询 | 筛选 | 图表 | 导出 | 报告   │
├─────────────────────────────────────────────────────────────┤
│                    工作流引擎 + WebSocket                    │
├─────────────────────────────────────────────────────────────┤
│  数据层  │  Futu │ AKShare │ 缓存 │ 质量检查 │ 美股 │ 加密货币│
├─────────────────────────────────────────────────────────────┤
│  分析层  │  技术指标 │ 情绪 │ ML │ 因子 │ 市场状态 │ 另类数据 │
├─────────────────────────────────────────────────────────────┤
│  策略层  │  20+ 策略 │ 组合管理 │ 轮动引擎 │ 参数优化        │
├─────────────────────────────────────────────────────────────┤
│  执行层  │  风控 │ 仓位 │ 模拟盘 │ 实盘 │ 多资产 │ 路由      │
├─────────────────────────────────────────────────────────────┤
│  回测层  │  Backtrader │ 事件驱动 │ Walk-Forward │ 蒙特卡洛  │
├─────────────────────────────────────────────────────────────┤
│  监控层  │  绩效分析 │ 风险预警 │ 实盘监控 │ 审计日志        │
├─────────────────────────────────────────────────────────────┤
│  核心    │  配置 │ 异常处理 │ DI │ 接口 │ 类型 │ 日志        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 开发进度

### ✅ 已完成阶段

| 阶段 | 主题 | 状态 |
|------|------|------|
| Phase 1-7 | 核心架构 (数据/分析/策略/执行/回测/监控/生产化) | ✅ |
| Phase 8-11 | 实战运行到生产优化 (模拟盘/ML/CI/CD/监控) | ✅ |
| Phase 12-15 | 实盘准备到平台化 (实盘环境/期权/多因子/插件) | ✅ |
| Phase 16-21 | 代码质量到打包分发 (类型/DI/测试/安全/PyPI) | ✅ |
| Phase 23-25 | 可视化到国际化 (图表/社区/中英文) | ✅ |
| Phase 26-27 | 数据展示到用户体验 (Web 界面/导出/PDF) | ✅ |
| Phase 28-31 | 性能优化到高级可视化 (缓存/索引/PWA/认证) | ✅ |
| Phase 32 | 代码重构与优化 (配置/错误/WebSocket/DAL) | ✅ |
| Phase 33-34 | 高级回测 + 策略优化 (Walk-Forward/遗传算法) | ✅ |
| Phase 35-38 | 事件驱动 + 多资产 + 实盘 + 路由 | ✅ |
| Phase 39 | 新闻交易策略 | ✅ |
| Phase 40-43 | 高级风险 + 绩效 + 工作流 + 数据质量 | ✅ |
| Phase 44-45 | 因子研究平台 + 市场状态检测 | ✅ |
| Phase 46 | 策略组合管理器 | ✅ |
| Phase 47 | 投资组合优化引擎 | ✅ |
| Phase 48 | 完整交易系统整合 | ✅ |
| Phase 49-50 | 新策略 + 新因子 (配对/波动率/统计套利/Alpha 因子) | ✅ |
| Phase 51-52 | 代码优化 + 高级功能优化 | ✅ |
| Phase 53 | ML 交易流水线 | ✅ |
| Phase 54-58 | 实时数据 + 高级图表 + 风险平价 + 情绪 v2 + 回测报告 | ✅ |
| Phase 59-62 | 自适应仓位 + 市场冲击 + 交易成本 + 策略轮动 | ✅ |
| Phase 63-65 | 新策略 + 新因子 + 系统优化 | ✅ |
| Phase 66-67 | WebUI v3 + 数据库优化 | ✅ |
| Phase 68-70 | 实时推送 + 异步处理 + 智能缓存 | ✅ |
| Phase 71-73 | WebUI 优化 + 移动端 + 安全增强 | ✅ |
| Phase 74-76 | 最终系统优化 | ✅ |
| Phase 77-80 | 告警系统 + AI策略助手 + 自动化回测 + 性能基准测试 | ✅ |
| Phase 81-84 | 智能仓位 + 市场情绪 + 成本优化 + 策略健康监控 | ✅ |
| Phase 85-88 | 事件研究 + 组合归因 + 压力测试 + 策略生命周期 | ✅ |
| Phase 89-92 | 微观结构 + 因子择时 + 再平衡引擎 + 交易日历优化 | ✅ |
| Phase 93-96 | 智能止损 + 组合保险 + 行为分析 + 系统健康检查 | ✅ |
| Phase 97-100 | 自动报告 + 参数优化 + 多账户 + 合规检查 | ✅ |

**总计**: 100 个开发阶段全部完成 🎉🎉🎉

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [SUMMARY.md](SUMMARY.md) | 项目总结 |
| [PLAN.md](PLAN.md) | 开发路线图 |
| [FEATURES.md](FEATURES.md) | 功能清单 |
| [docs/API.md](docs/API.md) | API 文档 |
| [docs/DEPLOY.md](docs/DEPLOY.md) | 部署指南 |
| [docs/PERFORMANCE.md](docs/PERFORMANCE.md) | 性能优化 |
| [docs/README_EN.md](docs/README_EN.md) | English Documentation |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |
| [examples/README.md](examples/README.md) | 示例项目 |

---

## 🤝 贡献

欢迎贡献代码、报告问题、提出建议！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

详见 [贡献指南](CONTRIBUTING.md)

---

## 📄 许可证

本项目基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。

---

## 📞 联系方式

- **GitHub Issues**: <https://github.com/xuefeng19988/cuihua-quant/issues>
- **项目作者**: Snow
- **项目启动**: 2026-04-16

---

## ⭐ 支持项目

如果这个项目对你有帮助，请给它一个 Star ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=xuefeng19988/cuihua-quant&type=Date)](https://star-history.com/#xuefeng19988/cuihua-quant&Date)

---

*最后更新：2026-04-17*  
*版本：v3.0.0*
