<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>🔥 压力测试</span><el-button size="mini" style="float:right;" type="danger" @click="runStress">🚨 开始测试</el-button></div></el-card>
    <el-row :gutter="20">
      <el-col :span="8" v-for="s in scenarios" :key="s.name">
        <el-card shadow="hover">
          <div style="font-weight:600;margin-bottom:8px;">{{ s.icon }} {{ s.name }}</div>
          <div style="color:#909399;font-size:12px;margin-bottom:12px;">{{ s.desc }}</div>
          <el-progress :percentage="s.impact" :color="s.color" :stroke-width="8" />
          <div style="margin-top:8px;font-size:13px;">组合影响: <span :style="{color: s.color, fontWeight:600}">{{ s.impact }}%</span></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script>
export default { name: 'Stress', data() { return {
  scenarios: [
    { name: '市场暴跌', icon: '📉', desc: '大盘下跌 10%', impact: 12, color: '#F56C6C' },
    { name: '流动性危机', icon: '💧', desc: '成交量萎缩 50%', impact: 8, color: '#E6A23C' },
    { name: '黑天鹅事件', icon: '🦢', desc: '极端市场波动', impact: 20, color: '#F56C6C' },
    { name: '利率上调', icon: '📈', desc: '央行加息 50bp', impact: 5, color: '#67C23A' },
    { name: '行业政策风险', icon: '📋', desc: '行业监管收紧', impact: 7, color: '#E6A23C' },
    { name: '汇率波动', icon: '💱', desc: '人民币贬值 5%', impact: 4, color: '#67C23A' }
  ]
}}, methods: { runStress() { this.$message.warning('压力测试运行中...') } } }
</script>
