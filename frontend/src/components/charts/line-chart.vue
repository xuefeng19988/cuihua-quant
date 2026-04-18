<template>
  <div class="chart-container" ref="chart" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'LineChart',
  props: {
    categories: { type: Array, default: () => [] },
    series: { type: Array, default: () => [] },
    height: { type: Number, default: 300 },
    title: { type: String, default: '' },
    showArea: { type: Boolean, default: false }
  },
  data() { return { chart: null } },
  watch: {
    categories() { this.updateChart() },
    series: { deep: true, handler() { this.updateChart() } },
    title() { this.updateChart() }
  },
  mounted() { this.initChart() },
  beforeDestroy() { if (this.chart) this.chart.dispose() },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chart)
      this.updateChart()
      window.addEventListener('resize', this.onResize)
    },
    updateChart() {
      const option = {
        title: { text: this.title, left: 'center', textStyle: { fontSize: 14, color: '#d1d4dc' } },
        tooltip: { trigger: 'axis' },
        legend: { data: this.series.map(s => s.name), top: 25, textStyle: { color: '#d1d4dc' } },
        grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
        xAxis: { type: 'category', data: this.categories, axisLabel: { color: '#d1d4dc' } },
        yAxis: { type: 'value', axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
        series: this.series.map(s => ({
          type: 'line',
          name: s.name,
          data: s.data,
          smooth: true,
          lineStyle: { width: s.width || 2 },
          itemStyle: { color: s.color },
          areaStyle: this.showArea ? { color: s.color, opacity: 0.3 } : undefined
        }))
      }
      this.chart.setOption(option, true)
    },
    onResize() { this.chart?.resize() }
  }
}
</script>
