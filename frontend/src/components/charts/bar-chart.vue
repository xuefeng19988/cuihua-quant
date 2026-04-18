<template>
  <div class="chart-container" ref="chart" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'BarChart',
  props: {
    data: { type: Array, default: () => [] },
    categories: { type: Array, default: () => [] },
    height: { type: Number, default: 300 },
    title: { type: String, default: '' },
    horizontal: { type: Boolean, default: false }
  },
  data() { return { chart: null } },
  watch: {
    data() { this.updateChart() },
    categories() { this.updateChart() },
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
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: this.horizontal ? { type: 'value', axisLabel: { color: '#d1d4dc' } } : { type: 'category', data: this.categories, axisLabel: { color: '#d1d4dc', rotate: 30 } },
        yAxis: this.horizontal ? { type: 'category', data: this.categories, axisLabel: { color: '#d1d4dc' } } : { type: 'value', axisLabel: { color: '#d1d4dc' } },
        series: [{
          type: 'bar',
          data: this.data.map((v, i) => ({
            value: v,
            itemStyle: { color: v >= 0 ? '#26a69a' : '#ef5350' }
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
