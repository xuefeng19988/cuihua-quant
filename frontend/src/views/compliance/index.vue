<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="item in stats" :key="item.label">
        <el-card shadow="hover"><div style="color:#909399;font-size:13px;">{{ item.label }}</div><div style="font-size:20px;font-weight:600;margin-top:8px;" :style="{color: item.color}">{{ item.value }}</div></el-card>
      </el-col>
    </el-row>
    <el-card>
      <div slot="header"><span>✅ 合规规则</span></div>
      <el-table :data="rules" style="width: 100%">
        <el-table-column prop="category" label="规则类别" width="120" />
        <el-table-column prop="rule" label="规则" />
        <el-table-column prop="threshold" label="阈值" width="100" />
        <el-table-column label="状态" width="80">
          <template slot-scope="{ row }"><el-tag type="success" size="small">合规</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
<script>
export default {
  name: 'Compliance',
  data() {
    return {
      stats: [
        { label: '合规规则', value: '20+', color: '#409EFF' },
        { label: '违规次数', value: '0', color: '#67C23A' },
        { label: '检查频率', value: '实时', color: '#303133' },
        { label: '最后检查', value: '今日', color: '#303133' }
      ],
      rules: [
        { category: '持仓限制', rule: '单只股票占比', threshold: '<20%' },
        { category: '行业集中度', rule: '行业总占比', threshold: '<40%' },
        { category: '杠杆限制', rule: '总杠杆率', threshold: '<2x' },
        { category: '流动性', rule: '低流动性股票', threshold: '<10%' },
        { category: '交易频率', rule: '日内交易次数', threshold: '<N次' }
      ]
    }
  }
}
</script>
