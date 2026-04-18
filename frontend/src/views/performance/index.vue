<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📊 绩效看板</span></div></el-card>
    <el-row :gutter="20">
      <el-col :span="6" v-for="m in metrics" :key="m.label">
        <el-card shadow="hover"><div style="color:#909399;font-size:13px;">{{ m.label }}</div><div style="font-size:20px;font-weight:600;margin-top:8px;" :style="{color:m.color}">{{ m.value }}</div></el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top:20px;"><div slot="header"><span>📈 月度收益</span></div>
      <el-table :data="monthly" v-loading="loading">
        <el-table-column prop="month" label="月份" width="100" />
        <el-table-column prop="return_pct" label="收益率"><template slot-scope="{ row }"><span :style="{color: row.return_pct > 0 ? '#67C23A' : '#F56C6C', fontWeight:600}">{{ row.return_pct > 0 ? '+' : '' }}{{ row.return_pct }}%</span></template></el-table-column>
        <el-table-column prop="benchmark" label="基准" width="80" />
        <el-table-column prop="alpha" label="Alpha" width="80" />
      </el-table>
    </el-card>
  </div>
</template>
<script>
import request from '@/utils/request'
export default { name: 'Performance', data() { return {
  metrics: [
    { label: '累计收益', value: '--', color: '#303133' },
    { label: '年化收益', value: '--', color: '#303133' },
    { label: '夏普比率', value: '--', color: '#303133' },
    { label: '最大回撤', value: '--', color: '#303133' }
  ],
  monthly: [], loading: false
}}, created() { this.fetchData() }, methods: {
  async fetchData() {
    this.loading = true
    try {
      const { data } = await request.get('/api/performance')
      if (data.code === 200) {
        const d = data.data
        this.metrics[0].value = d.total_return ? '+' + d.total_return + '%' : '--'
        this.metrics[1].value = d.annual_return ? '+' + d.annual_return + '%' : '--'
        this.metrics[2].value = d.sharpe || '--'
        this.metrics[3].value = d.max_drawdown ? d.max_drawdown + '%' : '--'
        this.monthly = d.monthly || []
      }
    } catch (e) { this.$message.error('获取绩效数据失败') }
    finally { this.loading = false }
  }
}}
</script>
