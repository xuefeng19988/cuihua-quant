<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="item in metrics" :key="item.label">
        <el-card shadow="hover"><div style="color:#909399;font-size:13px;">{{ item.label }}</div><div style="font-size:20px;font-weight:600;margin-top:8px;" :style="{color:item.color}">{{ item.value }}</div></el-card>
      </el-col>
    </el-row>
    <el-card>
      <div slot="header"><span>📈 绩效分析</span></div>
      <el-empty description="暂无绩效数据，请先运行回测" />
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Performance',
  data() {
    return {
      metrics: [
        { label: '总收益率', value: '--', color: '#303133' },
        { label: '年化收益', value: '--', color: '#303133' },
        { label: '夏普比率', value: '--', color: '#303133' },
        { label: '最大回撤', value: '--', color: '#303133' }
      ]
    }
  }
}
</script>
