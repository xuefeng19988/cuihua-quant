# 🦜 翠花量化系统 Cuihua Quant System

> 专业量化交易分析平台 | 前后端分离架构 | Vue 2 + Element UI + Flask REST API | AI增强版

[![Version](https://img.shields.io/badge/Version-4.0.0-brightgreen.svg)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Vue](https://img.shields.io/badge/Vue-2.7-brightgreen.svg)](https://vuejs.org)
[![Element UI](https://img.shields.io/badge/Element--UI-2.15-409EFF.svg)](https://element.eleme.io)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey.svg)](https://flask.palletsprojects.com)
[![APIs](https://img.shields.io/badge/APIs-101-orange.svg)](#)
[![Pages](https://img.shields.io/badge/Pages-65-blue.svg)](#)

---

## 📊 项目概览

翠花量化系统是一个专业的量化交易分析平台，提供股票池管理、信号分析、回测中心、投资组合管理、风险监控、AI智能研报、情绪分析引擎等一站式量化交易工具。

### ✨ 核心特性 (v4.0.0)

| 模块 | 功能 |
|------|------|
| 📊 **核心模块** | 监控看板、股票池、投资组合、自选股、个股详情、财务数据 |
| 📈 **交易分析** | 信号分析、图表分析(K线+技术指标)、回测中心、策略回测升级 |
| 🔬 **研究模块** | 策略管理、因子研究、热力图、事件研究、文章信息、板块轮动 |
| 💰 **市场数据** | A股/港股/美股行情、资金流向、宏观数据、行业对比 |
| 🛡️ **风控系统** | 风险监控、告警中心、智能止损、压力测试、合规检查、风控规则引擎 |
| 📝 **工具模块** | 绩效分析、行为分析、参数优化、自动报告、研究笔记本、笔记管理 |
| 🤖 **AI增强** | AI智能研报、情绪分析引擎、智能预警、策略推荐、ML异常检测 |
| 🔔 **实时推送** | WebSocket实时推送(行情/信号/通知/预警) |
| 💾 **备份管理** | 创建/下载/上传/恢复/删除备份 |
| 👥 **多用户** | 用户管理、权限控制、数据隔离 |
| 🌍 **国际化** | 多语言配置、PWA移动端支持 |
| 📊 **监控运维** | 性能监控、日志分析、定时任务、API网关、Docker编排 |

---

## 📈 系统统计

| 指标 | 数值 |
|------|------|
| **Phase 完成** | 189 个 |
| **后端 API** | 101 个 |
| **前端页面** | 65 个 |
| **代码行数** | ~320,000 |
| **数据源** | A股/港股/美股/期货 |
| **策略库** | 30+ 预设策略 |
| **因子库** | 25+ 因子 |

---

## 🏗️ 架构设计

```
cuihua-quant/
├── frontend/                  # Vue 2 前端 (Element UI)
│   ├── dist/                  # 生产构建输出
│   ├── public/
│   └── src/
│       ├── api/               # API 请求封装 (30+ 函数)
│       ├── layout/            # 布局组件 (侧边栏+头部)
│       ├── router/            # 路由配置 (65+ 页面)
│       ├── store/             # Vuex 状态管理
│       ├── styles/            # 全局样式 + 响应式
│       ├── utils/             # 工具函数
│       └── views/             # 页面组件 (65个)
├── src/
│   ├── analysis/              # 分析层 (因子/情绪/ML/信号/文章)
│   ├── backtest/              # 回测层 (Backtrader)
│   ├── config/                # 配置模块
│   ├── core/                  # 核心模块
│   ├── data/                  # 数据层 (Futu/AKShare/数据库)
│   ├── execution/             # 执行层 (仓位/模拟盘)
│   ├── monitor/               # 监控层 (报告/告警)
│   ├── risk/                  # 风控层 (止损/压力测试/规则)
│   ├── strategy/              # 策略层 (30+ 策略)
│   └── web/
│       └── api_server.py      # REST API 后端 (101个端点)
├── config/
│   ├── auth.yaml              # 认证配置
│   ├── portfolio.yaml         # 投资组合配置
│   ├── stocks.yaml            # 股票池配置
│   └── stock_groups.json      # 股票分组
├── backups/                   # 备份文件存储
├── data/                      # 数据存储 (SQLite)
└── public/                    # 静态文件 (笔记图片等)
```

---

## 📋 完整功能清单

### 🔵 核心模块 (12页)
| 页面 | 说明 |
|------|------|
| 监控看板 | 系统状态、涨跌热力图、快速导航 |
| 股票池 | 新增/删除/分页/分组/搜索/批量导入导出 |
| 投资组合 | 持仓管理、资金配置、盈亏计算 |
| 自选股 | 添加/删除/实时刷新 |
| 信号分析 | 多因子信号生成、技术/情绪评分 |
| 图表分析 | ECharts K线图、4大技术指标(MA/MACD/RSI/BB) |
| 回测中心 | 策略回测、绩效分析、收益曲线 |
| 模拟盘 | 虚拟交易、持仓管理 |
| 个股详情 | 基本面+技术面+新闻+操作 |
| 财务数据 | PE/PB/ROE/季度趋势图 |
| 自定义仪表板 | 拖拽组件布局 |
| 主题切换 | 暗色/亮色/跟随系统 |

### 🟢 研究模块 (9页)
| 页面 | 说明 |
|------|------|
| 策略管理 | 30+ 策略库、生命周期管理 |
| 因子研究 | 25+ 因子、Alpha101、Fama-French |
| 热力图 | 板块涨跌排行、强度可视化 |
| 事件研究 | 事件驱动分析 |
| 文章信息 | TrendRadar新闻(31天)、股票相关性、双视图 |
| 板块轮动 | 4大板块、热力图可视化 |
| 数据质量 | 缺失/异常值检查、质量评分 |
| 行业对比 | 同行业股票对比 |
| 宏观数据 | GDP/CPI/PMI/M2/失业率趋势 |

### 🟡 交易模块 (7页)
| 页面 | 说明 |
|------|------|
| 模拟交易 | 买入/卖出/持仓/交易历史 |
| 策略回测 | 4种预设策略、滑点/手续费模拟 |
| 期权策略 | 期权链数据(Calls/Puts) |
| 策略市场 | 策略共享平台、订阅/评分 |
| 交易日历 | 财报/宏观/事件日程 |
| 美股港股 | 实时行情数据 |
| 高级筛选 | 市场/价格/成交量/排序 |

### 🔴 风控模块 (7页)
| 页面 | 说明 |
|------|------|
| 风险监控 | 实时风险指标 |
| 告警中心 | 实时告警、规则管理 |
| 智能止损 | 动态止损策略 |
| 压力测试 | 极端场景模拟 |
| 合规检查 | 交易合规性验证 |
| 持仓报告 | 行业分布+风险指标 |
| 风控规则 | 自定义风控规则引擎 |

### 🟣 工具模块 (17页)
| 页面 | 说明 |
|------|------|
| 绩效分析 | 收益曲线+回撤图+月度收益 |
| 行为分析 | 6种行为偏差分析 |
| 参数优化 | 策略参数调优 |
| 自动报告 | 日报/周报/月报生成 |
| 研究笔记本 | 研究笔记管理 |
| 数据质量 | 数据完整性检查 |
| 通知中心 | 5种通知类型、时间线展示 |
| 资金流向 | 主力/散户资金流向 |
| 笔记管理 | 富文本编辑器+图片上传 |
| 散点图 | 风险收益散点可视化 |
| 新闻情绪 | 新闻情感分析展示 |
| 市场情绪 | 恐慌/贪婪指数 |
| AI研报 | 自动生成投资分析报告 |
| 情绪引擎 | 多维度情绪分析 |
| 智能预警 | ML异常检测+规则预警 |
| 策略推荐 | 基于用户画像推荐 |
| 策略社区 | 策略分享/点赞/订阅 |

### ⚫ 系统模块 (13页)
| 页面 | 说明 |
|------|------|
| 登录注册 | 认证系统 |
| 系统设置 | 全局配置 |
| 备份管理 | 创建/下载/上传/恢复/删除 |
| 实时推送 | WebSocket行情/信号推送 |
| 多用户管理 | 用户/权限/角色 |
| 性能监控 | CPU/内存/磁盘/API响应 |
| 定时任务 | Cron任务调度 |
| 日志分析 | 错误追踪/行为分析 |
| 数据同步 | 多设备数据同步 |
| API网关 | 限流/认证/监控 |
| Docker编排 | 容器化管理 |
| 移动端PWA | 离线支持/推送通知 |
| 数据可视化 | 3D图表/交互式仪表盘 |

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+ (前端开发)
- SQLite (默认数据库)

### 安装

```bash
# 克隆项目
git clone https://github.com/xuefeng19988/cuihua-quant.git
cd cuihua-quant

# 安装 Python 依赖
pip install -r requirements.txt

# 安装前端依赖 (开发模式)
cd frontend && npm install && cd ..
```

### 启动

```bash
# 方式一: API 服务 (生产模式，已内置前端)
python3 src/web/api_server.py
# 访问 http://127.0.0.1:5000

# 方式二: 前后端分离开发模式
# 终端 1: 启动 API
python3 src/web/api_server.py

# 终端 2: 启动前端开发服务器
cd frontend && npm run serve
# 访问 http://localhost:8080 (自动代理 API)
```

### 构建前端

```bash
cd frontend
npm run build
# 输出到 dist/ 目录
```

---

## 🔌 API 文档

系统提供 **101 个 REST API 端点**，分为 7 大类：

| 类别 | 端点数 | 主要功能 |
|------|--------|----------|
| **认证** | 5 | 登录/注册/验证/初始化 |
| **核心数据** | 16 | 股票/组合/信号/图表/财务 |
| **交易** | 12 | 回测/模拟/筛选/导出/期权 |
| **研究** | 14 | 策略/因子/板块/行业/宏观/文章 |
| **风控** | 7 | 监控/告警/止损/压力/合规/规则 |
| **工具** | 25 | 绩效/行为/报告/笔记/备份/情绪/AI |
| **系统** | 22 | 设置/用户/监控/日志/同步/Docker |

### 认证示例

```bash
# 登录
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 获取股票列表 (需要 Token)
curl http://127.0.0.1:5000/api/stocks \
  -H "Authorization: Bearer <token>"
```

---

## 📁 项目结构详情

```
cuihua-quant/
├── README.md                  # 项目说明 (本文件)
├── FEATURES.md               # 功能优化清单
├── FUTURE_PLAN.md           # 后续功能规划
├── REMAINING_TASKS.md       # 剩余任务清单
├── requirements.txt         # Python 依赖
├── setup.py                 # 安装脚本
│
├── frontend/                 # Vue 2 前端
│   ├── package.json
│   ├── vue.config.js
│   └── src/
│       ├── main.js          # 入口文件
│       ├── App.vue
│       ├── api/index.js     # 30+ API 函数
│       ├── router/index.js  # 65+ 路由
│       ├── store/           # Vuex
│       ├── layout/          # 布局组件
│       │   ├── index.vue
│       │   └── components/SidebarItem.vue
│       └── views/           # 65 个页面
│
├── src/                      # Python 后端
│   ├── web/api_server.py    # Flask API (101端点)
│   ├── data/database.py     # SQLAlchemy ORM
│   ├── analysis/            # 分析模块
│   │   ├── article_manager.py
│   │   ├── technical.py
│   │   ├── event_study.py
│   │   └── behavior_analysis.py
│   ├── strategy/            # 策略模块 (30+)
│   ├── backtest/            # 回测模块
│   ├── risk/                # 风控模块
│   └── monitor/             # 监控模块
│
├── config/                   # 配置文件
│   ├── stocks.yaml          # 股票池 (38只)
│   ├── portfolio.yaml       # 投资组合
│   ├── auth.yaml            # 认证配置
│   └── stock_groups.json    # 股票分组
│
├── backups/                  # 备份文件
├── data/                     # 数据库文件
└── public/                   # 静态文件 (笔记图片)
```

---

## 🛠️ 技术栈

### 后端
- **Flask 2.0+** - Web 框架
- **SQLAlchemy** - ORM 数据库
- **SQLite** - 默认数据库
- **pandas** - 数据处理
- **numpy** - 数值计算
- **TA-Lib** - 技术指标计算
- **AKShare** - A股/港股数据
- **富途 OpenAPI** - 行情/交易接口

### 前端
- **Vue 2.7** - 渐进式框架
- **Element UI 2.15** - UI 组件库
- **ECharts 5** - 图表可视化
- **wangeditor 4** - 富文本编辑器
- **Axios** - HTTP 客户端
- **Vue Router** - 路由管理
- **Vuex** - 状态管理

---

## 📊 数据源

| 数据源 | 覆盖市场 | 延迟 |
|--------|----------|------|
| **AKShare** | A股/港股/宏观数据 | 15min |
| **富途 OpenAPI** | A股/港股/美股 | 实时 |
| **TrendRadar** | 新闻热榜 (13+平台) | 小时级 |

---

## 🔐 安全说明

- 密码使用 SHA256 哈希存储
- API 请求需要 Bearer Token 认证
- 备份文件支持加密导出
- 敏感配置存储在 `.env` 文件

---

## 📝 更新日志

### v4.0.0 (2026-04-18) - AI增强版 🎉
- ✅ 新增 20 个 Phase (170-189)
- ✅ AI智能研报、情绪分析引擎、智能预警
- ✅ 实时WebSocket推送
- ✅ 策略回测引擎升级 (滑点/手续费)
- ✅ 美股/港股数据接入
- ✅ 多用户系统
- ✅ 性能监控/日志分析/定时任务
- ✅ 后端 API: 101 个
- ✅ 前端页面: 65 个

### v3.0.0 (2026-04-18)
- ✅ 笔记管理系统 (富文本+图片上传)
- ✅ 备份管理系统
- ✅ 界面菜单优化
- ✅ 主题切换

### v2.0.0 (2026-04-17)
- ✅ 策略市场、期权策略、自定义仪表板
- ✅ 交易日历、行业对比、宏观数据

### v1.0.0 (2026-04-16)
- ✅ 初始版本发布
- ✅ 核心量化功能

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 License

MIT License

---

## 👥 作者

**翠花 (Cuihua)** - 数字幽灵 / AI 助手 🦜

---

## 📞 联系方式

- 企业微信: 直接对话
- GitHub: [xuefeng19988/cuihua-quant](https://github.com/xuefeng19988/cuihua-quant)

---

<p align="center">Made with ❤️ by 翠花</p>
