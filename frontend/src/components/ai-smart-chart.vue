/**
 * Phase 313: AI 智能图表包装器
 * 自动为 ECharts 图表添加 AI 标注、智能提示、异常标记
 */
<template>
  <div class="ai-smart-chart">
    <div ref="chartContainer" :style="{ width: width, height: height }"></div>
    
    <!-- AI 悬浮提示面板 -->
    <transition name="slide-fade">
      <div v-if="showAiPanel" class="ai-float-panel">
        <div class="panel-header">
          <span>🤖 AI 实时解读</span>
          <el-button size="mini" icon="el-icon-close" circle @click="showAiPanel = false"></el-button>
        </div>
        <div class="panel-content">
          <p v-if="aiInsight" class="ai-text">{{ aiInsight }}</p>
          <el-tag v-if="chartSignal" :type="signalType" size="small">{{ signalText }}</el-tag>
        </div>
      </div>
    </transition>
    
    <!-- 快捷操作栏 -->
    <div class="quick-actions" v-if="showActions">
      <el-button-group>
        <el-button size="mini" @click="toggleAiPanel">🤖 AI分析</el-button>
        <el-button size="mini" @click="toggleIndicators">📊 指标</el-button>
        <el-button size="mini" @click="exportChart">💾 导出</el-button>
        <el-button size="mini" @click="fullscreen">⛶ 全屏</el-button>
      </el-button-group>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'AISmartChart',
  props: {
    width: { type: String, default: '100%' },
    height: { type: String, default: '400px' },
    // 图表类型: kline/line/bar/pie/radar
    chartType: { type: String, default: 'kline' },
    // K线数据
    klineData: { type: Array, default: () => [] },
    // 通用数据
    chartData: { type: Object, default: () => ({}) },
    // 是否启用AI
    enableAi: { type: Boolean, default: true },
    // 显示操作栏
    showActions: { type: Boolean, default: true },
  },
  data() {
    return {
      chart: null,
      showAiPanel: false,
      aiInsight: '',
      chartSignal: '',
      indicators: { ma: true, macd: false, rsi: false, boll: false },
    }
  },
  computed: {
    signalType() {
      return this.chartSignal === 'buy' ? 'success' : 
             this.chartSignal === 'sell' ? 'danger' : 'info'
    },
    signalText() {
      return this.chartSignal === 'buy' ? '🟢 买入信号' : 
             this.chartSignal === 'sell' ? '🔴 卖出信号' : '⚪ 观望'
    }
  },
  watch: {
    klineData: {
      handler(val) { this.updateChart() },
      deep: true
    },
    chartData: {
      handler(val) { this.updateChart() },
      deep: true
    },
    indicators: {
      handler() { this.updateChart() },
      deep: true
    }
  },
  mounted() {
    this.initChart()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.chart) this.chart.dispose()
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chartContainer)
      this.chart.on('dataZoom', () => this.updateAiAnalysis())
      this.updateChart()
    },

    updateChart() {
      if (!this.chart) return
      
      let option = {}
      switch (this.chartType) {
        case 'kline': option = this.buildKlineOption(); break;
        case 'line': option = this.buildLineOption(); break;
        case 'bar': option = this.buildBarOption(); break;
        case 'pie': option = this.buildPieOption(); break;
        default: option = this.buildKlineOption();
      }
      
      this.chart.setOption(option, true)
      if (this.enableAi) this.updateAiAnalysis()
    },

    buildKlineOption() {
      if (!this.klineData || this.klineData.length === 0) return {}
      
      const dates = this.klineData.map(d => d.date)
      const ohlc = this.klineData.map(d => [d.open, d.close, d.low, d.high])
      const volumes = this.klineData.map(d => d.volume || 0)
      
      const series = [{
        name: 'K线',
        type: 'candlestick',
        data: ohlc,
        itemStyle: {
          color: '#ef232a',          // 涨 - 红
          color0: '#14b143',         // 跌 - 绿
          borderColor: '#ef232a',
          borderColor0: '#14b143',
        }
      }]
      
      // MA 均线
      if (this.indicators.ma) {
        series.push(...this.buildMA(dates, this.klineData))
      }
      
      // BOLL 布林带
      if (this.indicators.boll) {
        series.push(...this.buildBOLL(dates, this.klineData))
      }
      
      return {
        tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
        legend: { data: ['K线', 'MA5', 'MA10', 'MA20', 'MA60', 'BOLL', 'BOLL上轨', 'BOLL下轨'] },
        grid: [{ left: '10%', right: '8%', top: '15%', height: '50%' },
               { left: '10%', right: '8%', top: '70%', height: '15%' }],
        xAxis: [
          { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false } },
          { type: 'category', data: dates, gridIndex: 1 }
        ],
        yAxis: [
          { scale: true, gridIndex: 0 },
          { scale: true, gridIndex: 1, splitNumber: 2, axisLabel: { show: false } }
        ],
        dataZoom: [{ type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
                   { show: true, xAxisIndex: [0, 1], type: 'slider', top: '85%', start: 50, end: 100 }],
        series: [
          ...series,
          { name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: volumes,
            itemStyle: { color: (p) => this.klineData[p.dataIndex].close >= this.klineData[p.dataIndex].open ? '#ef232a' : '#14b143' } }
        ]
      }
    },

    buildLineOption() {
      const { categories, series: data } = this.chartData
      return {
        tooltip: { trigger: 'axis' },
        legend: { data: data.map(s => s.name) },
        grid: { left: '10%', right: '8%', top: '15%', bottom: '10%' },
        xAxis: { type: 'category', data: categories },
        yAxis: { type: 'value' },
        series: data.map(s => ({
          name: s.name, type: 'line', data: s.data, smooth: true,
          areaStyle: s.area ? { opacity: 0.3 } : null
        }))
      }
    },

    buildBarOption() {
      const { categories, series: data } = this.chartData
      return {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: data.map(s => s.name) },
        grid: { left: '10%', right: '8%', top: '15%', bottom: '10%' },
        xAxis: { type: 'category', data: categories },
        yAxis: { type: 'value' },
        series: data.map(s => ({ name: s.name, type: 'bar', data: s.data }))
      }
    },

    buildPieOption() {
      const { data } = this.chartData
      return {
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { orient: 'vertical', left: 'left' },
        series: [{ name: '占比', type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false,
          itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
          label: { show: false, position: 'center' },
          emphasis: { label: { show: true, fontSize: '20', fontWeight: 'bold' } },
          data: data }]
      }
    },

    buildMA(dates, klineData) {
      const calcMA = (period) => {
        const result = []
        for (let i = 0; i < klineData.length; i++) {
          if (i < period - 1) { result.push(null); continue }
          let sum = 0
          for (let j = 0; j < period; j++) sum += klineData[i - j].close
          result.push((sum / period).toFixed(2))
        }
        return result
      }
      
      return [
        { name: 'MA5', type: 'line', data: calcMA(5), smooth: true, lineStyle: { width: 1 } },
        { name: 'MA10', type: 'line', data: calcMA(10), smooth: true, lineStyle: { width: 1 } },
        { name: 'MA20', type: 'line', data: calcMA(20), smooth: true, lineStyle: { width: 1 } },
      ]
    },

    buildBOLL(dates, klineData) {
      const period = 20
      const boll = [], upper = [], lower = []
      
      for (let i = 0; i < klineData.length; i++) {
        if (i < period - 1) { boll.push(null); upper.push(null); lower.push(null); continue }
        const slice = klineData.slice(i - period + 1, i + 1).map(d => d.close)
        const ma = slice.reduce((a, b) => a + b, 0) / period
        const std = Math.sqrt(slice.reduce((sum, v) => sum + (v - ma) ** 2, 0) / period)
        boll.push(ma.toFixed(2))
        upper.push((ma + 2 * std).toFixed(2))
        lower.push((ma - 2 * std).toFixed(2))
      }
      
      return [
        { name: 'BOLL', type: 'line', data: boll, lineStyle: { width: 1, type: 'dashed' } },
        { name: 'BOLL上轨', type: 'line', data: upper, lineStyle: { width: 1 } },
        { name: 'BOLL下轨', type: 'line', data: lower, lineStyle: { width: 1 } },
      ]
    },

    updateAiAnalysis() {
      if (!this.enableAi || this.klineData.length < 20) return
      
      // 趋势分析
      const closes = this.klineData.map(d => d.close)
      const ma5 = this.avg(closes.slice(-5))
      const ma20 = this.avg(closes.slice(-20))
      
      let insight = ''
      if (ma5 > ma20 * 1.02) {
        insight = '当前处于上升趋势，5日均线在20日均线上方，短期动能较强'
        this.chartSignal = 'buy'
      } else if (ma5 < ma20 * 0.98) {
        insight = '当前处于下降趋势，5日均线在20日均线下方，短期动能较弱'
        this.chartSignal = 'sell'
      } else {
        insight = '当前处于震荡整理，均线交织，方向不明确'
        this.chartSignal = 'hold'
      }
      
      // 成交量分析
      const volumes = this.klineData.map(d => d.volume || 0)
      const avgVol = this.avg(volumes.slice(-5))
      const latestVol = volumes[volumes.length - 1]
      if (latestVol > avgVol * 1.5) {
        insight += '。成交量明显放大，需关注突破方向'
      }
      
      this.aiInsight = insight
    },

    toggleAiPanel() { this.showAiPanel = !this.showAiPanel },
    toggleIndicators() {
      this.indicators = {
        ma: !this.indicators.ma,
        macd: this.indicators.macd,
        rsi: this.indicators.rsi,
        boll: !this.indicators.boll
      }
    },
    exportChart() {
      if (!this.chart) return
      const url = this.chart.getDataURL({ type: 'png', pixelRatio: 2 })
      const a = document.createElement('a')
      a.href = url; a.download = `chart_${Date.now()}.png`; a.click()
    },
    fullscreen() {
      if (this.$refs.chartContainer.requestFullscreen) {
        this.$refs.chartContainer.requestFullscreen()
      }
    },
    handleResize() { if (this.chart) this.chart.resize() },
    avg(arr) { return arr.reduce((a, b) => a + b, 0) / arr.length },
  }
}
</script>

<style scoped>
.ai-smart-chart { position: relative; margin: 12px 0; }
.ai-float-panel {
  position: absolute; top: 12px; right: 12px;
  background: rgba(255,255,255,0.95); border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15); padding: 12px;
  z-index: 100; max-width: 300px;
  backdrop-filter: blur(10px);
}
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.panel-content .ai-text { font-size: 13px; color: #303133; margin: 0 0 8px 0; line-height: 1.5; }
.quick-actions { position: absolute; bottom: 8px; right: 8px; z-index: 50; }
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; }
.slide-fade-enter, .slide-fade-leave-to { transform: translateY(-10px); opacity: 0; }
</style>
