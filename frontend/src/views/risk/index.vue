<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="item in metrics" :key="item.label">
        <el-card shadow="hover"><div style="color:#909399;font-size:13px;">{{ item.label }}</div><div style="font-size:20px;font-weight:600;margin-top:8px;color:#303133;">{{ item.value }}</div></el-card>
      </el-col>
    </el-row>
    <el-card>
      <div slot="header"><span>📊 风险指标</span></div>
      <el-table :data="indicators" style="width: 100%">
        <el-table-column prop="name" label="指标" />
        <el-table-column prop="value" label="当前值" width="100" />
        <el-table-column prop="threshold" label="阈值" width="100" />
        <el-table-column label="状态" width="80">
          <template slot-scope="{ row }"><el-tag :type="row.status === 'normal' ? 'success' : 'warning'" size="small">{{ row.statusText }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Risk',
  data() {
    return {
      metrics: [
        { label: 'VaR (95%)', value: '--' },
        { label: 'CVaR (95%)', value: '--' },
        { label: '最大回撤', value: '--' },
        { label: '波动率', value: '--' }
      ],
      indicators: [
        { name: '组合波动率', value: '--', threshold: '25%', status: 'normal', statusText: '待计算' },
        { name: '最大集中度', value: '--', threshold: '20%', status: 'normal', statusText: '待计算' },
        { name: '杠杆率', value: '1.0x', threshold: '2.0x', status: 'normal', statusText: '正常' },
        { name: '现金比例', value: '--', threshold: '10%', status: 'normal', statusText: '待计算' }
      ]
    }
  }
}
</script>
