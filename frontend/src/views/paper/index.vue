<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>📝 模拟盘</span><el-tag size="mini" style="float:right;" :type="running ? 'success' : 'info'">{{ running ? '运行中' : '未启动' }}</el-tag></div>
      <el-button type="primary" size="small" @click="togglePaper">{{ running ? '暂停' : '启动' }}</el-button>
    </el-card>
    <el-row :gutter="20">
      <el-col :span="6" v-for="m in metrics" :key="m.label">
        <el-card shadow="hover"><div style="color:#909399;font-size:13px;">{{ m.label }}</div><div style="font-size:20px;font-weight:600;margin-top:8px;" :style="{color: m.color}">{{ m.value }}</div></el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top:20px;"><div slot="header"><span>📊 持仓明细</span></div>
      <el-table :data="positions" v-loading="loading">
        <el-table-column prop="code" label="代码" width="100" />
        <el-table-column prop="name" label="名称" width="80" />
        <el-table-column prop="shares" label="股数" width="80" />
        <el-table-column prop="cost" label="成本价" width="80" />
        <el-table-column prop="price" label="现价" width="80" />
        <el-table-column prop="pnl" label="盈亏"><template slot-scope="{ row }"><span :style="{color: row.pnl > 0 ? '#67C23A' : '#F56C6C'}">{{ row.pnl > 0 ? '+' : '' }}{{ row.pnl }}元</span></template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Paper',
  data() {
    return {
      running: true, loading: false,
      metrics: [
        { label: '总资产', value: '--', color: '#303133' },
        { label: '总收益', value: '--', color: '#303133' },
        { label: '收益率', value: '--', color: '#303133' },
        { label: '持仓数', value: '--', color: '#303133' }
      ],
      positions: []
    }
  },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/paper')
        if (data.code === 200) {
          const d = data.data
          this.running = d.running
          this.metrics[0].value = d.total_value ? d.total_value.toLocaleString() + '元' : '--'
          this.metrics[1].value = d.total_pnl ? (d.total_pnl > 0 ? '+' : '') + d.total_pnl.toLocaleString() + '元' : '--'
          this.metrics[2].value = d.return_pct ? d.return_pct + '%' : '--'
          this.metrics[3].value = d.holdings_count || '--'
          this.positions = d.positions || []
        }
      } catch (e) { this.$message.error('获取模拟盘数据失败') }
      finally { this.loading = false }
    },
    togglePaper() { this.$message.info(this.running ? '模拟盘已暂停' : '模拟盘已启动') }
  }
}
</script>
