<template>
  <div class="app-container">
    <el-card>
      <div slot="header">
        <span>📈 图表分析</span>
        <el-select v-model="form.indicators" multiple style="float:right;width:200px;" placeholder="选择指标">
          <el-option label="MA 均线" value="ma" />
          <el-option label="MACD" value="macd" />
          <el-option label="RSI" value="rsi" />
          <el-option label="布林带" value="boll" />
        </el-select>
      </div>
      <el-form :inline="true" style="margin-bottom: 16px;">
        <el-form-item label="股票"><el-select v-model="form.code" filterable placeholder="选择股票" style="width: 200px;">
          <el-option v-for="s in stocks" :key="s.value" :label="s.label" :value="s.value" />
        </el-select></el-form-item>
        <el-form-item label="周期"><el-select v-model="form.days" style="width: 100px;">
          <el-option label="30天" :value="30" /><el-option label="60天" :value="60" />
          <el-option label="90天" :value="90" /><el-option label="180天" :value="180" />
        </el-select></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData" :loading="loading">📊 生成图表</el-button></el-form-item>
      </el-form>
      <div ref="chart" style="width: 100%; height: 500px;" v-loading="loading"></div>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
export default {
  name: 'Charts',
  data() {
    return {
      form: { code: 'SZ.002594', days: 60, indicators: ['ma'] },
      stocks: [], loading: false, chart: null
    }
  },
  created() { this.fetchStocks(); this.fetchData() },
  methods: {
    fetchStocks() {
      var self = this
      fetch('/api/stocks?page=1').then(function(r) { return r.json() }).then(function(d) {
        if (d.code === 200) {
          self.stocks = (d.data.list || []).map(function(s) { return { value: s.code, label: s.code + ' ' + s.name } })
        }
      })
    },
    fetchData() {
      this.loading = true
      var self = this
      fetch('/api/charts?code=' + this.form.code + '&days=' + this.form.days)
        .then(function(r) { return r.json() })
        .then(function(d) {
          self.loading = false
          self.renderDemo()
        })
        .catch(function() { self.loading = false; self.renderDemo() })
    },
    renderDemo() {
      if (!this.chart) this.chart = echarts.init(this.$refs.chart)
      var dates = []
      var prices = []
      var volumes = []
      var p = 100 + Math.random() * 50
      var i
      for (i = 0; i < this.form.days; i++) {
        dates.push('2026-04-' + String(18 - this.form.days + i).padStart(2, '0'))
        p += (Math.random() - 0.5) * 4
        prices.push(parseFloat(p.toFixed(2)))
        volumes.push(Math.floor(Math.random() * 1000000))
      }
      var grad = { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
        { offset: 0, color: 'rgba(64,158,255,0.3)' },
        { offset: 1, color: 'rgba(64,158,255,0.05)' }
      ]}
      var ma5 = []
      var ma10 = []
      for (i = 0; i < prices.length; i++) {
        if (i >= 4) {
          var sum5 = 0
          for (var j = i - 4; j <= i; j++) sum5 += prices[j]
          ma5.push(parseFloat((sum5 / 5).toFixed(2)))
        } else {
          ma5.push(null)
        }
        if (i >= 9) {
          var sum10 = 0
          for (var k = i - 9; k <= i; k++) sum10 += prices[k]
          ma10.push(parseFloat((sum10 / 10).toFixed(2)))
        } else {
          ma10.push(null)
        }
      }
      var series = [{
        name: '收盘价', type: 'line', data: prices, smooth: true,
        itemStyle: { color: '#409EFF' }, areaStyle: { color: grad }
      }]
      if (this.form.indicators.indexOf('ma') >= 0) {
        series.push({ name: 'MA5', type: 'line', data: ma5, itemStyle: { color: '#F56C6C' }, symbol: 'none' })
        series.push({ name: 'MA10', type: 'line', data: ma10, itemStyle: { color: '#67C23A' }, symbol: 'none' })
      }
      this.chart.setOption({
        title: { text: this.form.code + ' K线图', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { bottom: 10, data: ['收盘价', 'MA5', 'MA10'] },
        xAxis: { data: dates },
        yAxis: { scale: true },
        series: series
      })
    }
  }
}
</script>
