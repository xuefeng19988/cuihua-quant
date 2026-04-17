<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>⚡ 参数优化配置</span></div>
      <el-form :inline="true">
        <el-form-item label="策略"><el-select v-model="form.strategy" style="width: 150px;">
          <el-option label="SMA 交叉" value="sma" /><el-option label="动量策略" value="momentum" /><el-option label="多因子" value="multi_factor" />
        </el-select></el-form-item>
        <el-form-item label="优化方法"><el-select v-model="form.method" style="width: 150px;">
          <el-option label="网格搜索" value="grid" /><el-option label="贝叶斯优化" value="bayesian" /><el-option label="遗传算法" value="ga" />
        </el-select></el-form-item>
        <el-form-item label="目标函数"><el-select v-model="form.objective" style="width: 150px;">
          <el-option label="夏普比率" value="sharpe" /><el-option label="总收益" value="return" /><el-option label="Calmar 比率" value="calmar" />
        </el-select></el-form-item>
        <el-form-item><el-button type="primary" @click="$message.info('优化功能开发中')">🚀 开始优化</el-button></el-form-item>
      </el-form>
    </el-card>
  </div>
</template>
<script>
export default {
  name: 'ParamOpt',
  data() { return { form: { strategy: 'sma', method: 'grid', objective: 'sharpe' } } }
}
</script>
