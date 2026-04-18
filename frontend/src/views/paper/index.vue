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
    <el-card style="margin-top:20px;">
      <div slot="header"><span>📊 持仓明细</span></div>
      <el-table :data="positions" style="width:100%">
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
export default {
  name: 'Paper',
  data() {
    return {
      running: true,
      metrics: [
        { label: '总资产', value: '1,052,340', color: '#303133' },
        { label: '总收益', value: '+52,340', color: '#67C23A' },
        { label: '收益率', value: '+5.23%', color: '#67C23A' },
        { label: '持仓数', value: '8', color: '#303133' }
      ],
      positions: [
        { code: 'SH.600519', name: '贵州茅台', shares: 100, cost: 1680, price: 1720, pnl: 4000 },
        { code: 'SZ.002594', name: '比亚迪', shares: 200, cost: 280, price: 295, pnl: 3000 },
        { code: 'SH.601318', name: '中国平安', shares: 300, cost: 48, price: 50, pnl: 600 }
      ]
    }
  }
}
</script>
