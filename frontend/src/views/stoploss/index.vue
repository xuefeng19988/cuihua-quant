<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>🛑 智能止损</span><el-tag size="mini" style="float:right;">自动止损管理</el-tag></div>
    </el-card>
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card><div slot="header"><span>📋 止损规则</span></div>
          <el-table :data="rules" style="width:100%">
            <el-table-column prop="name" label="规则名称" />
            <el-table-column prop="type" label="类型" width="100"><template slot-scope="{ row }"><el-tag size="mini">{{ row.type }}</el-tag></template></el-table-column>
            <el-table-column prop="threshold" label="触发阈值" width="100" />
            <el-table-column prop="action" label="动作" width="80" />
            <el-table-column prop="enabled" label="状态" width="80"><template slot-scope="{ row }"><el-switch v-model="row.enabled" /></template></el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card><div slot="header"><span>📊 止损统计</span></div>
          <el-statistic title="今日触发" :value="2" />
          <el-statistic title="累计触发" :value="15" style="margin-top:16px;" />
          <el-statistic title="避免损失" :value="8520" suffix="元" :precision="0" style="margin-top:16px;" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'StopLoss',
  data() {
    return {
      rules: [
        { name: '固定比例止损', type: '比例', threshold: '-5%', action: '卖出', enabled: true },
        { name: '移动止损', type: '追踪', threshold: '-8%', action: '卖出', enabled: true },
        { name: '技术位止损', type: '技术', threshold: 'MA20', action: '卖出', enabled: false },
        { name: '时间止损', type: '时间', threshold: '5天', action: '卖出', enabled: false }
      ]
    }
  }
}
</script>
