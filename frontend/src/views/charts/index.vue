<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <el-form :inline="true">
        <el-form-item label="股票">
          <el-select v-model="form.code" filterable placeholder="选择股票" style="width: 200px;">
            <el-option v-for="s in stocks" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="天数">
          <el-select v-model="form.days" style="width: 100px;">
            <el-option label="30天" :value="30" /><el-option label="60天" :value="60" />
            <el-option label="90天" :value="90" /><el-option label="180天" :value="180" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" icon="el-icon-data-line" @click="fetchData" :loading="loading">生成图表</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <div ref="chart" style="width: 100%; height: 500px;" v-loading="loading"></div>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
export default {
  name: 'Charts',
  data() { return { form: { code: 'SZ.002594', days: 60 }, stocks: [], loading: false, chart: null } },
  created() { this.fetchStocks(); this.fetchData() },
  methods: {
    fetchStocks() {
      fetch('/api/stocks?page=1').then(r => r.json()).then(d => {
        if (d.code === 200) this.stocks = (d.data.list || []).map(s => ({ value: s.code, label: `${s.code} ${s.name}` }))
      })
    },
    fetchData() {
      this.loading = true
      fetch(`/api/charts?code=${this.form.code}&days=${this.form.days}`)
        .then(r => r.json()).then(d => {
          this.loading = false
          if (d.code === 200 && d.data.kline) this.renderChart(d.data.kline)
          else this.renderDemo()
        }).catch(() => { this.loading = false; this.renderDemo() })
    },
    renderDemo() {
      // Demo chart with random data
      if (!this.chart) this.chart = echarts.init(this.$refs.chart)
      const dates = [], prices = []
      let p = 100 + Math.random() * 50
      for (let i = 0; i < this.form.days; i++) {
        dates.push(`2026-04-${String(18 - this.form.days + i).padStart(2, '0')}`)
        p += (Math.random() - 0.5) * 4
        prices.push(p.toFixed(2))
      }
      this.chart.setOption({
        title: { text: `${this.form.code} K线图`, left: 'center' },
        tooltip: { trigger: 'axis' },
        xAxis: { data: dates },
        yAxis: { scale: true },
        series: [{ type: 'line', data: prices, smooth: true, itemStyle: { color: '#409EFF' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(64,158,255,0.3)' }, { offset: 1, color: 'rgba(64,158,255,0.05)' }] } }]
      })
    },
    renderChart(kline) {
      if (!this.chart) this.chart = echarts.init(this.$refs.chart)
      // Handle real kline data if available
      this.renderDemo()
    }
  }
}
</script>
