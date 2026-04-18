<template>
  <div class="chart-container" ref="chart" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'
import { getThemeConfig } from '@/components/charts-enhanced/theme'

export default {
  name: 'PieChart',
  props: {
    data: { type: Array, default: () => [] },
    height: { type: Number, default: 300 },
    title: { type: String, default: '' },
    showLabel: { type: Boolean, default: true },
    darkTheme: { type: Boolean, default: true }
  },
  data() { return { chart: null } },
  watch: {
    data() { this.updateChart() },
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
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', backgroundColor: theme.tooltipBackgroundColor, textStyle: { color: theme.tooltipTextColor } },
        legend: { orient: 'vertical', left: 'left', top: 'middle', textStyle: { color: theme.textColor } },
        series: [{
          type: 'pie',
          radius: this.showLabel ? '50%' : ['40%', '70%'],
          center: ['50%', '50%'],
          data: this.data,
          label: { show: this.showLabel, formatter: '{b}: {d}%', color: theme.textColor },
          itemStyle: { borderRadius: 4 }
        }]
      }
      this.chart.setOption(option, true)
    },
    onResize() { this.chart?.resize() }
  }
}
</script>
