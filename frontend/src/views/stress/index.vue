<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>🔥 压力测试</span><el-button size="mini" style="float:right;" type="danger" @click="runStress">🚨 开始测试</el-button></div></el-card>
    <el-row :gutter="20">
      <el-col :span="8" v-for="s in scenarios" :key="s.name">
        <el-card shadow="hover">
          <div style="font-weight:600;margin-bottom:8px;">{{ s.name }}</div>
          <div style="color:#909399;font-size:12px;margin-bottom:12px;">{{ s.desc }}</div>
          <el-progress :percentage="s.impact" :color="s.color" :stroke-width="8" />
          <div style="margin-top:8px;font-size:13px;">组合影响: <span :style="{color: s.color, fontWeight:600}">{{ s.impact }}%</span></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script>
import request from '@/utils/request'
export default { name: 'Stress', data() { return { scenarios: [] } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try {
        const { data } = await request.get('/stress')
        if (data.code === 200) this.scenarios = data.data.scenarios || []
      } catch (e) { this.$message.error('获取压力测试数据失败') }
    },
    runStress() { this.$message.warning('压力测试运行中...') }
  }
}
</script>
