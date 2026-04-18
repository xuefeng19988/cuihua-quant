<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📄 报告生成</span><el-button size="mini" style="float:right;" type="primary" @click="generateReport">📄 生成报告</el-button></div></el-card>
    <el-table :data="reports" style="width:100%">
      <el-table-column prop="name" label="报告名称" />
      <el-table-column prop="type" label="类型" width="100"><template slot-scope="{ row }"><el-tag size="mini">{{ row.type }}</el-tag></template></el-table-column>
      <el-table-column prop="date" label="生成日期" width="110" />
      <el-table-column prop="size" label="大小" width="80" />
      <el-table-column label="操作" width="100"><template slot-scope="{ row }"><el-button size="mini" type="primary">📥 下载</el-button></template></el-table-column>
    </el-table>
  </div>
</template>
<script>
export default { name: 'Reports', data() { return {
  reports: [
    { name: '2026年4月月度报告', type: '月度', date: '2026-04-16', size: '2.3MB' },
    { name: '2026年Q1季度报告', type: '季度', date: '2026-04-01', size: '5.1MB' },
    { name: '策略绩效评估报告', type: '专项', date: '2026-03-25', size: '1.8MB' }
  ]
}}, methods: { generateReport() { this.$message.info('报告生成中，请稍候...') } } }
</script>
