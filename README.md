# 🦜 翠花量化系统 Cuihua Quant System

> 专业量化交易分析平台 | 前后端分离架构 | Vue 2 + Element UI + Flask REST API

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Vue](https://img.shields.io/badge/Vue-2.7-brightgreen.svg)](https://vuejs.org)
[![Element UI](https://img.shields.io/badge/Element--UI-2.15-409EFF.svg)](https://element.eleme.io)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey.svg)](https://flask.palletsprojects.com)

---

## 📊 项目概览

翠花量化系统是一个专业的量化交易分析平台，提供股票池管理、信号分析、回测中心、投资组合管理、风险监控等一站式量化交易工具。

### ✨ 核心特性

| 模块 | 功能 |
|------|------|
| 📊 监控看板 | 系统状态、涨跌热力图、快速导航 |
| 💼 股票池 | 新增/删除/分页/实时价格刷新 |
| 🌍 投资组合 | 持仓管理、资金配置、盈亏计算 |
| 📈 信号分析 | 多因子信号生成、技术/情绪评分 |
| 📉 图表分析 | ECharts K线图、技术指标 |
| 🔬 回测中心 | 策略回测、绩效分析、收益曲线 |
| 🔥 热力图 | 板块涨跌排行、强度可视化 |
| 🎯 策略管理 | 30+ 策略库、生命周期管理 |
| 🧮 因子研究 | 25+ 因子、Alpha101、Fama-French |
| 🛡️ 风控系统 | 风险监控、智能止损、压力测试、合规检查 |
| 🔔 告警中心 | 实时告警、规则管理 |
| 📰 文章信息 | TrendRadar 新闻、股票相关性匹配 |

---

## 🏗️ 架构设计

```
cuihua-quant/
├── frontend/                  # Vue 2 前端 (Element UI)
│   ├── dist/                  # 生产构建输出
│   ├── public/
│   └── src/
│       ├── api/               # API 请求封装
│       ├── layout/            # 布局组件 (侧边栏+头部)
│       ├── router/            # 路由配置 (25+ 页面)
│       ├── store/             # Vuex 状态管理
│       ├── styles/            # 全局样式
│       ├── utils/             # 工具函数
│       └── views/             # 页面组件
├── src/
│   ├── analysis/              # 分析层 (因子/情绪/ML/信号)
│   ├── backtest/              # 回测层 (Backtrader)
│   ├── config/                # 配置模块
│   ├── core/                  # 核心模块
│   ├── data/                  # 数据层 (Futu/AKShare)
│   ├── execution/             # 执行层 (仓位/模拟盘)
│   ├── monitor/               # 监控层 (报告/告警)
│   ├── risk/                  # 风控层 (止损/压力测试)
│   ├── strategy/              # 策略层 (30+ 策略)
│   └── web/
│       └── api_server.py      # REST API 后端
├── config/
│   ├── auth.yaml              # 认证配置
│   ├── portfolio.yaml         # 投资组合配置
│   └── stocks.yaml            # 股票池配置
└── data/                      # 数据存储

```

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
cd frontend && npm run dev
# 访问 http://localhost:9528
```

### 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |

⚠️ **首次登录后请修改默认密码！**

---

## 📋 API 文档

### 认证

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/login` | POST | 登录获取 Token |
| `/api/auth/info` | GET | 获取用户信息 |
| `/api/auth/logout` | POST | 退出登录 |

### 数据

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/dashboard` | GET | 仪表盘数据 (状态+热力图) |
| `/api/stocks` | GET/POST/DELETE | 股票池管理 |
| `/api/portfolio` | GET/POST | 投资组合管理 |
| `/api/signals` | GET | 信号分析 |
| `/api/charts` | GET | 图表数据 |
| `/api/heatmap` | GET | 板块热力图 |
| `/api/strategies` | GET | 策略列表 |
| `/api/factors` | GET | 因子列表 |
| `/api/alerts` | GET | 告警列表 |
| `/api/risk` | GET | 风险指标 |

---

## 🛠️ 技术栈

### 后端
- **Flask** - Web 框架
- **SQLite** - 数据库
- **AKShare** - 行情数据
- **Futu API** - 富途交易接口
- **Pandas** - 数据处理
- **PyYAML** - 配置管理

### 前端
- **Vue 2** - 前端框架
- **Element UI** - UI 组件库
- **Vue Router** - 路由管理
- **Vuex** - 状态管理
- **ECharts** - 数据可视化
- **Axios** - HTTP 请求

---

## 📊 项目统计

| 指标 | 数据 |
|------|------|
| Python 文件 | 147+ |
| 前端文件 | 35+ |
| 代码行数 | ~30K |
| 功能页面 | 25+ |
| API 端点 | 15+ |
| 策略数量 | 30+ |
| 因子数量 | 25+ |
| Git 提交 | 80+ |

---

## 📝 更新日志

### v3.1.0 (2026-04-18)
- 🎨 Vue + Element UI 前端重构
- 🔐 登录认证 + Token 机制
- 📋 侧边栏分组折叠菜单
- 🌍 投资组合管理
- 📰 文章信息 + TrendRadar 集成
- 🔥 板块热力图
- 🧹 代码优化 (合并重复模块)
- 📉 仪表盘涨跌热力图
- 💼 股票池增删查改

### v3.0.0 (2026-04-17)
- 🦜 Phase 1-108 完成
- 核心架构搭建
- 30+ 策略实现
- 25+ 因子研究

---

## 📄 License

MIT License

---

<div align="center">
  <strong>🦜 翠花量化 - 让交易更智能</strong>
</div>
