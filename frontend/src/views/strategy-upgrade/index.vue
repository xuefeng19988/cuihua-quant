<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>🚀 策略回测升级</span></div></el-card>
    <el-card><div slot="header"><span>⚙️ 回测参数</span></div>
      <el-form :inline="true">
        <el-form-item label="滑点"><el-input-number v-model="form.slippage" :step="0.001" :min="0" :max="0.1" /></el-form-item>
        <el-form-item label="手续费"><el-input-number v-model="form.commission" :step="0.0001" :min="0" :max="0.01" /></el-form-item>
        <el-form-item><el-button type="primary" @click="runBacktest" :loading="loading">🚀 开始回测</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card v-if="results" style="margin-top:20px;"><div slot="header"><span>📊 回测结果</span></div>
      <el-row :gutter="20">
        <el-col :span="8" v-for="m in metrics" :key="m.label">
          <div style="text-align:center;padding:16px;background:#f5f7fa;border-radius:8px;margin-bottom:12px;">
            <div style="color:#909399;">{{ m.label }}</div>
            <div style="font-size:20px;font-weight:600;" :style="{color:m.color}">{{ m.value }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'StrategyUpgrade',
  data() { return { form: { slippage: 0.01, commission: 0.0003 }, loading: false, results: null } },
  computed: {
    metrics() {
      if (!this.results) return []
      const r = this.results
      return [
        { label: '总收益', value: r.total_return + '%', color: r.total_return > 0 ? '#67C23A' : '#F56C6C' },
        { label: '年化收益', value: r.annual_return + '%', color: '#409EFF' },
        { label: '最大回撤', value: r.max_drawdown + '%', color: '#F56C6C' },
        { label: '夏普比率', value: r.sharpe, color: r.sharpe > 1 ? '#67C23A' : '#E6A23C' },
        { label: '胜率', value: r.win_rate + '%', color: '#409EFF' },
        { label: '盈亏比', value: r.profit_loss_ratio, color: '#E6A23C' }
      ]
    }
  },
  methods: {
    async runBacktest() {
      this.loading = true
      try {
        const { data } = await request.post('/strategy/upgrade', this.form)
        if (data.code === 200) this.results = data.data.results
      } catch (e) { this.$message.error('回测失败') }
      finally { this.loading = false }
    }
  }
}
</script>
