# 系统优化清单 - 股票/笔记/AI/图表

> 基于 Phase 297 代码审计结果

---

## 🔍 当前问题诊断

### 1. 路由冲突（严重）

| 端点 | 位置 | 状态 |
|------|------|------|
| `/api/ai-stock-pick` (旧 mock) | api_server.py:2025 | ⚠️ 假数据，应删除 |
| `/api/ai/stock-pick` (新 LLM) | ai_stock_features.py | ✅ 真实 AI |
| `/api/ai-report` (旧 mock) | api_server.py:2728 | ⚠️ 假数据，应删除 |
| `/api/ai/generate-report` (新 LLM) | ai_service.py | ✅ 真实 AI |
| `/api/ai/analyze-stock` (旧) | ai_service.py | ⚠️ 与 financial-reading 重复 |

### 2. 27 处路由重复

- api_server.py 与 routes/ 模块大量重复（auth/charts/stock/analysis）
- `/api/stocks` 出现 4 次（api_server.py ×2, webui_v3.py, routes/stocks.py）
- `/api/articles` 出现 3 次

### 3. f-string SQL 注入残留

- 47 处分布在全项目
- api_server.py 仍有 8 处
- src/strategy/, src/execution/, src/core/ 多处

### 4. 前端页面冗余

| 重复组 | 页面 |
|--------|------|
| 回测 | 回测中心 + 策略回测 |
| 告警 | 告警中心 + 智能预警 + 智能提醒 |
| AI 研报 | AI研报 + AI中心/研报 |

### 5. 图表优化空间

| 页面 | 现状 | 优化方向 |
|------|------|---------|
| 个股详情 | 基础分时图 | + 指标叠加 + 画线工具 |
| 评分排行 | 纯表格 | + 雷达图 + 柱状对比 |
| 持仓分析 | 基础饼图 | + 行业旭日图 + 收益瀑布图 |
| 新闻情绪 | 无图表 | + 情绪走势图 |
| AI 分析 | 纯文字 | + 图表可视化 |

---

## 📋 优化计划

### Phase 297: 路由清理 + 删除假数据
- 删除 api_server.py 旧 mock AI 端点
- 合并 /api/notes 与 /api/articles
- 清理重复路由

### Phase 298: 前端页面整合
- 合并重复页面
- 统一告警中心
- 清理冗余路由

### Phase 299: 图表系统增强
- 技术指标叠加
- 评分雷达图
- AI 分析图表化
- 持仓可视化增强

### Phase 300: 笔记系统增强
- Markdown 编辑器增强
- 笔记关联股票
- 笔记模板
- 导出功能

---

## 📊 优先级

1. **Phase 297** - 路由清理 (基础)
2. **Phase 299** - 图表增强 (用户感知最强)
3. **Phase 298** - 页面整合
4. **Phase 300** - 笔记增强

---

_2026-04-20_
