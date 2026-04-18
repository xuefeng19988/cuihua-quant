<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>⚙️ 参数优化</span></div></el-card>
    <el-form :model="form" label-width="120px" style="max-width:600px;">
      <el-form-item label="优化策略"><el-select v-model="form.strategy"><el-option v-for="s in strategies" :key="s" :label="s" :value="s" /></el-select></el-form-item>
      <el-form-item label="优化算法"><el-select v-model="form.algorithm"><el-option label="网格搜索" value="grid" /><el-option label="贝叶斯优化" value="bayesian" /><el-option label="遗传算法" value="genetic" /></el-select></el-form-item>
      <el-form-item label="迭代次数"><el-input-number v-model="form.iterations" :min="10" :max="1000" :step="10" /></el-form-item>
      <el-form-item><el-button type="primary" @click="startOptimize" :loading="running">🚀 开始优化</el-button></el-form-item>
    </el-form>
    <el-card v-if="results.length"><div slot="header"><span>📊 优化结果</span></div>
      <el-table :data="results" style="width:100%">
        <el-table-column prop="params" label="参数组合" />
        <el-table-column prop="return_pct" label="收益率" width="90"><template slot-scope="{ row }"><span :style="{color: row.return_pct > 0 ? '#67C23A' : '#F56C6C'}">{{ row.return_pct }}%</span></template></el-table-column>
        <el-table-column prop="sharpe" label="夏普" width="80" />
        <el-table-column prop="max_dd" label="回撤" width="80" />
      </el-table>
    </el-card>
  </div>
</template>
<script>
export default { name: 'ParamOpt', data() { return {
  form: { strategy: '多因子策略', algorithm: 'bayesian', iterations: 100 },
  running: false,
  strategies: ['多因子策略', '动量策略', '均值回归策略'],
  results: []
}}, methods: {
  startOptimize() {
    this.running = true
    setTimeout(() => {
      this.results = [
        { params: 'window=20, threshold=0.05', return_pct: 12.3, sharpe: 1.45, max_dd: -6.2 },
        { params: 'window=15, threshold=0.03', return_pct: 10.8, sharpe: 1.32, max_dd: -7.1 },
        { params: 'window=30, threshold=0.08', return_pct: 9.5, sharpe: 1.18, max_dd: -5.8 }
      ]
      this.running = false
      this.$message.success('优化完成')
    }, 2000)
  }
}}
</script>
