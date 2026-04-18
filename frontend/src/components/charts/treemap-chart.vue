<template>
  <div class="chart-container" ref="chart" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'TreemapChart',
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
      const option = {
        title: { text: this.title, left: 'center', textStyle: { fontSize: 14, color: '#d1d4dc' } },
        tooltip: { formatter: p => `${p.name}: ${p.value}` },
        series: [{
          type: 'treemap',
          data: this.data,
          leafDepth: 1,
          levels: [
            { itemStyle: { borderColor: '#1a1a2e', borderWidth: 3, gapWidth: 3 }, upperLabel: { show: true, color: '#d1d4dc', fontSize: 14 } },
            { itemStyle: { borderColor: '#1a1a2e', borderWidth: 2, gapWidth: 2 }, label: { show: true, fontSize: 12, color: '#fff' } }
          ],
          itemStyle: { borderRadius: 4 }
        }]
      }
      this.chart.setOption(option, true)
    },
    onResize() { this.chart?.resize() }
  }
}
</script>
