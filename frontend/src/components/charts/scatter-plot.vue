<template>
  <div class="chart-container" ref="chart" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'ScatterPlot',
  props: {
    data: { type: Array, default: () => [] },
    height: { type: Number, default: 300 },
    title: { type: String, default: '' },
    xAxisName: { type: String, default: 'X' },
    yAxisName: { type: String, default: 'Y' }
  },
  data() { return { chart: null } },
  watch: { data() { this.updateChart() }, title() { this.updateChart() } },
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
        tooltip: { formatter: p => `${p.data[3]}<br/>${this.xAxisName}: ${p.data[0]}<br/>${this.yAxisName}: ${p.data[1]}` },
        grid: { left: '3%', right: '8%', bottom: '3%', top: '15%', containLabel: true },
        xAxis: { name: this.xAxisName, nameLocation: 'middle', nameGap: 25, axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
        yAxis: { name: this.yAxisName, nameLocation: 'middle', nameGap: 35, axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
        series: [{
          type: 'scatter',
          data: this.data,
          symbolSize: d => Math.max(10, Math.sqrt(d[2]) * 5),
          itemStyle: { color: p => {
            const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
            return colors[p.dataIndex % colors.length]
          }},
          label: { show: true, formatter: p => p.data[3], position: 'top', fontSize: 10, color: '#d1d4dc' }
        }]
      }
      this.chart.setOption(option, true)
    },
    onResize() { this.chart?.resize() }
  }
}
</script>
