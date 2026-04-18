<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📋 合规检查</span><el-button size="mini" style="float:right;" type="primary" @click="runCheck">🔍 运行检查</el-button></div></el-card>
    <el-table :data="checks" style="width:100%">
      <el-table-column prop="name" label="检查项" />
      <el-table-column prop="category" label="类别" width="100"><template slot-scope="{ row }"><el-tag size="mini">{{ row.category }}</el-tag></template></el-table-column>
      <el-table-column prop="status" label="状态" width="80"><template slot-scope="{ row }"><el-tag :type="row.status === 'pass' ? 'success' : 'danger'" size="mini">{{ row.status === 'pass' ? '通过' : '不通过' }}</el-tag></template></el-table-column>
      <el-table-column prop="detail" label="详情" />
    </el-table>
  </div>
</template>
<script>
export default { name: 'Compliance', data() { return {
  checks: [
    { name: '单只股票持仓上限', category: '风控', status: 'pass', detail: '最大持仓 15%，符合规定' },
    { name: '行业集中度检查', category: '风控', status: 'pass', detail: '科技行业占比 28%，在阈值内' },
    { name: '日内交易频率', category: '交易', status: 'pass', detail: '本月日均交易 3.2 次' },
    { name: '数据源合规性', category: '数据', status: 'pass', detail: '所有数据源均已授权' },
    { name: '策略备案检查', category: '策略', status: 'pass', detail: '所有在用策略已备案' }
  ]
}}, methods: { runCheck() { this.$message.success('合规检查完成，全部通过') } } }
</script>
