import Vue from 'vue'
import Router from 'vue-router'
import Layout from '@/layout'

Vue.use(Router)

export const constantRoutes = [
  { path: '/login', component: () => import('@/views/login/index'), hidden: true },
  { path: '/register', component: () => import('@/views/register/index'), hidden: true },
  { path: '/404', component: () => import('@/views/404'), hidden: true },

  // ===== 1. 监控看板 =====
  { path: '/', component: Layout, redirect: '/dashboard', children: [{ path: 'dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/index'), meta: { title: '监控看板', icon: 'dashboard' } }] },

  // ===== 2. 股票中心 =====
  { path: '/stocks', component: Layout, redirect: '/stocks/pool', name: 'Stocks', meta: { title: '股票中心', icon: 'el-icon-s-data' }, children: [
    { path: 'pool', name: 'StockPool', component: () => import('@/views/stocks/index'), meta: { title: '股票池', icon: 'el-icon-s-grid' } },
    { path: 'watchlist', name: 'Watchlist', component: () => import('@/views/watchlist/index'), meta: { title: '自选股', icon: 'el-icon-star-on' } },
    { path: 'detail', name: 'StockDetail', component: () => import('@/views/stock-detail/index'), meta: { title: '个股详情', icon: 'el-icon-info' } },
    { path: 'detail/:id', name: 'StockDetailById', component: () => import('@/views/stock-detail/index'), meta: { title: '个股详情', icon: 'el-icon-info' }, hidden: true },
    { path: 'compare', name: 'StockCompare', component: () => import('@/views/stock-compare/index'), meta: { title: '股票对比', icon: 'el-icon-s-data' } },
    { path: 'scoring', name: 'ScoringDashboard', component: () => import('@/views/scoring-dashboard/index'), meta: { title: '评分排行', icon: 'el-icon-trophy' } },
    { path: 'alerts', name: 'StockAlerts', component: () => import('@/views/stock-alerts/index'), meta: { title: '行情异动', icon: 'el-icon-warning' } },
    { path: 'news', name: 'StockNews', component: () => import('@/views/stock-news/index'), meta: { title: '股票资讯', icon: 'el-icon-news' } },
    { path: 'smart-alerts', name: 'SmartAlerts', component: () => import('@/views/smart-alerts/index'), meta: { title: '智能提醒', icon: 'el-icon-bell' } },
    { path: 'sentiment', name: 'Sentiment', component: () => import('@/views/sentiment/index'), meta: { title: '市场情绪', icon: 'el-icon-s-custom' } },
  ]},

  // ===== 3. 投资组合 =====
  { path: '/portfolio', component: Layout, redirect: '/portfolio/holdings', name: 'Portfolio', meta: { title: '投资组合', icon: 'el-icon-s-marketing' }, children: [
    { path: 'holdings', name: 'PortfolioHoldings', component: () => import('@/views/portfolio/index'), meta: { title: '持仓管理', icon: 'el-icon-s-cooperation' } },
    { path: 'report', name: 'PortfolioReport', component: () => import('@/views/portfolio-report/index'), meta: { title: '持仓报告', icon: 'el-icon-s-management' } },
    { path: 'industry', name: 'IndustryCompare', component: () => import('@/views/industry-compare/index'), meta: { title: '行业对比', icon: 'el-icon-s-data' } },
    { path: 'sector', name: 'SectorRotation', component: () => import('@/views/sector-rotation/index'), meta: { title: '板块轮动', icon: 'el-icon-s-opportunity' } },
    { path: 'fund-flow', name: 'FundFlow', component: () => import('@/views/fund-flow/index'), meta: { title: '资金流向', icon: 'el-icon-money' } },
    { path: 'financial', name: 'FinancialData', component: () => import('@/views/financial-data/index'), meta: { title: '财务数据', icon: 'el-icon-document' } },
    { path: 'macro', name: 'MacroData', component: () => import('@/views/macro-data/index'), meta: { title: '宏观数据', icon: 'el-icon-s-marketing' } },
    { path: 'us-hk', name: 'UsHkData', component: () => import('@/views/us-hk-data/index'), meta: { title: '美股港股', icon: 'el-icon-s-finance' } },
  ]},

  // ===== 4. 交易 =====
  { path: '/trade', component: Layout, redirect: '/trade/analysis', name: 'Trade', meta: { title: '交易', icon: 'el-icon-s-order' }, children: [
    { path: 'analysis', name: 'Analysis', component: () => import('@/views/analysis/index'), meta: { title: '信号分析', icon: 'el-icon-trend-charts' } },
    { path: 'charts', name: 'Charts', component: () => import('@/views/charts/index'), meta: { title: '图表分析', icon: 'el-icon-data-line' } },
    { path: 'simulator', name: 'TradeSimulator', component: () => import('@/views/trade-simulator/index'), meta: { title: '模拟交易', icon: 'el-icon-s-order' } },
    { path: 'paper', name: 'Paper', component: () => import('@/views/paper/index'), meta: { title: '模拟盘', icon: 'el-icon-document' } },
    { path: 'calendar', name: 'TradeCalendar', component: () => import('@/views/trade-calendar/index'), meta: { title: '交易日历', icon: 'el-icon-date' } },
    { path: 'options', name: 'OptionStrategy', component: () => import('@/views/option-strategy/index'), meta: { title: '期权策略', icon: 'el-icon-s-cooperation' } },
  ]},

  // ===== 5. 策略研究 =====
  { path: '/research', component: Layout, redirect: '/research/strategies', name: 'Research', meta: { title: '策略研究', icon: 'el-icon-notebook-2' }, children: [
    { path: 'strategies', name: 'Strategies', component: () => import('@/views/strategies/index'), meta: { title: '策略管理', icon: 'el-icon-medal' } },
    { path: 'factors', name: 'Factors', component: () => import('@/views/factors/index'), meta: { title: '因子研究', icon: 'el-icon-s-grid' } },
    { path: 'backtest', name: 'Backtest', component: () => import('@/views/backtest/index'), meta: { title: '回测中心', icon: 'el-icon-s-claim' } },
    { path: 'strategy-backtest', name: 'StrategyBacktest', component: () => import('@/views/strategy-backtest/index'), meta: { title: '策略回测', icon: 'el-icon-s-claim' } },
    { path: 'heatmap', name: 'Heatmap', component: () => import('@/views/heatmap/index'), meta: { title: '热力图', icon: 'el-icon-s-opportunity' } },
    { path: 'events', name: 'Events', component: () => import('@/views/events/index'), meta: { title: '事件研究', icon: 'el-icon-calendar' } },
    { path: 'recommend', name: 'StrategyRecommender', component: () => import('@/views/strategy-recommender/index'), meta: { title: '策略推荐', icon: 'el-icon-s-check' } },
    { path: 'upgrade', name: 'StrategyUpgrade', component: () => import('@/views/strategy-upgrade/index'), meta: { title: '策略升级', icon: 'el-icon-s-promotion' } },
    { path: 'articles', name: 'Articles', component: () => import('@/views/articles/index'), meta: { title: '文章资讯', icon: 'el-icon-news' } },
    { path: 'notes', name: 'Notes', component: () => import('@/views/notes/index'), meta: { title: '笔记管理', icon: 'el-icon-edit-outline' } },
    { path: 'community', name: 'Community', component: () => import('@/views/community/index'), meta: { title: '策略社区', icon: 'el-icon-s-custom' } },
  ]},

  // ===== 6. 风控告警 =====
  { path: '/risk', component: Layout, redirect: '/risk/monitor', name: 'Risk', meta: { title: '风控告警', icon: 'el-icon-lock' }, children: [
    { path: 'monitor', name: 'RiskMonitor', component: () => import('@/views/risk/index'), meta: { title: '风险监控', icon: 'el-icon-warning' } },
    { path: 'alerts', name: 'Alerts', component: () => import('@/views/alerts/index'), meta: { title: '告警中心', icon: 'el-icon-bell' } },
    { path: 'stoploss', name: 'Stoploss', component: () => import('@/views/stoploss/index'), meta: { title: '智能止损', icon: 'el-icon-close' } },
    { path: 'stress', name: 'Stress', component: () => import('@/views/stress/index'), meta: { title: '压力测试', icon: 'el-icon-s-help' } },
    { path: 'compliance', name: 'Compliance', component: () => import('@/views/compliance/index'), meta: { title: '合规检查', icon: 'el-icon-circle-check' } },
    { path: 'smart-alert', name: 'SmartAlert', component: () => import('@/views/smart-alert/index'), meta: { title: '智能预警', icon: 'el-icon-warning' } },
  ]},

  // ===== 7. AI 中心 =====
  { path: '/ai-center', component: Layout, redirect: '/ai-center/chat', name: 'AICenter', meta: { title: 'AI 中心', icon: 'el-icon-magic-stick' }, children: [
    { path: 'chat', name: 'AIChat', component: () => import('@/views/ai-center/index'), meta: { title: '🤖 AI 对话', icon: 'el-icon-chat-dot-round' } },
    { path: 'stock', name: 'AIStock', component: () => import('@/views/ai-center/index'), meta: { title: '📈 AI 个股', icon: 'el-icon-trend-charts' } },
    { path: 'note', name: 'AINote', component: () => import('@/views/ai-center/index'), meta: { title: '📝 AI 笔记', icon: 'el-icon-edit-outline' } },
    { path: 'market', name: 'AIMarket', component: () => import('@/views/ai-center/index'), meta: { title: '📊 市场总结', icon: 'el-icon-s-data' } },
    { path: 'stock-ai', name: 'AIStockFeatures', component: () => import('@/views/ai-center/index'), meta: { title: '🤖 股票 AI', icon: 'el-icon-magic-stick' } },
    { path: 'config', name: 'AIConfig', component: () => import('@/views/ai-center/index'), meta: { title: '⚙️ 模型管理', icon: 'el-icon-setting' } },
    { path: 'reports', name: 'AIReports', component: () => import('@/views/ai-reports/index'), meta: { title: '📋 AI 研报', icon: 'el-icon-document-copy' } },
    { path: 'sentiment-engine', name: 'SentimentEngine', component: () => import('@/views/sentiment-engine/index'), meta: { title: '📊 情绪引擎', icon: 'el-icon-s-opportunity' } },
  ]},

  // ===== 8. 系统工具 =====
  { path: '/system', component: Layout, redirect: '/system/performance', name: 'System', meta: { title: '系统工具', icon: 'el-icon-s-tools' }, children: [
    { path: 'performance', name: 'Performance', component: () => import('@/views/performance/index'), meta: { title: '绩效分析', icon: 'el-icon-data-analysis' } },
    { path: 'behavior', name: 'Behavior', component: () => import('@/views/behavior/index'), meta: { title: '行为分析', icon: 'el-icon-headset' } },
    { path: 'paramopt', name: 'ParamOpt', component: () => import('@/views/paramopt/index'), meta: { title: '参数优化', icon: 'el-icon-cpu' } },
    { path: 'reports', name: 'Reports', component: () => import('@/views/reports/index'), meta: { title: '自动报告', icon: 'el-icon-document-copy' } },
    { path: 'research-notebook', name: 'ResearchNotebook', component: () => import('@/views/research/index'), meta: { title: '研究笔记本', icon: 'el-icon-notebook-1' } },
    { path: 'data-quality', name: 'DataQuality', component: () => import('@/views/data-quality/index'), meta: { title: '数据质量', icon: 'el-icon-circle-check' } },
    { path: 'scatter', name: 'ScatterPlot', component: () => import('@/views/scatter-plot/index'), meta: { title: '散点图', icon: 'el-icon-s-data' } },
    { path: 'custom-dashboard', name: 'CustomDashboard', component: () => import('@/views/custom-dashboard/index'), meta: { title: '自定义仪表板', icon: 'el-icon-s-grid' } },
  ]},

  // ===== 9. 系统管理 =====
  { path: '/admin', component: Layout, redirect: '/admin/settings', name: 'Admin', meta: { title: '系统管理', icon: 'el-icon-s-tools' }, children: [
    { path: 'settings', name: 'Settings', component: () => import('@/views/settings/index'), meta: { title: '系统设置', icon: 'el-icon-setting' } },
    { path: 'notifications', name: 'Notifications', component: () => import('@/views/notifications/index'), meta: { title: '通知中心', icon: 'el-icon-bell' } },
    { path: 'users', name: 'MultiUser', component: () => import('@/views/multi-user/index'), meta: { title: '用户管理', icon: 'el-icon-user' } },
    { path: 'backup', name: 'BackupManager', component: () => import('@/views/backup-manager/index'), meta: { title: '备份管理', icon: 'el-icon-files' } },
    { path: 'realtime', name: 'RealtimePusher', component: () => import('@/views/realtime-pusher/index'), meta: { title: '实时推送', icon: 'el-icon-connection' } },
    { path: 'scheduler', name: 'Scheduler', component: () => import('@/views/scheduler/index'), meta: { title: '定时任务', icon: 'el-icon-alarm-clock' } },
    { path: 'perf-monitor', name: 'PerfMonitor', component: () => import('@/views/perf-monitor/index'), meta: { title: '性能监控', icon: 'el-icon-monitor' } },
    { path: 'log-analyzer', name: 'LogAnalyzer', component: () => import('@/views/log-analyzer/index'), meta: { title: '日志分析', icon: 'el-icon-document-copy' } },
    { path: 'db-optimizer', name: 'DBOptimizer', component: () => import('@/views/db-optimizer/index'), meta: { title: '数据库优化', icon: 'el-icon-s-tools' } },
    { path: 'cache-manager', name: 'CacheManager', component: () => import('@/views/cache-manager/index'), meta: { title: '缓存管理', icon: 'el-icon-connection' } },
    { path: 'theme', name: 'ThemeSwitcher', component: () => import('@/views/theme-switcher/index'), meta: { title: '主题切换', icon: 'el-icon-sunny' } },
    { path: 'strategy-market', name: 'StrategyMarket', component: () => import('@/views/strategy-market/index'), meta: { title: '策略市场', icon: 'el-icon-shopping-cart-full' } },
  ]},

  { path: '/knowledge-base', component: Layout, children: [{ path: '', name: 'KnowledgeBase', component: () => import('@/views/knowledge-base/index'), meta: { title: '知识库', icon: 'el-icon-notebook-2' } }] },
  { path: '*', redirect: '/404', hidden: true }
]

export default new Router({ mode: 'history', scrollBehavior: () => ({ y: 0 }), routes: constantRoutes })
