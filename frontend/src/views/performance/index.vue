<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📊 绩效看板</span></div></el-card>
    <el-row :gutter="20">
      <el-col :span="6" v-for="m in metrics" :key="m.label">
        <el-card shadow="hover"><div style="color:#909399;font-size:13px;">{{ m.label }}</div><div style="font-size:20px;font-weight:600;margin-top:8px;" :style="{color:m.color}">{{ m.value }}</div></el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top:20px;"><div slot="header"><span>📈 月度收益</span></div>
      <el-table :data="monthly" style="width:100%">
        <el-table-column prop="month" label="月份" width="100" />
        <el-table-column prop="return_pct" label="收益率"><template slot-scope="{ row }"><span :style="{color: row.return_pct > 0 ? '#67C23A' : '#F56C6C', fontWeight:600}">{{ row.return_pct > 0 ? '+' : '' }}{{ row.return_pct }}%</span></template></el-table-column>
        <el-table-column prop="benchmark" label="基准" width="80" />
        <el-table-column prop="alpha" label="Alpha" width="80" />
      </el-table>
    </el-card>
  </div>
</template>
<script>
export default { name: 'Performance', data() { return {
  metrics: [
    { label: '累计收益', value: '+15.2%', color: '#67C23A' },
    { label: '年化收益', value: '+18.5%', color: '#67C23A' },
    { label: '夏普比率', value: '1.35', color: '#303133' },
    { label: '最大回撤', value: '-8.2%', color: '#F56C6C' }
  ],
  monthly: [
    { month: '2026-04', return_pct: 5.2, benchmark: 2.1, alpha: 3.1 },
    { month: '2026-03', return_pct: -2.1, benchmark: -1.5, alpha: -0.6 },
    { month: '2026-02', return_pct: 8.3, benchmark: 4.2, alpha: 4.1 },
    { month: '2026-01', return_pct: 3.1, benchmark: 1.8, alpha: 1.3 }
  ]
}}}
</script>
