<template>
  <div class="chart-container" ref="chart" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'
import { getThemeConfig } from '@/components/charts-enhanced/theme'

export default {
  name: 'BarChart',
  props: {
    data: { type: Array, default: () => [] },
    categories: { type: Array, default: () => [] },
    height: { type: Number, default: 300 },
    title: { type: String, default: '' },
    horizontal: { type: Boolean, default: false },
    darkTheme: { type: Boolean, default: true }
  },
  data() { return { chart: null } },
  watch: {
    data() { this.updateChart() },
    categories() { this.updateChart() },
    title() { this.updateChart() },
    darkTheme() { this.updateChart() }
  },
  mounted() { this.initChart() },
  beforeDestroy() { if (this.chart) this.chart.dispose() },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chart, null, { renderer: 'canvas' })
      this.updateChart()
      window.addEventListener('resize', this.onResize)
    },
    updateChart() {
      const theme = getThemeConfig(this.darkTheme)
      const option = {
        backgroundColor: theme.backgroundColor,
        title: { text: this.title, left: 'center', textStyle: { fontSize: 14, color: theme.textColor } },
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: theme.tooltipBackgroundColor, textStyle: { color: theme.tooltipTextColor } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: this.horizontal ? { type: 'value', axisLabel: { color: theme.textColor } } : { type: 'category', data: this.categories, axisLabel: { color: theme.textColor, rotate: 30 } },
        yAxis: this.horizontal ? { type: 'category', data: this.categories, axisLabel: { color: theme.textColor } } : { type: 'value', axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.splitLineColor } } },
        series: [{
          type: 'bar',
          data: this.data.map((v, i) => ({
            value: v,
            itemStyle: { color: v >= 0 ? theme.upColor : theme.downColor }
          })),
          barWidth: this.horizontal ? 20 : '60%'
        }]
      }
      this.chart.setOption(option, true)
    },
    onResize() { this.chart?.resize() }
  }
}
</script>
