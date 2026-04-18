<template>
  <div class="chart-container" ref="chart" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'RadarChart',
  props: {
    indicators: { type: Array, default: () => [] },
    data: { type: Array, default: () => [] },
    height: { type: Number, default: 300 },
    title: { type: String, default: '' }
  },
  data() { return { chart: null } },
  watch: {
    indicators() { this.updateChart() },
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
        tooltip: { trigger: 'item' },
        radar: {
          indicator: this.indicators,
          radius: '65%',
          center: ['50%', '55%'],
          axisName: { color: '#d1d4dc', fontSize: 12 },
          splitArea: { areaStyle: { color: ['rgba(26,26,46,0.8)', 'rgba(42,42,62,0.8)'] } },
          splitLine: { lineStyle: { color: '#2a2a3e' } },
          axisLine: { lineStyle: { color: '#2a2a3e' } }
        },
        series: [{
          type: 'radar',
          data: [{
            value: this.data,
            name: '风险指标',
            areaStyle: { color: 'rgba(64,158,255,0.3)' },
            lineStyle: { color: '#409EFF', width: 2 },
            itemStyle: { color: '#409EFF' }
          }]
        }]
      }
      this.chart.setOption(option, true)
    },
    onResize() { this.chart?.resize() }
  }
}
</script>
