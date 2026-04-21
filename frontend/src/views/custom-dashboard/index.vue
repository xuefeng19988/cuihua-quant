<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📊 自定义仪表板</span><el-button size="mini" type="primary" style="float:right;" @click="saveConfig">💾 保存布局</el-button></div></el-card>
    <el-row :gutter="20">
      <el-col :span="24"><el-card shadow="hover"><div slot="header"><span>📈 市场概览</span></div><div style="height:200px;display:flex;align-items:center;justify-content:center;color:#909399;">市场概览图表区域</div></el-card></el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top:20px;">
      <el-col :span="12"><el-card shadow="hover"><div slot="header"><span>💰 持仓盈亏</span></div><div style="height:150px;display:flex;align-items:center;justify-content:center;color:#909399;">持仓盈亏图表区域</div></el-card></el-col>
      <el-col :span="12"><el-card shadow="hover"><div slot="header"><span>📜 最近交易</span></div><div style="height:150px;display:flex;align-items:center;justify-content:center;color:#909399;">最近交易表格区域</div></el-card></el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'CustomDashboard',
  data() { return { config: { widgets: [] } } },
  created() { this.fetchConfig() },
  methods: {
    async fetchConfig() {
      try { const { data } = await request.get('/custom-dashboard'); if (data.code === 200) this.config = data.data }
      catch (e) { this.$message.error('获取配置失败') }
    },
    async saveConfig() {
      try {
        await request.post('/custom-dashboard', this.config)
        this.$message.success('布局已保存')
      } catch (e) { this.$message.error('保存失败') }
    }
  }
}
</script>
