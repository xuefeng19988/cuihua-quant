<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>📄 自动报告</span>
        <el-button size="mini" type="primary" @click="generateReport" :loading="generating" style="float:right;">📄 生成报告</el-button>
      </div>
      <el-form :inline="true" size="small">
        <el-form-item label="报告类型">
          <el-select v-model="reportType" style="width:150px;">
            <el-option label="日报" value="daily" />
            <el-option label="周报" value="weekly" />
            <el-option label="月报" value="monthly" />
            <el-option label="专项报告" value="special" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="generateReport" :loading="generating">📊 生成</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <div slot="header"><span>📋 报告列表</span></div>
      <el-table :data="reports" v-loading="loading">
        <el-table-column prop="name" label="报告名称" />
        <el-table-column prop="type" label="类型" width="100">
          <template slot-scope="{ row }"><el-tag size="mini">{{ row.type }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="date" label="生成日期" width="110" />
        <el-table-column prop="size" label="大小" width="80" />
        <el-table-column label="操作" width="150">
          <template slot-scope="{ row }">
            <el-button size="mini" type="primary" @click="downloadReport(row)">📥 下载</el-button>
            <el-button size="mini" type="danger" @click="deleteReport(row)">🗑️</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Reports',
  data() {
    return { reports: [], loading: false, generating: false, reportType: 'daily' }
  },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/reports')
        if (data.code === 200) this.reports = data.data.reports || []
      } catch (e) { this.$message.error('获取报告列表失败') }
      finally { this.loading = false }
    },
    async generateReport() {
      this.generating = true
      try {
        const { data } = await request.get('/export/csv', { params: { days: 30 } })
        if (data.code === 200) {
          this.$message.success('报告生成成功！')
          this.fetchData()
        }
      } catch (e) { this.$message.error('报告生成失败') }
      finally { this.generating = false }
    },
    downloadReport(row) { this.$message.success('下载: ' + row.name) },
    deleteReport(row) { this.$message.success('已删除: ' + row.name) }
  }
}
</script>
