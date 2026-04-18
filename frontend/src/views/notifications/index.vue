<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>🔔 通知中心</span>
        <div style="float:right;">
          <el-badge :value="unread" :hidden="unread===0" style="margin-right:12px;">
            <el-tag size="mini">未读消息</el-tag>
          </el-badge>
          <el-button size="mini" @click="markAllRead" :disabled="unread===0">✅ 全部已读</el-button>
        </div>
      </div>
    </el-card>

    <el-timeline v-loading="loading">
      <el-timeline-item
        v-for="n in notifications"
        :key="n.id"
        :color="typeColor(n.type)"
        :icon="typeIcon(n.type)"
        :timestamp="formatTime(n.time)"
        placement="top"
      >
        <el-card shadow="hover" :style="{ opacity: n.read ? 0.7 : 1 }">
          <h4>{{ n.title }} <el-tag v-if="!n.read" size="mini" type="danger" style="margin-left:8px;">未读</el-tag></h4>
          <p style="color:#606266;margin:8px 0;">{{ n.message }}</p>
          <el-tag size="mini" :type="typeTagColor(n.type)">{{ typeName(n.type) }}</el-tag>
        </el-card>
      </el-timeline-item>
    </el-timeline>

    <el-empty v-if="notifications.length === 0 && !loading" description="暂无通知" />
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Notifications',
  data() { return { notifications: [], unread: 0, loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/notifications')
        if (data.code === 200) {
          this.notifications = data.data.notifications || []
          this.unread = data.data.unread || 0
        }
      } catch (e) { this.$message.error('获取通知失败') }
      finally { this.loading = false }
    },
    async markAllRead() {
      try {
        await request.post('/api/notifications', { action: 'mark_read' })
        this.$message.success('已全部标为已读')
        this.fetchData()
      } catch (e) { this.$message.error('操作失败') }
    },
    typeColor(type) {
      const map = { alert: '#F56C6C', signal: '#67C23A', system: '#409EFF', risk: '#E6A23C', news: '#909399' }
      return map[type] || '#909399'
    },
    typeIcon(type) {
      const map = { alert: 'el-icon-warning', signal: 'el-icon-success', system: 'el-icon-info', risk: 'el-icon-warning-outline', news: 'el-icon-news' }
      return map[type] || 'el-icon-info'
    },
    typeName(type) {
      const map = { alert: '预警', signal: '信号', system: '系统', risk: '风险', news: '新闻' }
      return map[type] || type
    },
    typeTagColor(type) {
      const map = { alert: 'danger', signal: 'success', system: '', risk: 'warning', news: 'info' }
      return map[type] || ''
    },
    formatTime(time) {
      const d = new Date(time)
      return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
    }
  }
}
</script>
