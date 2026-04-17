<template>
  <div class="app-container">
    <el-card>
      <div slot="header"><span>🧠 行为分析</span></div>
      <el-table :data="behaviors" style="width: 100%">
        <el-table-column prop="name" label="行为指标" />
        <el-table-column prop="desc" label="描述" />
        <el-table-column prop="value" label="当前值" width="100" />
        <el-table-column prop="suggestion" label="建议" />
      </el-table>
    </el-card>
  </div>
</template>
<script>
export default {
  name: 'Behavior',
  data() {
    return {
      behaviors: [
        { name: '过度交易', desc: '交易频率过高', value: '--', suggestion: '控制交易次数' },
        { name: '损失厌恶', desc: '亏损持仓过长', value: '--', suggestion: '严格执行止损' },
        { name: '确认偏误', desc: '只看支持信息', value: '--', suggestion: '多角度分析' },
        { name: '锚定效应', desc: '依赖初始价格', value: '--', suggestion: '动态调整预期' },
        { name: '羊群效应', desc: '跟随市场情绪', value: '--', suggestion: '独立思考' }
      ]
    }
  }
}
</script>
