<template>
  <div class="app-container">
    <el-card>
      <div slot="header"><span>📑 自动报告</span></div>
      <el-table :data="reports" style="width: 100%">
        <el-table-column prop="name" label="报告类型" />
        <el-table-column prop="content" label="内容" />
        <el-table-column prop="frequency" label="频率" width="80" />
        <el-table-column label="状态" width="100">
          <template slot-scope="{ row }"><el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '已配置' : '待配置' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
<script>
export default {
  name: 'Reports',
  data() {
    return {
      reports: [
        { name: '每日交易报告', content: '交易记录/盈亏', frequency: '每日', enabled: false },
        { name: '周报', content: '组合表现/策略分析', frequency: '每周', enabled: false },
        { name: '月报', content: '月度总结/风险报告', frequency: '每月', enabled: false },
        { name: '风险报告', content: 'VaR/压力测试', frequency: '每周', enabled: false },
        { name: '策略报告', content: '策略表现对比', frequency: '每月', enabled: false }
      ]
    }
  }
}
</script>
