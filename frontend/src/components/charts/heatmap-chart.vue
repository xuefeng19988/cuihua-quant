<template>
  <div class="chart-container" ref="chart" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'HeatmapChart',
  props: {
    data: { type: Array, default: () => [] },
    xAxis: { type: Array, default: () => [] },
    yAxis: { type: Array, default: () => [] },
    height: { type: Number, default: 400 },
    title: { type: String, default: '' }
  },
  data() { return { chart: null } },
  watch: {
    data() { this.updateChart() },
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
        tooltip: { position: 'top', formatter: p => `${this.xAxis[p.data[0]]} - ${this.yAxis[p.data[1]]}: ${p.data[2].toFixed(2)}` },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
        xAxis: { type: 'category', data: this.xAxis, splitArea: { show: true }, axisLabel: { color: '#d1d4dc', rotate: 30 } },
        yAxis: { type: 'category', data: this.yAxis, splitArea: { show: true }, axisLabel: { color: '#d1d4dc' } },
        visualMap: {
          min: -1, max: 1, calculable: true, orient: 'horizontal', left: 'center', bottom: '0%',
          inRange: { color: ['#ef5350', '#2a2a3e', '#26a69a'] },
          textStyle: { color: '#d1d4dc' }
        },
        series: [{
          type: 'heatmap',
          data: this.data,
          label: { show: true, fontSize: 10, color: '#fff' },
          itemStyle: { borderColor: '#1a1a2e', borderWidth: 2 }
        }]
      }
      this.chart.setOption(option, true)
    },
    onResize() { this.chart?.resize() }
  }
}
</script>
