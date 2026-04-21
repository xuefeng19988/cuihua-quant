<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📡 实时推送</span><el-tag size="mini" type="success" style="float:right;">已连接</el-tag></div></el-card>
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in pushTypes" :key="item.type">
        <el-card shadow="hover" style="text-align:center;">
          <div style="font-size:24px;">{{ item.icon }}</div>
          <div style="font-size:14px;margin:8px 0;">{{ item.name }}</div>
          <el-switch v-model="item.enabled" />
        </el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top:20px;"><div slot="header"><span>📋 推送日志</span></div>
      <el-timeline>
        <el-timeline-item v-for="log in logs" :key="log.time" :timestamp="log.time" placement="top">
          <el-card shadow="hover"><h4>{{ log.type }}</h4><p>{{ log.message }}</p></el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'RealtimePusher',
  data() {
    return {
      pushTypes: [
        { type: 'quotes', name: '行情推送', icon: '📈', enabled: true },
        { type: 'signals', name: '信号推送', icon: '🔔', enabled: true },
        { type: 'notifications', name: '通知推送', icon: '📢', enabled: true },
        { type: 'alerts', name: '预警推送', icon: '⚠️', enabled: true }
      ],
      logs: [
        { time: '15:38:00', type: '行情', message: 'SH.600519 贵州茅台 价格更新: 1720.50' },
        { time: '15:37:45', type: '信号', message: 'SZ.002594 比亚迪 RSI超卖信号' },
        { time: '15:37:30', type: '预警', message: 'HK.00700 腾讯控股 涨幅超3%' }
      ]
    }
  },
  created() { this.fetchStatus() },
  methods: {
    async fetchStatus() {
      try { await request.get('/realtime/status') } catch (e) {}
    }
  }
}
</script>
