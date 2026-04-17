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
    { path: 'research-notebook', name: 'ResearchNotebook', component: () => import('@/views/research/index'), meta: { title: '研究笔记本', icon: 'el-icon-notebook-1' } }
  ]},
  { path: '/settings', component: Layout, children: [{ path: '', name: 'Settings', component: () => import('@/views/settings/index'), meta: { title: '系统设置', icon: 'el-icon-s-tools' } }] },
  { path: '*', redirect: '/404', hidden: true }
]

export default new Router({ mode: 'history', scrollBehavior: () => ({ y: 0 }), routes: constantRoutes })
