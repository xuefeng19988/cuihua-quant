# 📋 翠花量化系统 - 开发路线图 (Roadmap)

> **项目**: Cuihua Quant System  
> **启动日期**: 2026-04-16  
> **当前版本**: v0.1.0  
> **状态**: ✅ 核心模块完成，进入实战验证阶段

---

## 🏗️ 已完成模块 (Phase 1) ✅

| 层级 | 模块 | 文件 | 状态 |
|------|------|------|------|
| **数据层** | Futu 数据同步 | `src/data/futu_sync.py` | ✅ |
| | AKShare 备用源 | `src/data/akshare_sync.py` | ✅ |
| | SQLite 数据库 | `src/data/database.py` | ✅ |
| **分析层** | 技术指标计算 | `src/analysis/technical.py` | ✅ |
| | 新闻情绪分析 | `src/analysis/sentiment.py` | ✅ |
| | 信号生成引擎 | `src/analysis/signal_gen.py` | ✅ |
| **策略层** | 策略基类 | `src/strategy/base.py` | ✅ |
| | SMA 交叉策略 | `src/strategy/sma_cross.py` | ✅ |
| | 多因子策略 | `src/strategy/multi_factor.py` | ✅ |
| | 动量策略 | `src/strategy/momentum.py` | ✅ |
| | 均值回归策略 | `src/strategy/mean_reversion.py` | ✅ |
| | 策略运行器 | `src/strategy/runner.py` | ✅ |
| **执行层** | 风控模块 | `src/execution/risk_control.py` | ✅ |
| | 仓位管理 | `src/execution/position_manager.py` | ✅ |
| | Futu 交易接口 | `src/execution/futu_trader.py` | ✅ |
| | 交易流水线 | `src/execution/pipeline.py` | ✅ |
| **回测层** | Backtrader 引擎 | `src/backtest/engine.py` | ✅ |
| **监控层** | 每日报告 | `src/monitor/reporter.py` | ✅ |
| | 绩效分析 | `src/monitor/performance.py` | ✅ |
| **工具** | CLI 命令行 | `cli.py` | ✅ |
| | 单元测试 | `tests/test_core.py` (15/15) | ✅ |

---

## 🎯 Phase 2: 实战验证（本周）

### 2.1 策略参数配置化
- [ ] 创建 `config/strategies.yaml`
- [ ] 将所有阈值、权重从代码抽离到配置文件
- [ ] 支持热加载配置（无需重启）

### 2.2 交易日志系统
- [ ] 创建 `src/data/trade_log.py`
- [ ] 记录信号生成历史
- [ ] 记录订单执行结果
- [ ] 记录盈亏明细

### 2.3 真实数据全流程验证
- [ ] 用 38 只股票完整跑一次 pipeline
- [ ] 验证信号生成合理性
- [ ] 验证风控模块生效
- [ ] 验证报告格式正确

### 2.4 盘中监控模块
- [ ] 创建 `src/monitor/intraday_monitor.py`
- [ ] 实时价格检查
- [ ] 止损/止盈预警推送
- [ ] 异动检测

---

## 🚀 Phase 3: 模拟盘运行（1-2 周）

### 3.1 模拟盘自动化
- [ ] 接入 Futu 模拟盘 (Paper Trading)
- [ ] 自动执行每日信号
- [ ] 记录模拟交易记录
- [ ] 模拟盘绩效报告

### 3.2 现有脚本整合
- [ ] 整合 `futu_realtime_predict.py`
- [ ] 整合 `prediction_accuracy_analysis.py`
- [ ] 统一数据格式
- [ ] 消除重复代码

### 3.3 情绪数据源扩展
- [ ] 接入 TrendRadar 新闻数据
- [ ] 情绪分析结果入库
- [ ] 情绪因子参与信号打分

### 3.4 绩效追踪面板
- [ ] 收益率曲线
- [ ] 回撤分析
- [ ] 胜率/赔率统计
- [ ] 策略对比分析

---

## 🔮 Phase 4: 进阶优化（1 月+）

### 4.1 ML 模型集成
- [ ] 接入 LightGBM 预测模型
- [ ] 预测结果作为策略因子
- [ ] 模型在线更新

### 4.2 多市场支持
- [ ] 港股交易逻辑完善
- [ ] 美股市场接入
- [ ] 汇率处理

### 4.3 自动调参
- [ ] 基于历史数据回测调参
- [ ] 参数优化算法
- [ ] 过拟合检测

### 4.4 Web 监控面板
- [ ] 实时持仓展示
- [ ] 信号推送
- [ ] 绩效可视化
- [ ] 策略配置界面

---

## 📊 技术指标目标

| 指标 | 目标值 | 当前状态 |
|------|--------|----------|
| 年化收益率 | >15% | 待验证 |
| 夏普比率 | >1.0 | 待验证 |
| 最大回撤 | <15% | 待验证 |
| 胜率 | >55% | 待验证 |
| 系统可用性 | 99.9% | ✅ |

---

## ⚙️ 配置清单

| 文件 | 说明 |
|------|------|
| `config/app.yaml` | 应用基础设置（DB、日志、集成） |
| `config/stocks.yaml` | 股票池定义 |
| `config/schedule.yaml` | 运行计划（Cron） |
| `config/strategies.yaml` | 策略参数（待创建） |
| `config/risk.yaml` | 风控参数（待创建） |
| `.env` | 环境变量（不提交 Git） |

---

## 📝 开发规范

### 代码规范
- Python 3.10+
- 使用 type hints
- 模块独立，低耦合
- 配置与代码分离

### 测试规范
- 核心逻辑必须有单元测试
- 新策略需附带测试用例
- 目标覆盖率 >80%

### Git 规范
- 功能分支开发，main 为主干
- Commit message 使用中文描述
- 大功能提交前更新此文档

---

*最后更新：2026-04-16*
