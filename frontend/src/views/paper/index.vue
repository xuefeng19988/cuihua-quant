<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="item in stats" :key="item.label">
        <el-card shadow="hover"><div style="color:#909399;font-size:13px;">{{ item.label }}</div><div style="font-size:20px;font-weight:600;margin-top:8px;">{{ item.value }}</div></el-card>
      </el-col>
    </el-row>
    <el-card>
      <div slot="header"><span>📋 交易记录</span></div>
      <el-empty description="暂无交易记录，请先添加策略信号" />
    </el-card>
  </div>
</template>
<script>
export default {
  name: 'Paper',
  data() {
    return {
      stats: [
        { label: '模拟资产', value: '¥1,000,000' },
        { label: '持仓数量', value: '0' },
        { label: '今日盈亏', value: '¥0' },
        { label: '总收益率', value: '0%' }
      ]
    }
  }
}
</script>
