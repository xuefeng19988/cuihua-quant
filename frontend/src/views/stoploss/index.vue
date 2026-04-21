<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>🛑 智能止损</span></div></el-card>
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card><div slot="header"><span>📋 止损规则</span></div>
          <el-table :data="rules" v-loading="loading">
            <el-table-column prop="name" label="规则名称" />
            <el-table-column prop="type" label="类型" width="80"><template slot-scope="{ row }"><el-tag size="mini">{{ row.type }}</el-tag></template></el-table-column>
            <el-table-column prop="threshold" label="触发阈值" width="100" />
            <el-table-column prop="action" label="动作" width="70" />
            <el-table-column prop="enabled" label="状态" width="80"><template slot-scope="{ row }"><el-switch v-model="row.enabled" /></template></el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card><div slot="header"><span>📊 止损统计</span></div>
          <el-statistic title="今日触发" :value="stats.today_triggers" />
          <el-statistic title="累计触发" :value="stats.total_triggers" style="margin-top:16px;" />
          <el-statistic title="避免损失" :value="stats.avoided_loss" suffix="元" :precision="0" style="margin-top:16px;" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script>
import request from '@/utils/request'
export default { name: 'StopLoss', data() { return { rules: [], stats: {}, loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/stoploss')
        if (data.code === 200) { this.rules = data.data.rules || []; this.stats = data.data.stats || {} }
      } catch (e) { this.$message.error('获取止损数据失败') }
      finally { this.loading = false }
    }
  }
}
</script>
