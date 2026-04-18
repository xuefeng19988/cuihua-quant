<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📅 量化交易日历</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div></el-card>
    <el-timeline>
      <el-timeline-item v-for="e in events" :key="e.date" :color="e.importance==='high'?'#F56C6C':'#E6A23C'" :timestamp="e.date" placement="top">
        <el-card shadow="hover">
          <h4><el-tag size="mini" :type="e.type==='财报'?'success':e.type==='宏观'?'warning':'info'">{{ e.type }}</el-tag> {{ e.title }}</h4>
          <el-tag size="mini" style="margin-top:8px;" :type="e.importance==='high'?'danger':''">{{ e.importance==='high'?'重要':'一般' }}</el-tag>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'TradeCalendar', data() { return { events: [], loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try { const { data } = await request.get('/api/trade-calendar'); if (data.code === 200) this.events = data.data.events }
      catch (e) { this.$message.error('获取数据失败') }
      finally { this.loading = false }
    }
  }
}
</script>
