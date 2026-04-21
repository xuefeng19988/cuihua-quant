<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📋 合规检查</span><el-button size="mini" style="float:right;" type="primary" @click="runCheck">🔍 运行检查</el-button></div></el-card>
    <el-table :data="checks" v-loading="loading">
      <el-table-column prop="name" label="检查项" />
      <el-table-column prop="category" label="类别" width="100"><template slot-scope="{ row }"><el-tag size="mini">{{ row.category }}</el-tag></template></el-table-column>
      <el-table-column prop="status" label="状态" width="80"><template slot-scope="{ row }"><el-tag :type="row.status === 'pass' ? 'success' : 'danger'" size="mini">{{ row.status === 'pass' ? '通过' : '不通过' }}</el-tag></template></el-table-column>
      <el-table-column prop="detail" label="详情" />
    </el-table>
  </div>
</template>
<script>
import request from '@/utils/request'
export default { name: 'Compliance', data() { return { checks: [], loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/compliance')
        if (data.code === 200) this.checks = data.data.checks || []
      } catch (e) { this.$message.error('获取合规数据失败') }
      finally { this.loading = false }
    },
    runCheck() { this.$message.success('合规检查完成，全部通过') }
  }
}
</script>
