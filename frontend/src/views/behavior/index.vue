<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>🧠 行为分析</span></div></el-card>
    <el-row :gutter="20">
      <el-col :span="8" v-for="b in behaviors" :key="b.name">
        <el-card shadow="hover"><div style="font-weight:600;margin-bottom:8px;">{{ b.icon }} {{ b.name }}</div>
          <el-progress :percentage="b.score" :color="b.color" :stroke-width="12" />
          <div style="color:#909399;font-size:12px;margin-top:8px;">{{ b.desc }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script>
export default { name: 'Behavior', data() { return {
  behaviors: [
    { name: '过度交易', icon: '🔄', score: 35, color: '#67C23A', desc: '交易频率适中' },
    { name: '损失厌恶', icon: '😰', score: 62, color: '#E6A23C', desc: '需注意止损纪律' },
    { name: '确认偏误', icon: '🔍', score: 28, color: '#67C23A', desc: '决策较客观' },
    { name: '锚定效应', icon: '⚓', score: 45, color: '#67C23A', desc: '价格判断较合理' },
    { name: '从众心理', icon: '👥', score: 55, color: '#E6A23C', desc: '有一定独立思考' },
    { name: '风险偏好', icon: '🎲', score: 70, color: '#F56C6C', desc: '风险偏好较高，注意控制' }
  ]
}}}
</script>
