/**
 * 增强图表组件库 - Phase 245
 * 统一主题、性能优化、响应式设计
 */

// 核心组件
export { default as EnhancedChart } from './enhanced-chart.vue'
export { default as ComboChart } from './combo-chart.vue'
export { default as RealtimeChart } from './realtime-chart.vue'
export { default as CompareChart } from './compare-chart.vue'

// 工具函数
export { getThemeConfig, applyTheme, getSeriesColors, DARK_THEME, LIGHT_THEME } from './theme'

// 性能优化工具
export class ChartPerformanceOptimizer {
  /**
   * 数据抽样 - 大数据量时抽取样本点
   */
  static sampleData(data, maxPoints = 500) {
    if (data.length <= maxPoints) return data
    
    const step = Math.ceil(data.length / maxPoints)
    const sampled = []
    for (let i = 0; i < data.length; i += step) {
      sampled.push(data[i])
    }
    return sampled
  }
  
  /**
   * 增量更新 - 只更新变化的数据
   */
  static incrementalUpdate(chart, newData, oldData) {
    // 实现增量更新逻辑
    return newData
  }
  
  /**
   * 防抖处理
   */
  static debounce(fn, delay = 300) {
    let timer = null
    return function(...args) {
      if (timer) clearTimeout(timer)
      timer = setTimeout(() => fn.apply(this, args), delay)
    }
  }
  
  /**
   * 节流处理
   */
  static throttle(fn, delay = 300) {
    let lastTime = 0
    return function(...args) {
      const now = Date.now()
      if (now - lastTime >= delay) {
        fn.apply(this, args)
        lastTime = now
      }
    }
  }
}
