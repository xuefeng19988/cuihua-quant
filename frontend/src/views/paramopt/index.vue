<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>⚙️ 参数优化</span></div></el-card>
    <el-form :model="form" label-width="120px" style="max-width:600px;">
      <el-form-item label="优化策略"><el-select v-model="form.strategy"><el-option v-for="s in strategies" :key="s" :label="s" :value="s" /></el-select></el-form-item>
      <el-form-item label="优化算法"><el-select v-model="form.algorithm"><el-option label="网格搜索" value="grid" /><el-option label="贝叶斯优化" value="bayesian" /><el-option label="遗传算法" value="genetic" /></el-select></el-form-item>
      <el-form-item label="迭代次数"><el-input-number v-model="form.iterations" :min="10" :max="1000" :step="10" /></el-form-item>
      <el-form-item><el-button type="primary" @click="startOptimize" :loading="running">🚀 开始优化</el-button></el-form-item>
    </el-form>
    <el-card v-if="results.length" style="margin-top:20px;"><div slot="header"><span>📊 优化结果</span></div>
      <el-table :data="results">
        <el-table-column prop="params" label="参数组合" />
        <el-table-column prop="return_pct" label="收益率" width="90"><template slot-scope="{ row }"><span :style="{color: row.return_pct > 0 ? '#67C23A' : '#F56C6C'}">{{ row.return_pct }}%</span></template></el-table-column>
        <el-table-column prop="sharpe" label="夏普" width="80" />
        <el-table-column prop="max_dd" label="回撤" width="80" />
      </el-table>
    </el-card>
  </div>
</template>
<script>
import request from '@/utils/request'
export default { name: 'ParamOpt', data() { return {
  form: { strategy: '多因子策略', algorithm: 'bayesian', iterations: 100 },
  strategies: [], running: false, results: []
}}, methods: {
  async startOptimize() {
    this.running = true
    try {
      const { data } = await request.post('/paramopt', this.form)
      if (data.code === 200) this.results = data.data.results || []
      this.$message.success('优化完成')
    } catch (e) { this.$message.error('优化失败') }
    finally { this.running = false }
  }
}, created() {
  request.get('/paramopt').then(({ data }) => { if (data.code === 200) this.strategies = data.data.strategies || [] })
}}
</script>
