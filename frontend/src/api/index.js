import request from '@/utils/request'

export function login(data) {
  return request({ url: '/auth/login', method: 'post', data })
}

export function getInfo() {
  return request({ url: '/auth/info', method: 'get' })
}

export function logout() {
  return request({ url: '/auth/logout', method: 'post' })
}

export function getDashboard() {
  return request({ url: '/dashboard', method: 'get' })
}

export function getStocks(params) {
  return request({ url: '/stocks', method: 'get', params })
}

export function addStock(data) {
  return request({ url: '/stocks', method: 'post', data })
}

export function deleteStock(code) {
  return request({ url: `/stocks/${code}`, method: 'delete' })
}

export function getPortfolio() {
  return request({ url: '/portfolio', method: 'get' })
}

export function updatePortfolio(data) {
  return request({ url: '/portfolio', method: 'post', data })
}

export function getSignals(params) {
  return request({ url: '/signals', method: 'get', params })
}

export function getCharts(params) {
  return request({ url: '/charts', method: 'get', params })
}

export function getStrategies() {
  return request({ url: '/strategies', method: 'get' })
}

export function getFactors() {
  return request({ url: '/factors', method: 'get' })
}

export function getHeatmap() {
  return request({ url: '/heatmap', method: 'get' })
}

export function getAlerts() {
  return request({ url: '/alerts', method: 'get' })
}

export function getRisk() {
  return request({ url: '/risk', method: 'get' })
}

export function getArticles(params) {
  return request({ url: '/articles', method: 'get', params })
}

export function getBehavior(params) {
  return request({ url: '/behavior', method: 'get', params })
}

export function getEvents(params) {
  return request({ url: '/events', method: 'get', params })
}

export function getStockGroups(params) {
  return request({ url: '/stock-groups', method: 'get', params })
}

export function createStockGroup(data) {
  return request({ url: '/stock-groups', method: 'post', data })
}

export function updateStockGroup(data) {
  return request({ url: '/stock-groups', method: 'put', data })
}

export function deleteStockGroup(data) {
  return request({ url: '/stock-groups', method: 'delete', data })
}

export function getEquityCurve(params) {
  return request({ url: '/equity-curve', method: 'get', params })
}

export function screenStocks(data) {
  return request({ url: '/screener', method: 'post', data })
}

export function exportData(format, params) {
  return request({ url: `/export/${format}`, method: 'get', params })
}

export function importStocks(data) {
  return request({ url: '/stock-import', method: 'post', data })
}

export function exportStocks() {
  return request({ url: '/stock-export', method: 'get' })
}

export function getDataQuality() {
  return request({ url: '/data-quality', method: 'get' })
}

export function getNotifications() {
  return request({ url: '/notifications', method: 'get' })
}

export function markNotificationsRead() {
  return request({ url: '/notifications', method: 'post', data: { action: 'mark_read' } })
}

export function getCacheStats() {
  return request({ url: '/cache/stats', method: 'get' })
}

export function getStockDetail(code) {
  return request({ url: `/stock-detail/${code}`, method: 'get' })
}

export function getSectorRotation() {
  return request({ url: '/sector-rotation', method: 'get' })
}

export function getFundFlow() {
  return request({ url: '/fund-flow', method: 'get' })
}

export function getFinancialData(code) {
  return request({ url: `/financial/${code}`, method: 'get' })
}

export function getTradeSimulator() {
  return request({ url: '/trade-simulator', method: 'get' })
}

export function executeTrade(data) {
  return request({ url: '/trade-simulator', method: 'post', data })
}

export function getAlertConfig() {
  return request({ url: '/alert-config', method: 'get' })
}

export function saveAlertConfig(data) {
  return request({ url: '/alert-config', method: 'post', data })
}

export function getStrategyBacktest() {
  return request({ url: '/strategy-backtest', method: 'get' })
}

export function runStrategyBacktest(data) {
  return request({ url: '/strategy-backtest', method: 'post', data })
}

export function getPortfolioReport() {
  return request({ url: '/portfolio-report', method: 'get' })
}

export function getIndustryCompare() {
  return request({ url: '/industry-compare', method: 'get' })
}

export function getMacroData() {
  return request({ url: '/macro-data', method: 'get' })
}

export function getSentiment() {
  return request({ url: '/sentiment', method: 'get' })
}

export function getTradeCalendar() {
  return request({ url: '/trade-calendar', method: 'get' })
}
