<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>📊 回测配置</span></div>
      <el-form :model="form" :inline="true">
        <el-form-item label="策略"><el-select v-model="form.strategy" style="width: 180px;">
          <el-option label="SMA 交叉" value="sma" /><el-option label="动量策略" value="momentum" />
          <el-option label="均值回归" value="mean_reversion" /><el-option label="多因子" value="multi_factor" />
        </el-select></el-form-item>
        <el-form-item label="开始"><el-date-picker v-model="form.start" type="date" value-format="yyyy-MM-dd" /></el-form-item>
        <el-form-item label="结束"><el-date-picker v-model="form.end" type="date" value-format="yyyy-MM-dd" /></el-form-item>
        <el-form-item label="资金"><el-input-number v-model="form.capital" :step="100000" :min="100000" /></el-form-item>
        <el-form-item><el-button type="primary" @click="runBacktest" :loading="loading">🚀 开始回测</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20" style="margin-bottom: 20px;" v-if="result">
      <el-col :span="6" v-for="item in metrics" :key="item.label">
        <el-card shadow="hover"><div style="color:#909399;font-size:13px;">{{ item.label }}</div>
          <div style="font-size:24px;font-weight:600;margin-top:8px;" :style="{color:item.color}">{{ item.value }}</div></el-card>
      </el-col>
    </el-row>

    <el-card v-if="result">
      <div slot="header"><span>📈 收益曲线</span></div>
      <div ref="chart" style="width:100%;height:400px;" v-loading="loading"></div>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
export default {
  name: 'Backtest',
  data() {
    return {
      form: { strategy: 'sma', start: '2024-01-01', end: '2026-04-18', capital: 1000000 },
      loading: false, result: null, metrics: [], chart: null
    }
  },
  methods: {
    runBacktest() {
      this.loading = true
      fetch('/api/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.form)
      })
      .then(r => r.json())
      .then(d => {
        this.loading = false
        if (d.code === 200) {
          this.result = d.data
          this.metrics = [
            { label: '总收益率', value: '+' + d.data.total_return + '%', color: d.data.total_return >= 0 ? '#67C23A' : '#F56C6C' },
            { label: '年化收益', value: '+' + d.data.annual_return + '%', color: d.data.annual_return >= 0 ? '#67C23A' : '#F56C6C' },
            { label: '夏普比率', value: d.data.sharpe, color: '#409EFF' },
            { label: '最大回撤', value: d.data.max_drawdown + '%', color: '#F56C6C' },
            { label: '胜率', value: d.data.win_rate + '%', color: '#67C23A' },
            { label: '盈亏比', value: d.data.profit_factor, color: '#67C23A' }
          ]
          this.renderChart(d.data.equity_curve, d.data.dates)
        }
      })
      .catch(() => { this.loading = false })
    },
    renderChart(values, dates) {
      if (!this.chart) this.chart = echarts.init(this.$refs.chart)
      this.chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { data: dates },
        yAxis: { scale: true },
        series: [{ type: 'line', data: values, smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#409EFF' } }]
      })
    }
  }
}
</script>