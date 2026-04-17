<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>🎯 策略管理</span></div>
      <el-table :data="strategies" style="width: 100%">
        <el-table-column prop="name" label="策略名称" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="status" label="状态" width="80">
          <template slot-scope="{ row }"><el-tag :type="row.status === 'active' ? 'success' : row.status === 'research' ? 'warning' : 'info'" size="small">{{ row.statusText }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="desc" label="描述" />
        <el-table-column label="操作" width="100">
          <template slot-scope="{ row }"><el-button size="mini" @click="$router.push('/trade/backtest')">🔬 回测</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Strategies',
  data() {
    return {
      strategies: [
        { name: 'SMA 交叉', type: '趋势跟踪', status: 'active', statusText: '活跃', desc: '基础均线交叉策略' },
        { name: '动量策略', type: '趋势跟踪', status: 'active', statusText: '活跃', desc: '动量突破策略' },
        { name: '均值回归', type: '均值回归', status: 'active', statusText: '活跃', desc: '布林带均值回归' },
        { name: '多因子', type: '量化选股', status: 'active', statusText: '活跃', desc: '多因子选股模型' },
        { name: '配对交易', type: '统计套利', status: 'research', statusText: '研究中', desc: '协整配对交易' },
        { name: '波动率策略', type: '波动率', status: 'research', statusText: '研究中', desc: '波动率突破策略' },
        { name: '行业轮动', type: '行业轮动', status: 'research', statusText: '研究中', desc: '行业轮动策略' }
      ]
    }
  }
}
</script>
