<template>
  <div class="chart-container" ref="chart" :style="{ height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'PieChart',
  props: {
    data: { type: Array, default: () => [] },
    height: { type: Number, default: 300 },
    title: { type: String, default: '' },
    showLabel: { type: Boolean, default: true }
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
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { orient: 'vertical', left: 'left', top: 'middle', textStyle: { color: '#d1d4dc' } },
        series: [{
          type: 'pie',
          radius: this.showLabel ? '50%' : ['40%', '70%'],
          center: ['50%', '50%'],
          data: this.data,
          label: { show: this.showLabel, formatter: '{b}: {d}%', color: '#d1d4dc' },
          itemStyle: { borderRadius: 4 }
        }]
      }
      this.chart.setOption(option, true)
    },
    onResize() { this.chart?.resize() }
  }
}
</script>
