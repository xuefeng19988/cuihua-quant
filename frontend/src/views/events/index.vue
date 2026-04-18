<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>📅 事件研究</span>
        <div style="float:right;">
          <el-select v-model="filterType" size="mini" placeholder="全部类型" clearable style="width:120px;" @change="fetchEvents">
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
          <el-button size="mini" icon="el-icon-refresh" @click="fetchEvents" style="margin-left:8px;">刷新</el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="16">
        <el-card>
          <div slot="header"><span>📋 事件列表 ({{ total }})</span></div>
          <el-table :data="events" style="width:100%">
            <el-table-column prop="name" label="事件名称" />
            <el-table-column prop="date" label="日期" width="110" />
            <el-table-column prop="type" label="类型" width="80">
              <template slot-scope="{ row }"><el-tag size="mini" :type="typeColor(row.type)">{{ row.type }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="impact" label="影响" width="90">
              <template slot-scope="{ row }">
                <span :style="{color: row.impact > 0 ? '#67C23A' : '#F56C6C', fontWeight:600}">
                  {{ row.impact > 0 ? '+' : '' }}{{ row.impact }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card style="margin-bottom:16px;">
          <div slot="header"><span>📊 统计</span></div>
          <el-statistic title="总事件数" :value="total" />
          <el-statistic title="平均影响" :value="avgImpact" suffix="%" :precision="2" style="margin-top:16px;" />
        </el-card>
        <el-card>
          <div slot="header"><span>📈 类型分布</span></div>
          <div v-for="(count, type) in typeDist" :key="type" style="margin:8px 0;">
            <span style="color:#606266;">{{ type }}</span>
            <el-tag size="mini" style="float:right;">{{ count }}</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Events',
  data() {
    return { events: [], total: 0, avgImpact: 0, typeDist: {}, types: [], filterType: '', loading: false }
  },
  created() { this.fetchEvents() },
  methods: {
    async fetchEvents() {
      this.loading = true
      try {
        const params = {}
        if (this.filterType) params.type = this.filterType
        const res = await request.get('/events', { params })
        if (res.code === 200) {
          const d = res.data
          this.events = d.events || []
          this.total = d.total || 0
          this.avgImpact = d.avg_impact || 0
          this.typeDist = d.type_distribution || {}
          this.types = Object.keys(this.typeDist)
        }
      } catch (e) {
        console.error('获取事件数据失败:', e)
      } finally {
        this.loading = false
      }
    },
    typeColor(type) {
      const map = { '宏观': '', '政策': 'warning', '财报': 'success', '地缘': 'danger', '公司': 'info' }
      return map[type] || ''
    }
  }
}
</script>
