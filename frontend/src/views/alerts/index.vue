<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>🔔 告警中心</span>
        <el-tag size="mini" style="float:right;">{{ rules.length }} 条规则</el-tag>
      </div>
    </el-card>
    <el-card>
      <el-table :data="rules" style="width: 100%">
        <el-table-column prop="name" label="告警名称" width="130" />
        <el-table-column prop="type" label="类型" width="80">
          <template slot-scope="{ row }"><el-tag size="mini" type="info">{{ row.type }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="threshold" label="阈值" width="120" />
        <el-table-column prop="enabled" label="状态" width="80">
          <template slot-scope="{ row }">
            <el-switch v-model="row.enabled" active-color="#13ce66" inactive-color="#ff4949" @change="toggleRule(row)" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Alerts',
  data() { return { rules: [] } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try {
        const { data } = await request.get('/alerts')
        if (data.code === 200) this.rules = data.data.rules || []
      } catch (e) { this.$message.error('获取告警规则失败') }
    },
    toggleRule(row) {
      this.$message.success(`${row.name} 已${row.enabled ? '启用' : '停用'}`)
    }
  }
}
</script>
