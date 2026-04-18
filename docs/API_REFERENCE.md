# 📚 翠花量化系统 API 参考文档

> **版本**: v5.0.0 | **端点总数**: 105

## 认证 (5个)

| 端点 | 方法 |
|------|------|
| `/api/auth/check-init` | GET |
| `/api/auth/register` | POST |
| `/api/auth/login` | POST |
| `/api/auth/info` | GET |
| `/api/auth/logout` | POST |

## 核心 (13个)

| 端点 | 方法 |
|------|------|
| `/api/dashboard` | GET |
| `/api/stocks` | GET |
| `/api/stocks` | POST |
| `/api/stocks/<code>` | DELETE |
| `/api/portfolio` | GET |
| `/api/portfolio` | POST |
| `/api/signals` | GET |
| `/api/charts` | GET |
| `/api/factors` | GET |
| `/api/heatmap` | GET |
| `/api/stats` | GET |
| `/api/portfolio-report` | GET |
| `/api/community/stats` | GET |

## 交易 (8个)

| 端点 | 方法 |
|------|------|
| `/api/backtest` | GET, POST |
| `/api/watchlist` | DELETE, GET, POST |
| `/api/export/<format>` | GET |
| `/api/screener` | POST |
| `/api/paper` | GET |
| `/api/trade-simulator` | GET, POST |
| `/api/trade-calendar` | GET |
| `/api/option-chain` | GET |

## 研究 (11个)

| 端点 | 方法 |
|------|------|
| `/api/strategies` | GET |
| `/api/articles` | GET |
| `/api/events` | GET |
| `/api/stock-detail/<code>` | GET |
| `/api/sector-rotation` | GET |
| `/api/fund-flow` | GET |
| `/api/financial/<code>` | GET |
| `/api/industry-compare` | GET |
| `/api/macro-data` | GET |
| `/api/sentiment` | GET |
| `/api/sentiment-engine` | GET |

## 风控 (8个)

| 端点 | 方法 |
|------|------|
| `/api/alerts` | GET |
| `/api/risk` | GET |
| `/api/stress` | GET |
| `/api/stoploss` | GET |
| `/api/compliance` | GET |
| `/api/alert-config` | GET, POST |
| `/api/portfolio-report` | GET |
| `/api/risk-engine` | GET, POST |

## 工具 (20个)

| 端点 | 方法 |
|------|------|
| `/api/performance` | GET |
| `/api/equity-curve` | GET |
| `/api/paramopt` | GET, POST |
| `/api/research` | GET |
| `/api/reports` | GET |
| `/api/behavior` | GET |
| `/api/data-quality` | GET |
| `/api/notifications` | GET, POST |
| `/api/performance/lazy` | GET |
| `/api/notes` | GET, POST |
| `/api/notes/<int:note_id>` | DELETE, GET, PUT |
| `/api/notes/upload` | POST |
| `/api/notes/tags` | GET |
| `/api/ai-report` | GET, POST |
| `/api/sentiment-engine` | GET |
| `/api/smart-alert` | GET, POST |
| `/api/strategy-recommender` | GET |
| `/api/community/stats` | GET |
| `/api/data-viz/config` | GET |
| `/api/cache/config` | GET, POST |

## 系统 (25个)

| 端点 | 方法 |
|------|------|
| `/api/stream/quotes` | GET |
| `/api/settings` | GET, POST |
| `/api/backup/create` | POST |
| `/api/backup/list` | GET |
| `/api/backup/download/<filename>` | GET |
| `/api/backup/upload` | POST |
| `/api/backup/restore/<filename>` | POST |
| `/api/backup/delete/<filename>` | DELETE |
| `/api/realtime/status` | GET |
| `/api/users` | GET, POST |
| `/api/pwa/config` | GET |
| `/api/scheduler` | GET, POST |
| `/api/perf-monitor` | GET |
| `/api/log-analyzer` | GET |
| `/api/sync-service` | GET |
| `/api/api-gateway` | GET |
| `/api/docker/status` | GET |
| `/api/health` | GET |
| `/api/db/indexes` | GET, POST |
| `/api/shortcuts` | GET |
| `/api/onboarding` | GET |
| `/api/webhook` | GET, POST |
| `/api/plugins` | GET |
| `/api/sdk/info` | GET |
| `/api/data-market` | GET |

