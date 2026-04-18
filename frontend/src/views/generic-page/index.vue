<!--
  通用占位页面组件
  用于功能开发中或信息展示类页面
  用法: 通过路由 meta.apiEndpoint 指定API端点
-->
<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>{{ icon }} {{ title }}</span>
        <el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button>
      </div>
      <el-alert v-if="description" :title="description" type="info" :closable="false" style="margin-bottom:16px;" />
    </el-card>
    <el-card v-if="data && Object.keys(data).length > 0">
      <div v-if="isTableData" style="margin-bottom:16px;">
        <el-table :data="tableData" stripe>
          <el-table-column v-for="col in tableColumns" :key="col.prop" :prop="col.prop" :label="col.label" :width="col.width" />
        </el-table>
      </div>
      <div v-else>
        <el-descriptions :column="2" border>
          <el-descriptions-item v-for="(val, key) in flatData" :key="key" :label="key">{{ val }}</el-descriptions-item>
        </el-descriptions>
        <pre v-if="showRaw" style="margin-top:16px;font-size:12px;max-height:400px;overflow:auto;">{{ JSON.stringify(data, null, 2) }}</pre>
      </div>
    </el-card>
    <el-empty v-else description="暂无数据" />
  </div>
</template>

<script>
import request from '@/utils/request'

const PAGE_CONFIG = {
  'HealthCheck': { icon: '💚', title: '健康检查', endpoint: '/api/health', desc: '系统运行状态检查' },
  'ErrorHandler': { icon: '⚠️', title: '错误处理', endpoint: '/api/logs', desc: '全局错误捕获与处理' },
  'TestRunner': { icon: '🧪', title: '测试运行器', endpoint: '/api/perf-monitor', desc: '自动化测试执行' },
  'SecurityConfig': { icon: '🔒', title: '安全配置', endpoint: '/api/settings', desc: 'HTTPS/认证/权限配置' },
  'LogRotator': { icon: '🔄', title: '日志轮转', endpoint: '/api/log-analyzer', desc: '日志归档与清理策略' },
  'DBBackup': { icon: '💾', title: '数据库备份', endpoint: '/api/backup/list', desc: '定时自动备份数据库' },
  'MonitorAlert': { icon: '📊', title: '监控告警', endpoint: '/api/perf-monitor', desc: '系统监控与告警集成' },
  'ShortcutConfig': { icon: '⌨️', title: '快捷键配置', endpoint: '/api/shortcuts', desc: '全局键盘快捷键设置' },
  'DataWizard': { icon: '🎯', title: '数据导入向导', endpoint: '/api/data-quality', desc: '图形化数据导入流程' },
  'PrintOptimizer': { icon: '🖨️', title: '打印优化', endpoint: '/api/settings', desc: '打印样式优化' },
  'Accessibility': { icon: '♿', title: '无障碍访问', endpoint: '/api/settings', desc: 'a11y 无障碍支持' },
  'LLMIntegration': { icon: '🤖', title: 'LLM集成', endpoint: '/api/ai-report', desc: '大语言模型智能问答' },
  'ImageRecognition': { icon: '🖼️', title: '图像识别', endpoint: '/api/charts', desc: 'K线形态自动识别' },
  'OpenAPIDoc': { icon: '📚', title: 'OpenAPI文档', endpoint: '/api/stats', desc: 'API 文档 (Swagger/Redoc)' },
  'WebhookManager': { icon: '🔗', title: 'Webhook管理', endpoint: '/api/webhook', desc: '第三方集成 Webhook' },
  'PluginManager': { icon: '🧩', title: '插件管理', endpoint: '/api/plugins', desc: '可扩展插件系统' },
  'SDKDocs': { icon: '📖', title: 'SDK文档', endpoint: '/api/sdk/info', desc: 'Python/JS SDK 文档' },
  'DataMarketplace': { icon: '🛒', title: '数据市场', endpoint: '/api/data-market', desc: '付费数据源接入' }
}

export default {
  name: 'GenericPage',
  data() {
    return { data: null, loading: false, showRaw: false }
  },
  computed: {
    config() { return PAGE_CONFIG[this.$options.name] || { icon: '📄', title: this.$route.meta.title || '页面', endpoint: '/api/stats', desc: '' } },
    icon() { return this.config.icon },
    title() { return this.config.title },
    description() { return this.config.desc },
    endpoint() { return this.config.endpoint },
    isTableData() { return this.data && Array.isArray(this.data[this.primaryKey]) },
    primaryKey() {
      if (!this.data) return ''
      const keys = Object.keys(this.data)
      return keys.find(k => Array.isArray(this.data[k]) && this.data[k].length > 0 && typeof this.data[k][0] === 'object') || ''
    },
    tableData() { return this.primaryKey ? this.data[this.primaryKey] : [] },
    tableColumns() {
      if (!this.tableData.length) return []
      return Object.keys(this.tableData[0]).map(k => ({ prop: k, label: k, width: k === 'id' || k === 'status' ? 100 : undefined }))
    },
    flatData() {
      if (!this.data) return {}
      const result = {}
      const flatten = (obj, prefix = '') => {
        for (const [k, v] of Object.entries(obj)) {
          const key = prefix ? `${prefix}.${k}` : k
          if (typeof v === 'object' && v !== null && !Array.isArray(v)) flatten(v, key)
          else if (!Array.isArray(v)) result[key] = v
        }
      }
      flatten(this.data)
      return result
    }
  },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get(this.endpoint)
        if (data.code === 200) this.data = data.data
      } catch (e) { this.data = { error: '获取数据失败' } }
      finally { this.loading = false }
    }
  }
}
</script>
