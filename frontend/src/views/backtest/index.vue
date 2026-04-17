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
        <el-form-item label="资金"><el-input-number v-model="form.capital" :step="100000" /></el-form-item>
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
      <div ref="chart" style="width:100%;height:400px;"></div>
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
      loading: false, result: null, metrics: []
    }
  },
  methods: {
    runBacktest() {
      this.loading = true
      // Simulate backtest result
      setTimeout(() => {
        this.loading = false
        this.result = { total_return: 23.5, annual: 11.2, sharpe: 1.35, max_dd: -8.2, win_rate: 58.3, profit_factor: 1.68 }
        this.metrics = [
          { label: '总收益率', value: '+23.5%', color: '#67C23A' },
          { label: '年化收益', value: '+11.2%', color: '#67C23A' },
          { label: '夏普比率', value: '1.35', color: '#409EFF' },
          { label: '最大回撤', value: '-8.2%', color: '#F56C6C' },
          { label: '胜率', value: '58.3%', color: '#409EFF' },
          { label: '盈亏比', value: '1.68', color: '#67C23A' }
        ]
        this.renderChart()
      }, 1500)
    },
    renderChart() {
      const chart = echarts.init(this.$refs.chart)
      const dates = [], values = []
      let v = 100
      for (let i = 0; i < 250; i++) {
        dates.push(`2025-${String(Math.floor(i/22)+1).padStart(2,'0')}-${String(i%22+1).padStart(2,'0')}`)
        v += (Math.random() - 0.45) * 2
        values.push(v.toFixed(2))
      }
      chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { data: dates },
        yAxis: { scale: true },
        series: [{ type: 'line', data: values, smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#409EFF' } }]
      })
    }
  }
}
</script>
