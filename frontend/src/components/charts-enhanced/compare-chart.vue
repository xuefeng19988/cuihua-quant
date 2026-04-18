<template>
  <div class="compare-chart" :style="{ height: height + 'px' }">
    <enhanced-chart
      ref="chart"
      :height="height"
      :loading="loading"
      :dark-theme="darkTheme"
      :show-toolbar="showToolbar"
      @click="onChartClick"
    />
  </div>
</template>

<script>
import EnhancedChart from './enhanced-chart.vue'

export default {
  name: 'CompareChart',
  components: { EnhancedChart },
  props: {
    height: { type: Number, default: 400 },
    loading: { type: Boolean, default: false },
    darkTheme: { type: Boolean, default: true },
    showToolbar: { type: Boolean, default: true },
    stocks: { type: Array, default: () => [] },
    categories: { type: Array, default: () => [] },
    type: { type: String, default: 'price' } // price/change/compare
  },
  watch: {
    stocks: { deep: true, handler() { this.updateChart() } },
    categories() { this.updateChart() },
    type() { this.updateChart() }
  },
  mounted() { this.updateChart() },
  methods: {
    updateChart() {
      const chart = this.$refs.chart
      if (!chart || this.stocks.length === 0) return

      const theme = this.darkTheme ? {
        textColor: '#d1d4dc',
        splitLine: '#2a2a3e'
      } : {
        textColor: '#333333',
        splitLine: '#f0f0f0'
      }

      const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#ffeb3b']
      
      let series = []
      if (this.type === 'price') {
        series = this.stocks.map((stock, i) => ({
          name: stock.name,
          type: 'line',
          data: stock.data,
          smooth: true,
          lineStyle: { width: 2 },
          itemStyle: { color: colors[i % colors.length] }
        }))
      } else if (this.type === 'change') {
        // 涨跌幅对比 (归一化到0点)
        series = this.stocks.map((stock, i) => {
          const basePrice = stock.data[0]
          const normalizedData = stock.data.map(v => ((v - basePrice) / basePrice * 100).toFixed(2))
          return {
            name: stock.name,
            type: 'line',
            data: normalizedData,
            smooth: true,
            lineStyle: { width: 2 },
            itemStyle: { color: colors[i % colors.length] },
            areaStyle: { color: colors[i % colors.length], opacity: 0.1 }
          }
        })
      }

      const option = {
        title: { text: this.type === 'price' ? '价格对比' : '涨跌幅对比', left: 'center', textStyle: { fontSize: 14, color: theme.textColor } },
        tooltip: { trigger: 'axis' },
        legend: { data: this.stocks.map(s => s.name), top: 25, textStyle: { color: theme.textColor } },
        grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
        xAxis: { type: 'category', data: this.categories, axisLabel: { color: theme.textColor } },
        yAxis: {
          type: this.type === 'change' ? 'value' : 'value',
          axisLabel: {
            color: theme.textColor,
            formatter: this.type === 'change' ? '{value}%' : undefined
          },
          splitLine: { lineStyle: { color: theme.splitLine } }
        },
        series: series
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
.compare-chart {
  width: 100%;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}
</style>
