<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>🔬 回测中心</span></div>
      <el-form :inline="true">
        <el-form-item label="策略"><el-select v-model="form.strategy" size="small"><el-option v-for="s in strategies" :key="s" :label="s" :value="s" /></el-select></el-form-item>
        <el-form-item label="开始"><el-date-picker v-model="form.start" type="date" size="small" value-format="yyyy-MM-dd" /></el-form-item>
        <el-form-item label="结束"><el-date-picker v-model="form.end" type="date" size="small" value-format="yyyy-MM-dd" /></el-form-item>
        <el-form-item label="资金"><el-input-number v-model="form.capital" :step="10000" :min="10000" size="small" style="width:120px;" /></el-form-item>
        <el-form-item><el-button size="small" type="primary" @click="runBacktest" :loading="loading">🚀 回测</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20" v-if="result">
      <el-col :span="6" v-for="m in metrics" :key="m.label">
        <el-card shadow="hover"><div style="color:#909399;font-size:13px;">{{ m.label }}</div><div style="font-size:20px;font-weight:600;margin-top:8px;" :style="{color:m.color}">{{ m.value }}</div></el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Backtest',
  data() {
    return {
      form: { strategy: '多因子策略', start: '2025-01-01', end: '2026-04-16', capital: 100000 },
      strategies: ['多因子策略', '动量策略', '均值回归策略'],
      result: null, metrics: [], loading: false
    }
  },
  methods: {
    async runBacktest() {
      this.loading = true
      try {
        const { data } = await request.post('/backtest', this.form)
        if (data.code === 200) {
          this.result = data.data
          const r = data.data
          this.metrics = [
            { label: '累计收益', value: r.return_pct ? r.return_pct + '%' : '--', color: r.return_pct > 0 ? '#67C23A' : '#F56C6C' },
            { label: '年化收益', value: r.annual_return ? r.annual_return + '%' : '--', color: '#303133' },
            { label: '夏普比率', value: r.sharpe || '--', color: '#303133' },
            { label: '最大回撤', value: r.max_dd ? r.max_dd + '%' : '--', color: '#F56C6C' }
          ]
        }
      } catch (e) { this.$message.error('回测失败: ' + e.message) }
      finally { this.loading = false }
    }
  }
}
</script>
