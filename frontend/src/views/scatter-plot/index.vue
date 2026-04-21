<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📊 散点图分析</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div></el-card>
    <el-card><div id="scatter-chart" style="width:100%;height:500px;"></div></el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'
export default {
  name: 'ScatterPlot', data() { return { loading: false, chart: null } },
  created() { this.fetchData() },
  mounted() { this.chart = echarts.init(document.getElementById('scatter-chart')); window.addEventListener('resize', () => this.chart?.resize()) },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/scatter-data')
        if (data.code === 200) this.renderChart(data.data.points)
      } catch (e) { this.$message.error('获取数据失败') }
      finally { this.loading = false }
    },
    renderChart(points) {
      const option = {
        tooltip: { formatter: p => `${p.data.label}<br/>X: ${p.data.x}<br/>Y: ${p.data.y}` },
        xAxis: { name: '风险', splitLine: { show: false } },
        yAxis: { name: '收益', splitLine: { show: false } },
        series: [{
          type: 'scatter',
          data: points.map(p => ({ value: [p.x, p.y], label: p.label })),
          symbolSize: p => p.data[2] || 20,
          itemStyle: { color: p => p.value[1] > 15 ? '#67C23A' : p.value[1] > 10 ? '#409EFF' : '#E6A23C' }
        }]
      }
      this.chart?.setOption(option, true)
    }
  }
}
</script>
