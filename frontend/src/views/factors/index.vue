<template>
  <div class="app-container">
    <el-card>
      <div slot="header"><span>🧮 因子研究</span></div>
      <el-table :data="factors" style="width: 100%">
        <el-table-column prop="name" label="因子类别" width="120" />
        <el-table-column prop="desc" label="描述" />
        <el-table-column prop="count" label="数量" width="80" />
        <el-table-column label="状态" width="100">
          <template slot-scope="{ row }"><el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">{{ row.status === 'active' ? '可用' : '研究中' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
<script>
export default {
  name: 'Factors',
  data() {
    return {
      factors: [
        { name: '技术因子', desc: 'MACD/RSI/布林带/KDJ', count: '10+', status: 'active' },
        { name: '基本面因子', desc: 'PE/PB/ROE/营收增长', count: '8+', status: 'active' },
        { name: '情绪因子', desc: '新闻情绪/社交情绪', count: '5+', status: 'active' },
        { name: '质量因子', desc: '盈利质量/财务健康', count: '4+', status: 'active' },
        { name: 'Alpha101', desc: 'WorldQuant Alpha101', count: '101', status: 'active' },
        { name: 'Fama-French', desc: '三因子/五因子', count: '5', status: 'active' }
      ]
    }
  }
}
</script>
