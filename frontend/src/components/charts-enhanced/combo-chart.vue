<template>
  <div class="combo-chart" :style="{ height: height + 'px' }">
    <enhanced-chart
      ref="chart"
      :height="height"
      :loading="loading"
      :empty="empty"
      :dark-theme="darkTheme"
      :show-toolbar="showToolbar"
      @click="onChartClick"
      @refresh="$emit('refresh')"
    />
  </div>
</template>

<script>
import EnhancedChart from './enhanced-chart.vue'
import * as echarts from 'echarts'

export default {
  name: 'ComboChart',
  components: { EnhancedChart },
  props: {
    height: { type: Number, default: 400 },
    loading: { type: Boolean, default: false },
    empty: { type: Boolean, default: false },
    darkTheme: { type: Boolean, default: true },
    showToolbar: { type: Boolean, default: true },
    categories: { type: Array, default: () => [] },
    series: { type: Array, default: () => [] },
    title: { type: String, default: '' }
  },
  watch: {
    categories() { this.updateChart() },
    series: { deep: true, handler() { this.updateChart() } },
    title() { this.updateChart() }
  },
  mounted() { this.updateChart() },
  methods: {
    updateChart() {
      const chart = this.$refs.chart
      if (!chart) return

      const theme = this.darkTheme ? {
        textColor: '#d1d4dc',
        splitLine: '#2a2a3e'
      } : {
        textColor: '#333333',
        splitLine: '#f0f0f0'
      }

      const option = {
        title: { text: this.title, left: 'center', textStyle: { fontSize: 14, color: theme.textColor } },
        tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
        legend: { data: this.series.map(s => s.name), top: 25, textStyle: { color: theme.textColor } },
        grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
        xAxis: { type: 'category', data: this.categories, axisLabel: { color: theme.textColor } },
        yAxis: this.series.map((s, i) => ({
          type: s.yAxisType || 'value',
          name: s.yAxisName || '',
          position: i === 0 ? 'left' : 'right',
          axisLabel: { color: theme.textColor },
          splitLine: { lineStyle: { color: theme.splitLine } }
        })),
        series: this.series.map(s => ({
          type: s.type || 'line',
          name: s.name,
          data: s.data,
          yAxisIndex: s.yAxisIndex || 0,
          smooth: s.smooth !== false,
          lineStyle: { width: s.lineWidth || 2 },
          itemStyle: { color: s.color },
          areaStyle: s.showArea ? { color: s.color, opacity: 0.3 } : undefined
        }))
      }

      chart.setOption(option, true)
    },
    onChartClick(params) {
      this.$emit('click', params)
    }
  }
}
</script>

<style scoped>
.combo-chart {
  width: 100%;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}
</style>
