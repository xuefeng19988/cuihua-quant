<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📋 日志分析</span></div></el-card>
    <el-row :gutter="20">
      <el-col :span="8"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;">总日志数</div><div style="font-size:24px;font-weight:600;">{{ data.total_logs }}</div></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;">错误数</div><div style="font-size:24px;font-weight:600;color:#F56C6C;">{{ data.error_count }}</div></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;">警告数</div><div style="font-size:24px;font-weight:600;color:#E6A23C;">{{ data.warning_count }}</div></el-card></el-col>
    </el-row>
    <el-card style="margin-top:20px;"><div slot="header"><span>🔴 最近错误</span></div>
      <el-table :data="data.recent_errors"><el-table-column prop="time" label="时间" /><el-table-column prop="level" label="级别" /><el-table-column prop="message" label="消息" /></el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'LogAnalyzer', data() { return { data: { total_logs: 0, error_count: 0, warning_count: 0, recent_errors: [] } } },
  created() { this.fetchData() },
  methods: {
    async fetchData() { try { const { data } = await request.get('/log-analyzer'); if (data.code === 200) this.data = data.data } catch (e) {} }
  }
}
</script>
