<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📝 AI智能研报</span><el-button size="mini" type="primary" style="float:right;" @click="generateReport" :loading="loading">🤖 生成报告</el-button></div></el-card>
    <el-card v-if="report">
      <h2>{{ report.title }}</h2>
      <p style="color:#909399;">生成时间: {{ new Date(report.generated_at).toLocaleString('zh-CN') }}</p>
      <el-divider />
      <h3>📊 摘要</h3><p>{{ report.summary }}</p>
      <h3>📋 报告章节</h3>
      <el-tag v-for="s in report.sections" :key="s" style="margin:4px;">{{ s }}</el-tag>
      <el-divider />
      <p>评级: <el-tag type="success">{{ report.rating }}</el-tag> | 目标价: <strong>¥{{ report.target_price }}</strong></p>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'AIReports', data() { return { report: null, loading: false } },
  methods: {
    async generateReport() {
      this.loading = true
      try {
        const { data } = await request.post('/ai-report', { stock: '贵州茅台' })
        if (data.code === 200) this.report = data.data
      } catch (e) { this.$message.error('生成失败') }
      finally { this.loading = false }
    }
  }
}
</script>
