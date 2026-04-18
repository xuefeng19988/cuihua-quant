<template>
  <div class="animated-chart" ref="chartRef" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'
import { getThemeConfig } from './theme'

/**
 * 动画图表组件
 * 支持平滑过渡动画和数据更新动画
 */
export default {
  name: 'AnimatedChart',
  props: {
    type: { type: String, default: 'line' }, // line/bar/pie/scatter/radar
    data: { type: [Array, Object], default: () => [] },
    categories: { type: Array, default: () => [] },
    height: { type: Number, default: 300 },
    title: { type: String, default: '' },
    darkTheme: { type: Boolean, default: true },
    animation: { type: Boolean, default: true },
    animationDuration: { type: Number, default: 1000 }
  },
  data() { return { chart: null, prevData: null } },
  watch: {
    data: { deep: true, handler() { this.updateWithAnimation() } },
    categories() { this.updateWithAnimation() },
    darkTheme() { this.updateTheme() }
  },
  mounted() { this.initChart() },
  beforeDestroy() { if (this.chart) this.chart.dispose() },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chartRef)
      this.updateChart(true)
      window.addEventListener('resize', this.resize)
    },
    
    /**
     * 带动画更新图表
     */
    updateWithAnimation() {
      this.updateChart(false, true)
    },
    
    /**
     * 更新图表
     */
    updateChart(init = false, animate = false) {
      if (!this.chart) return
      
      const theme = getThemeConfig(this.darkTheme)
      const option = this.buildOption(theme)
      
      if (animate && !init) {
        // 使用动画更新
        this.chart.setOption(option, {
          notMerge: false,
          lazyUpdate: false,
          animation: this.animation,
          animationDuration: this.animationDuration,
          animationEasing: 'cubicOut'
        })
      } else {
        this.chart.setOption(option, true)
      }
      
      this.prevData = JSON.parse(JSON.stringify(this.data))
    },
    
    /**
     * 构建图表配置
     */
    buildOption(theme) {
      const base = {
        backgroundColor: theme.backgroundColor,
        title: { text: this.title, left: 'center', textStyle: { fontSize: 14, color: theme.textColor } },
        tooltip: {
          trigger: this.type === 'pie' ? 'item' : 'axis',
          backgroundColor: theme.tooltipBackgroundColor,
          textStyle: { color: theme.tooltipTextColor },
          axisPointer: { type: 'cross' }
        },
        animation: this.animation,
        animationDuration: this.animationDuration
      }
      
      switch(this.type) {
        case 'line':
          return { ...base, ...this.buildLineOption(theme) }
        case 'bar':
          return { ...base, ...this.buildBarOption(theme) }
        case 'pie':
          return { ...base, ...this.buildPieOption(theme) }
        case 'scatter':
          return { ...base, ...this.buildScatterOption(theme) }
        case 'radar':
          return { ...base, ...this.buildRadarOption(theme) }
        default:
          return base
      }
    },
    
    buildLineOption(theme) {
      return {
        grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
        xAxis: { type: 'category', data: this.categories, axisLabel: { color: theme.textColor } },
        yAxis: { type: 'value', axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.splitLineColor } } },
        series: Array.isArray(this.data) ? this.data.map((d, i) => ({
          type: 'line',
          name: d.name || `系列${i+1}`,
          data: d.data || d,
          smooth: true,
          lineStyle: { width: d.lineWidth || 2 },
          itemStyle: { color: d.color || theme.seriesColors[i % theme.seriesColors.length] },
          areaStyle: d.showArea ? { color: d.color || theme.seriesColors[i % theme.seriesColors.length], opacity: 0.3 } : undefined
        })) : [{ type: 'line', data: this.data, smooth: true, itemStyle: { color: theme.seriesColors[0] } }]
      }
    },
    
    buildBarOption(theme) {
      return {
        grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
        xAxis: { type: 'category', data: this.categories, axisLabel: { color: theme.textColor } },
        yAxis: { type: 'value', axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.splitLineColor } } },
        series: [{
          type: 'bar',
          data: this.data.map((v, i) => ({
            value: v,
            itemStyle: { color: v >= 0 ? theme.upColor : theme.downColor }
          })),
          animationDelay: (idx) => idx * 10
        }]
      }
    },
    
    buildPieOption(theme) {
      return {
        legend: { orient: 'vertical', left: 'left', textStyle: { color: theme.textColor } },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          data: this.data,
          label: { formatter: '{b}: {d}%', color: theme.textColor },
          itemStyle: { borderRadius: 4 },
          animationType: 'expansion',
          animationEasing: 'elasticOut'
        }]
      }
    },
    
    buildScatterOption(theme) {
      return {
        grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
        xAxis: { name: 'X', axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.splitLineColor } } },
        yAxis: { name: 'Y', axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.splitLineColor } } },
        series: [{
          type: 'scatter',
          data: this.data,
          symbolSize: d => Math.max(10, Math.sqrt(d[2] || 1) * 5),
          itemStyle: { color: theme.seriesColors[0] }
        }]
      }
    },
    
    buildRadarOption(theme) {
      return {
        radar: {
          indicator: this.data.indicators || [],
          radius: '65%',
          axisName: { color: theme.textColor }
        },
        series: [{
          type: 'radar',
          data: [{
            value: this.data.values || [],
            name: this.data.name || '数据',
            areaStyle: { color: theme.seriesColors[0], opacity: 0.3 },
            lineStyle: { color: theme.seriesColors[0] }
          }]
        }]
      }
    },
    
    updateTheme() {
      this.updateChart(false, this.animation)
    },
    
    resize() {
      this.chart?.resize()
    },
    
    /**
     * 导出图表
     */
    exportChart(type = 'png') {
      const url = this.chart.getDataURL({
        type,
        pixelRatio: 2,
        backgroundColor: this.darkTheme ? '#1a1a2e' : '#ffffff'
      })
      const link = document.createElement('a')
      link.download = `chart_${Date.now()}.${type}`
      link.href = url
      link.click()
    },
    
    /**
     * 获取图表实例
     */
    getInstance() {
      return this.chart
    }
  }
}
</script>
