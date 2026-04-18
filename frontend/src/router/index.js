import Vue from 'vue'
import Router from 'vue-router'
import Layout from '@/layout'

Vue.use(Router)

export const constantRoutes = [
  { path: '/login', component: () => import('@/views/login/index'), hidden: true },
  { path: '/register', component: () => import('@/views/register/index'), hidden: true },
  { path: '/404', component: () => import('@/views/404'), hidden: true },
  { path: '/', component: Layout, redirect: '/dashboard', children: [{ path: 'dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/index'), meta: { title: '监控看板', icon: 'dashboard' } }] },
  { path: '/stocks', component: Layout, children: [{ path: '', name: 'Stocks', component: () => import('@/views/stocks/index'), meta: { title: '股票池', icon: 'el-icon-s-data' } }] },
  { path: '/portfolio', component: Layout, children: [{ path: '', name: 'Portfolio', component: () => import('@/views/portfolio/index'), meta: { title: '投资组合', icon: 'el-icon-s-marketing' } }] },
  { path: '/watchlist', component: Layout, children: [{ path: '', name: 'Watchlist', component: () => import('@/views/watchlist/index'), meta: { title: '自选股', icon: 'el-icon-star-on' } }] },
  { path: '/trade', component: Layout, redirect: '/analysis', name: 'Trade', meta: { title: '交易', icon: 'el-icon-s-order' }, children: [
    { path: 'analysis', name: 'Analysis', component: () => import('@/views/analysis/index'), meta: { title: '信号分析', icon: 'el-icon-trend-charts' } },
    { path: 'charts', name: 'Charts', component: () => import('@/views/charts/index'), meta: { title: '图表分析', icon: 'el-icon-data-line' } },
    { path: 'backtest', name: 'Backtest', component: () => import('@/views/backtest/index'), meta: { title: '回测中心', icon: 'el-icon-s-claim' } },
    { path: 'paper', name: 'Paper', component: () => import('@/views/paper/index'), meta: { title: '模拟盘', icon: 'el-icon-document' } }
  ]},
  { path: '/research', component: Layout, redirect: '/strategies', name: 'Research', meta: { title: '研究', icon: 'el-icon-notebook-2' }, children: [
    { path: 'strategies', name: 'Strategies', component: () => import('@/views/strategies/index'), meta: { title: '策略管理', icon: 'el-icon-medal' } },
    { path: 'factors', name: 'Factors', component: () => import('@/views/factors/index'), meta: { title: '因子研究', icon: 'el-icon-s-grid' } },
    { path: 'heatmap', name: 'Heatmap', component: () => import('@/views/heatmap/index'), meta: { title: '热力图', icon: 'el-icon-s-opportunity' } },
    { path: 'events', name: 'Events', component: () => import('@/views/events/index'), meta: { title: '事件研究', icon: 'el-icon-calendar' } },
    { path: 'articles', name: 'Articles', component: () => import('@/views/articles/index'), meta: { title: '文章信息', icon: 'el-icon-news' } }
  ]},
  { path: '/risk', component: Layout, redirect: '/risk-monitor', name: 'Risk', meta: { title: '风控', icon: 'el-icon-lock' }, children: [
    { path: 'monitor', name: 'RiskMonitor', component: () => import('@/views/risk/index'), meta: { title: '风险监控', icon: 'el-icon-warning' } },
    { path: 'alerts', name: 'Alerts', component: () => import('@/views/alerts/index'), meta: { title: '告警中心', icon: 'el-icon-bell' } },
    { path: 'stoploss', name: 'Stoploss', component: () => import('@/views/stoploss/index'), meta: { title: '智能止损', icon: 'el-icon-close' } },
    { path: 'stress', name: 'Stress', component: () => import('@/views/stress/index'), meta: { title: '压力测试', icon: 'el-icon-s-help' } },
    { path: 'compliance', name: 'Compliance', component: () => import('@/views/compliance/index'), meta: { title: '合规检查', icon: 'el-icon-circle-check' } }
  ]},
  { path: '/tools', component: Layout, redirect: '/performance', name: 'Tools', meta: { title: '工具', icon: 'el-icon-s-tools' }, children: [
    { path: 'performance', name: 'Performance', component: () => import('@/views/performance/index'), meta: { title: '绩效分析', icon: 'el-icon-data-analysis' } },
    { path: 'behavior', name: 'Behavior', component: () => import('@/views/behavior/index'), meta: { title: '行为分析', icon: 'el-icon-headset' } },
    { path: 'paramopt', name: 'ParamOpt', component: () => import('@/views/paramopt/index'), meta: { title: '参数优化', icon: 'el-icon-cpu' } },
    { path: 'reports', name: 'Reports', component: () => import('@/views/reports/index'), meta: { title: '自动报告', icon: 'el-icon-document-copy' } },
    { path: 'research-notebook', name: 'ResearchNotebook', component: () => import('@/views/research/index'), meta: { title: '研究笔记本', icon: 'el-icon-notebook-1' } },
    { path: 'data-quality', name: 'DataQuality', component: () => import('@/views/data-quality/index'), meta: { title: '数据质量', icon: 'el-icon-circle-check' } },
    { path: 'notes', name: 'Notes', component: () => import('@/views/notes/index'), meta: { title: '笔记管理', icon: 'el-icon-edit-outline' } }
  ]},
  { path: '/notifications', component: Layout, children: [{ path: '', name: 'Notifications', component: () => import('@/views/notifications/index'), meta: { title: '通知中心', icon: 'el-icon-bell' } }] },
  { path: '/stock-detail', component: Layout, children: [{ path: '', name: 'StockDetail', component: () => import('@/views/stock-detail/index'), meta: { title: '个股详情', icon: 'el-icon-info' } }] },
  { path: '/sector-rotation', component: Layout, children: [{ path: '', name: 'SectorRotation', component: () => import('@/views/sector-rotation/index'), meta: { title: '板块轮动', icon: 'el-icon-s-data' } }] },
  { path: '/fund-flow', component: Layout, children: [{ path: '', name: 'FundFlow', component: () => import('@/views/fund-flow/index'), meta: { title: '资金流向', icon: 'el-icon-money' } }] },
  { path: '/financial-data', component: Layout, children: [{ path: '', name: 'FinancialData', component: () => import('@/views/financial-data/index'), meta: { title: '财务数据', icon: 'el-icon-document' } }] },
  { path: '/trade-simulator', component: Layout, children: [{ path: '', name: 'TradeSimulator', component: () => import('@/views/trade-simulator/index'), meta: { title: '模拟交易', icon: 'el-icon-s-order' } }] },
  { path: '/strategy-backtest', component: Layout, children: [{ path: '', name: 'StrategyBacktest', component: () => import('@/views/strategy-backtest/index'), meta: { title: '策略回测', icon: 'el-icon-s-claim' } }] },
  { path: '/portfolio-report', component: Layout, children: [{ path: '', name: 'PortfolioReport', component: () => import('@/views/portfolio-report/index'), meta: { title: '持仓报告', icon: 'el-icon-s-management' } }] },
  { path: '/industry-compare', component: Layout, children: [{ path: '', name: 'IndustryCompare', component: () => import('@/views/industry-compare/index'), meta: { title: '行业对比', icon: 'el-icon-s-data' } }] },
  { path: '/macro-data', component: Layout, children: [{ path: '', name: 'MacroData', component: () => import('@/views/macro-data/index'), meta: { title: '宏观数据', icon: 'el-icon-s-marketing' } }] },
  { path: '/sentiment', component: Layout, children: [{ path: '', name: 'Sentiment', component: () => import('@/views/sentiment/index'), meta: { title: '市场情绪', icon: 'el-icon-s-custom' } }] },
  { path: '/trade-calendar', component: Layout, children: [{ path: '', name: 'TradeCalendar', component: () => import('@/views/trade-calendar/index'), meta: { title: '交易日历', icon: 'el-icon-date' } }] },
  { path: '/custom-dashboard', component: Layout, children: [{ path: '', name: 'CustomDashboard', component: () => import('@/views/custom-dashboard/index'), meta: { title: '自定义仪表板', icon: 'el-icon-s-grid' } }] },
  { path: '/option-strategy', component: Layout, children: [{ path: '', name: 'OptionStrategy', component: () => import('@/views/option-strategy/index'), meta: { title: '期权策略', icon: 'el-icon-s-cooperation' } }] },
  { path: '/strategy-market', component: Layout, children: [{ path: '', name: 'StrategyMarket', component: () => import('@/views/strategy-market/index'), meta: { title: '策略市场', icon: 'el-icon-shopping-cart-full' } }] },
  { path: '/theme-switcher', component: Layout, children: [{ path: '', name: 'ThemeSwitcher', component: () => import('@/views/theme-switcher/index'), meta: { title: '主题切换', icon: 'el-icon-sunny' } }] },
  { path: '/scatter-plot', component: Layout, children: [{ path: '', name: 'ScatterPlot', component: () => import('@/views/scatter-plot/index'), meta: { title: '散点图', icon: 'el-icon-s-data' } }] },
  { path: '/settings', component: Layout, children: [{ path: '', name: 'Settings', component: () => import('@/views/settings/index'), meta: { title: '系统设置', icon: 'el-icon-s-tools' } }] },
  { path: '/backup-manager', component: Layout, children: [{ path: '', name: 'BackupManager', component: () => import('@/views/backup-manager/index'), meta: { title: '备份管理', icon: 'el-icon-files' } }] },
  { path: '*', redirect: '/404', hidden: true }
]

export default new Router({ mode: 'history', scrollBehavior: () => ({ y: 0 }), routes: constantRoutes })
