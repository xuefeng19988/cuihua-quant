<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>🧮 因子研究</span>
        <el-tag size="mini" style="float:right;">{{ factors.length }} 个因子族</el-tag>
      </div>
    </el-card>
    <el-card>
      <el-table :data="factors" style="width: 100%">
        <el-table-column prop="name" label="因子族" width="130" />
        <el-table-column prop="desc" label="描述" />
        <el-table-column prop="count" label="因子数" width="90" />
        <el-table-column prop="status" label="状态" width="90">
          <template slot-scope="{ row }"><el-tag :type="row.status === 'active' ? 'success' : 'info'" size="mini">{{ row.status === 'active' ? '启用' : '停用' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Factors',
  data() { return { factors: [] } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try {
        const { data } = await request.get('/api/factors')
        if (data.code === 200) this.factors = data.data.list || []
      } catch (e) { this.$message.error('获取因子数据失败') }
    }
  }
}
</script>
