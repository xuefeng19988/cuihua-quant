<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>📅 事件研究</span><el-tag size="mini" style="float:right;">事件驱动分析</el-tag></div>
    </el-card>
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card><div slot="header"><span>📋 事件列表</span></div>
          <el-table :data="events" style="width:100%">
            <el-table-column prop="name" label="事件名称" />
            <el-table-column prop="date" label="事件日期" width="110" />
            <el-table-column prop="type" label="类型" width="80"><template slot-scope="{ row }"><el-tag size="mini">{{ row.type }}</el-tag></template></el-table-column>
            <el-table-column prop="impact" label="影响幅度" width="90"><template slot-scope="{ row }"><span :style="{color: row.impact > 0 ? '#67C23A' : '#F56C6C'}">{{ row.impact > 0 ? '+' : '' }}{{ row.impact }}%</span></template></el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card><div slot="header"><span>📊 事件统计</span></div>
          <el-statistic title="总事件数" :value="events.length" />
          <el-statistic title="平均影响" :value="avgImpact" suffix="%" :precision="2" style="margin-top:16px;" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'Events',
  data() {
    return {
      events: [
        { name: '财报发布', date: '2026-04-15', type: '财报', impact: 3.2 },
        { name: '央行降息', date: '2026-04-10', type: '宏观', impact: -1.5 },
        { name: '行业政策', date: '2026-04-05', type: '政策', impact: 2.1 },
        { name: '高管变动', date: '2026-03-28', type: '公司', impact: -0.8 }
      ]
    }
  },
  computed: { avgImpact() { return this.events.length ? this.events.reduce((s, e) => s + e.impact, 0) / this.events.length : 0 } }
}
</script>
