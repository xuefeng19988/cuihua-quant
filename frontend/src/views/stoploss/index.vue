<template>
  <div class="app-container">
    <el-card>
      <div slot="header"><span>🛑 智能止损</span></div>
      <el-table :data="strategies" style="width: 100%">
        <el-table-column prop="name" label="策略" />
        <el-table-column prop="desc" label="描述" />
        <el-table-column prop="param" label="参数" width="100" />
        <el-table-column label="状态" width="80">
          <template slot-scope="{ row }"><el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '可用' : '待配置' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
<script>
export default {
  name: 'Stoploss',
  data() {
    return {
      strategies: [
        { name: '固定止损', desc: '固定百分比止损', param: '5%', enabled: true },
        { name: '追踪止损', desc: '跟随价格上涨止损', param: '3% 回撤', enabled: true },
        { name: '波动率止损', desc: '基于 ATR 动态止损', param: '2x ATR', enabled: true },
        { name: '时间止损', desc: '持仓超时止损', param: 'N 天', enabled: false },
        { name: '技术止损', desc: '技术位破位止损', param: '均线/支撑', enabled: false }
      ]
    }
  }
}
</script>
