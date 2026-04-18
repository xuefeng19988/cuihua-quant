<template>
  <div class="chart-container" ref="chart" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'
import 'echarts-wordcloud'

export default {
  name: 'WordCloud',
  props: {
    words: { type: Array, default: () => [] },
    height: { type: Number, default: 300 },
    title: { type: String, default: '' }
  },
  data() { return { chart: null } },
  watch: {
    words() { this.updateChart() },
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
      const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#ffeb3b', '#ff9800']
      const option = {
        title: { text: this.title, left: 'center', textStyle: { fontSize: 14, color: '#d1d4dc' } },
        tooltip: { show: true, formatter: p => `${p.data.name}: ${p.data.value}` },
        series: [{
          type: 'wordCloud',
          gridSize: 10,
          sizeRange: [12, 50],
          rotationRange: [-45, 45],
          shape: 'circle',
          textStyle: {
            color: () => colors[Math.floor(Math.random() * colors.length)]
          },
          data: this.words
        }]
      }
      this.chart.setOption(option, true)
    },
    onResize() { this.chart?.resize() }
  }
}
</script>
