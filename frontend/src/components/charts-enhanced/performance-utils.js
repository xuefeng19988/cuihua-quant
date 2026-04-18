/**
 * 图表性能优化工具 - Phase 251
 * 大数据量渲染优化
 */

export class ChartPerformanceOptimizer {
  /**
   * 数据抽样 - 大数据量时抽取样本点
   * @param {Array} data - 原始数据
   * @param {number} maxPoints - 最大点数
   * @returns {Array} 抽样后的数据
   */
  static sampleData(data, maxPoints = 500) {
    if (!data || data.length <= maxPoints) return data
    
    const step = Math.ceil(data.length / maxPoints)
    const sampled = []
    
    for (let i = 0; i < data.length; i += step) {
      sampled.push(data[i])
    }
    
    return sampled
  }
  
  /**
   * 增量更新 - 只更新变化的数据
   * @param {Object} chart - 图表实例
   * @param {Object} newData - 新数据
   * @param {Object} oldData - 旧数据
   */
  static incrementalUpdate(chart, newData, oldData) {
    if (!chart || !newData) return
    
    // 比较数据差异
    const hasChanges = !oldData || JSON.stringify(newData) !== JSON.stringify(oldData)
    
    if (hasChanges) {
      chart.setOption({
        series: newData.series?.map((s, i) => ({
          data: s.data,
          animation: true,
          animationDuration: 300
        }))
      }, false)
    }
    
    return newData
  }
  
  /**
   * 防抖处理
   * @param {Function} fn - 需要防抖的函数
   * @param {number} delay - 延迟时间 (ms)
   * @returns {Function} 防抖后的函数
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
   * @param {Function} fn - 需要节流的函数
   * @param {number} delay - 延迟时间 (ms)
   * @returns {Function} 节流后的函数
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
  
  /**
   * 虚拟滚动优化
   * @param {Array} data - 完整数据
   * @param {number} startIndex - 开始索引
   * @param {number} endIndex - 结束索引
   * @returns {Array} 可见区域数据
   */
  static virtualScroll(data, startIndex, endIndex) {
    if (!data) return []
    return data.slice(startIndex, endIndex)
  }
  
  /**
   * Web Worker 数据处理
   * @param {Array} data - 原始数据
   * @param {Function} processor - 处理函数
   * @returns {Promise} 处理结果
   */
  static async processWithWorker(data, processor) {
    return new Promise((resolve, reject) => {
      try {
        // 在主线程中处理 (简化版)
        const result = processor(data)
        resolve(result)
      } catch (error) {
        reject(error)
      }
    })
  }
  
  /**
   * 图表渲染优化配置
   * @returns {Object} 优化配置
   */
  static getOptimizedConfig() {
    return {
      // 开启大数据量优化
      large: true,
      // 关闭动画提升性能
      animation: false,
      // 使用 Canvas 渲染
      renderer: 'canvas',
      // 渐进式渲染
      progressive: 400,
      // 渐进式渲染阈值
      progressiveThreshold: 3000,
      // 开启 hover 优化
      hoverLayerThreshold: 3000,
      // 关闭不必要的计算
      useUTC: false
    }
  }
}
