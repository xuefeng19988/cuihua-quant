<template>
  <div class="app-container">
    <el-card>
      <div slot="header"><span>💥 压力测试</span></div>
      <el-table :data="scenarios" style="width: 100%">
        <el-table-column prop="name" label="场景" />
        <el-table-column prop="desc" label="描述" />
        <el-table-column prop="impact" label="影响" width="150" />
        <el-table-column label="状态" width="100">
          <template slot-scope="{ row }"><el-tag type="success" size="small">可用</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
<script>
export default {
  name: 'Stress',
  data() {
    return {
      scenarios: [
        { name: '2008 金融危机', desc: '全球市场崩盘', impact: '组合 -30%~50%' },
        { name: '2020 疫情', desc: '疫情冲击市场', impact: '组合 -20%~40%' },
        { name: '利率飙升', desc: '利率快速上升', impact: '债券 -10%~20%' },
        { name: '流动性危机', desc: '市场流动性枯竭', impact: '组合 -15%~30%' },
        { name: '蒙特卡洛模拟', desc: '10000 次随机模拟', impact: 'VaR/CVaR 估计' }
      ]
    }
  }
}
</script>
