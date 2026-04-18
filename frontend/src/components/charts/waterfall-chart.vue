<template>
  <div class="chart-container" ref="chart" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'WaterfallChart',
  props: {
    data: { type: Array, default: () => [] },
    height: { type: Number, default: 300 },
    title: { type: String, default: '' }
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
      const categories = this.data.map(d => d.name)
      const values = this.data.map(d => d.value)
      
      // 计算辅助数据
      const transparent = []
      let cumulative = 0
      values.forEach((v, i) => {
        if (v >= 0) {
          transparent.push(cumulative)
          cumulative += v
        } else {
          cumulative += v
          transparent.push(cumulative)
        }
      })
      
      const option = {
        title: { text: this.title, left: 'center', textStyle: { fontSize: 14, color: '#d1d4dc' } },
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: p => `${p[0].name}: ${p[0].value > 0 ? '+' : ''}${p[0].value.toFixed(2)}` },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
        xAxis: { type: 'category', data: categories, axisLabel: { color: '#d1d4dc', rotate: 30 } },
        yAxis: { type: 'value', axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
        series: [
          { name: '辅助', type: 'bar', stack: 'total', itemStyle: { borderColor: 'transparent', color: 'transparent' }, emphasis: { itemStyle: { borderColor: 'transparent', color: 'transparent' } }, data: transparent },
          { name: '值', type: 'bar', stack: 'total', data: values.map(v => ({ value: Math.abs(v), itemStyle: { color: v >= 0 ? '#26a69a' : '#ef5350' } })) }
        ]
      }
      this.chart.setOption(option, true)
    },
    onResize() { this.chart?.resize() }
  }
}
</script>
