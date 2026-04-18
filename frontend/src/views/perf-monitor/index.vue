<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📊 性能监控</span></div></el-card>
    <el-row :gutter="20">
      <el-col :span="8" v-for="m in metrics" :key="m.label"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;">{{ m.label }}</div><div style="font-size:24px;font-weight:600;" :style="{color:m.color}">{{ m.value }}</div></el-card></el-col>
    </el-row>
    <el-card style="margin-top:20px;"><div slot="header"><span>📈 系统运行时间</span></div><p>系统已持续运行: <strong>{{ data.uptime }}</strong></p></el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'PerfMonitor', data() { return { data: {}, metrics: [] } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try {
        const { data } = await request.get('/api/perf-monitor')
        if (data.code === 200) {
          this.data = data.data
          this.metrics = [
            { label: 'CPU使用率', value: data.data.cpu_usage + '%', color: data.data.cpu_usage > 80 ? '#F56C6C' : '#67C23A' },
            { label: '内存使用率', value: data.data.memory_usage + '%', color: '#409EFF' },
            { label: '磁盘使用率', value: data.data.disk_usage + '%', color: '#E6A23C' },
            { label: 'API响应时间', value: data.data.api_response_time + 'ms', color: '#409EFF' },
            { label: '活跃用户', value: data.data.active_users, color: '#67C23A' },
            { label: '请求/分钟', value: data.data.requests_per_min, color: '#409EFF' }
          ]
        }
      } catch (e) {}
    }
  }
}
</script>
