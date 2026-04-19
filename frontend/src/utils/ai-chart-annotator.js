/**
 * Phase 313: AI 智能标注
 * 自动在图表上添加 AI 识别的买卖点、形态标注、异常标记
 */
export default class AIChartAnnotator {
  /**
   * 为 K 线图生成 AI 标注
   * @param {Array} klineData - K线数据
   * @returns {Object} ECharts markPoint/markLine 配置
   */
  static annotateKline(klineData) {
    if (!klineData || klineData.length < 20) return {}
    
    const markPoints = []
    const markLines = []
    
    // 1. 识别买卖点
    const signals = this.detectSignals(klineData)
    signals.forEach(s => {
      markPoints.push({
        name: s.type,
        coord: [s.date, s.price],
        value: s.type === 'buy' ? '🟢买' : '🔴卖',
        itemStyle: { color: s.type === 'buy' ? '#ef232a' : '#14b143' }
      })
    })
    
    // 2. 识别支撑压力线
    const srLevels = this.calcSupportResistance(klineData)
    srLevels.support.forEach(level => {
      markLines.push({
        name: '支撑位',
        yAxis: level,
        lineStyle: { color: '#409EFF', type: 'dashed', width: 1 },
        label: { formatter: `支撑 {c}`, position: 'insideStartTop' }
      })
    })
    srLevels.resistance.forEach(level => {
      markLines.push({
        name: '压力位',
        yAxis: level,
        lineStyle: { color: '#e6a23c', type: 'dashed', width: 1 },
        label: { formatter: `压力 {c}`, position: 'insideEndTop' }
      })
    })
    
    // 3. 标注异常点
    const anomalies = this.detectAnomalies(klineData)
    anomalies.forEach(a => {
      markPoints.push({
        name: '异常',
        coord: [a.date, a.price],
        value: '⚠️',
        itemStyle: { color: '#f56c6c' }
      })
    })
    
    return { markPoints, markLines }
  }
  
  /**
   * 买卖信号识别
   */
  static detectSignals(klineData) {
    const signals = []
    const closes = klineData.map(d => d.close || d.c)
    
    // 金叉/死叉
    for (let i = 10; i < closes.length; i++) {
      const ma5_prev = this.avg(closes.slice(i - 10, i - 5))
      const ma10_prev = this.avg(closes.slice(i - 10, i))
      const ma5_curr = this.avg(closes.slice(i - 5, i))
      const ma10_curr = this.avg(closes.slice(i - 5, i + 1)) || ma10_prev
      
      // 金叉
      if (ma5_prev <= ma10_prev && ma5_curr > ma10_curr) {
        signals.push({
          date: klineData[i].date,
          price: closes[i],
          type: 'buy',
          reason: 'MA5上穿MA10'
        })
      }
      // 死叉
      if (ma5_prev >= ma10_prev && ma5_curr < ma10_curr) {
        signals.push({
          date: klineData[i].date,
          price: closes[i],
          type: 'sell',
          reason: 'MA5下穿MA10'
        })
      }
    }
    
    return signals
  }
  
  /**
   * 支撑压力位计算 (基于近期高低点聚类)
   */
  static calcSupportResistance(klineData, lookback = 30) {
    const data = klineData.slice(-lookback)
    const highs = data.map(d => d.high || d.h)
    const lows = data.map(d => d.low || d.l)
    
    // 聚类简化
    const sortedHighs = [...highs].sort((a, b) => b - a)
    const sortedLows = [...lows].sort((a, b) => a - b)
    
    return {
      support: sortedLows.slice(0, 2).map(v => parseFloat(v.toFixed(2))),
      resistance: sortedHighs.slice(0, 2).map(v => parseFloat(v.toFixed(2)))
    }
  }
  
  /**
   * 异常检测
   */
  static detectAnomalies(klineData) {
    const anomalies = []
    const closes = klineData.map(d => d.close || d.c)
    
    // 计算涨跌幅
    const changes = []
    for (let i = 1; i < closes.length; i++) {
      changes.push((closes[i] - closes[i-1]) / closes[i-1])
    }
    
    const mean = changes.reduce((a, b) => a + b, 0) / changes.length
    const std = Math.sqrt(changes.reduce((sum, c) => sum + (c - mean) ** 2, 0) / changes.length)
    
    // 检测异常波动 (>2σ)
    changes.forEach((change, i) => {
      if (Math.abs(change - mean) > 2 * std) {
        anomalies.push({
          date: klineData[i + 1].date,
          price: closes[i + 1],
          type: 'volatility',
          reason: `异常波动 ${(change * 100).toFixed(2)}%`
        })
      }
    })
    
    return anomalies
  }
  
  /**
   * 为 ECharts 生成完整 option 增强
   */
  static enhanceOption(baseOption, klineData) {
    const annotation = this.annotateKline(klineData)
    
    return {
      ...baseOption,
      series: (baseOption.series || []).map((s, idx) => {
        if (idx === 0 && s.type === 'candlestick') {
          return {
            ...s,
            markPoint: {
              data: annotation.markPoints || [],
              symbolSize: 40,
              label: { show: true, fontSize: 10 }
            },
            markLine: {
              data: annotation.markLines || [],
              silent: true,
              symbol: 'none'
            }
          }
        }
        return s
      })
    }
  }
  
  /**
   * 计算均值
   */
  static avg(arr) {
    return arr.reduce((a, b) => a + b, 0) / arr.length
  }
}
