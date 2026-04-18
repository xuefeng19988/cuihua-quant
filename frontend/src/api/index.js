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
