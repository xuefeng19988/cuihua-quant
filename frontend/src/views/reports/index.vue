<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📄 报告生成</span><el-button size="mini" style="float:right;" type="primary" @click="generateReport">📄 生成报告</el-button></div></el-card>
    <el-table :data="reports" v-loading="loading">
      <el-table-column prop="name" label="报告名称" />
      <el-table-column prop="type" label="类型" width="100"><template slot-scope="{ row }"><el-tag size="mini">{{ row.type }}</el-tag></template></el-table-column>
      <el-table-column prop="date" label="生成日期" width="110" />
      <el-table-column prop="size" label="大小" width="80" />
      <el-table-column label="操作" width="100"><template slot-scope="{ row }"><el-button size="mini" type="primary">📥 下载</el-button></template></el-table-column>
    </el-table>
  </div>
</template>
<script>
import request from '@/utils/request'
export default { name: 'Reports', data() { return { reports: [], loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/reports')
        if (data.code === 200) this.reports = data.data.reports || []
      } catch (e) { this.$message.error('获取报告列表失败') }
      finally { this.loading = false }
    },
    generateReport() { this.$message.info('报告生成中，请稍候...') }
  }
}
</script>
