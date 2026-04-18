/**
 * 图表主题系统 - 自动适配深色/浅色主题
 */

// 深色主题配置
export const DARK_THEME = {
  backgroundColor: '#1a1a2e',
  textColor: '#d1d4dc',
  axisLineColor: '#2a2a3e',
  splitLineColor: '#2a2a3e',
  tooltipBackgroundColor: 'rgba(42, 42, 62, 0.9)',
  tooltipTextColor: '#d1d4dc',
  seriesColors: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#ffeb3b', '#ff9800', '#00bcd4'],
  upColor: '#26a69a',
  downColor: '#ef5350'
}

// 浅色主题配置
export const LIGHT_THEME = {
  backgroundColor: '#ffffff',
  textColor: '#333333',
  axisLineColor: '#e0e0e0',
  splitLineColor: '#f0f0f0',
  tooltipBackgroundColor: 'rgba(0, 0, 0, 0.8)',
  tooltipTextColor: '#ffffff',
  seriesColors: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#ffeb3b', '#ff9800', '#00bcd4'],
  upColor: '#ef232a',
  downColor: '#14b143'
}

/**
 * 获取当前主题配置
 */
export function getThemeConfig(isDark = true) {
  return isDark ? DARK_THEME : LIGHT_THEME
}

/**
 * 应用主题到图表实例
 */
export function applyTheme(chart, isDark = true) {
  const theme = getThemeConfig(isDark)
  chart.setOption({
    backgroundColor: theme.backgroundColor,
    textStyle: { color: theme.textColor },
    xAxis: {
      axisLine: { lineStyle: { color: theme.axisLineColor } },
      splitLine: { lineStyle: { color: theme.splitLineColor } },
      axisLabel: { color: theme.textColor }
    },
    yAxis: {
      axisLine: { lineStyle: { color: theme.axisLineColor } },
      splitLine: { lineStyle: { color: theme.splitLineColor } },
      axisLabel: { color: theme.textColor }
    },
    tooltip: {
      backgroundColor: theme.tooltipBackgroundColor,
      textStyle: { color: theme.tooltipTextColor }
    },
    legend: {
      textStyle: { color: theme.textColor }
    }
  }, true)
}

/**
 * 获取系列颜色
 */
export function getSeriesColors(index, isDark = true) {
  const theme = getThemeConfig(isDark)
  return theme.seriesColors[index % theme.seriesColors.length]
}
