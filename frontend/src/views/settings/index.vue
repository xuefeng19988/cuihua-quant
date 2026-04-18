<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>⚙️ 系统设置</span></div></el-card>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基本设置" name="basic">
        <el-form :model="settings" label-width="120px" style="max-width:500px;">
          <el-form-item label="系统名称"><el-input v-model="settings.app_name" /></el-form-item>
          <el-form-item label="数据源"><el-select v-model="settings.data_source"><el-option label="Futu" value="futu" /><el-option label="AKShare" value="akshare" /><el-option label="双源" value="both" /></el-select></el-form-item>
          <el-form-item label="刷新间隔"><el-input-number v-model="settings.refresh_interval" :min="5" :max="300" :step="5" /> 秒</el-form-item>
          <el-form-item><el-button type="primary" @click="saveSettings">💾 保存</el-button></el-form-item>
        </el-form>
      </el-tab-pane>
      <el-tab-pane label="通知设置" name="notify">
        <el-form :model="settings" label-width="120px" style="max-width:500px;">
          <el-form-item label="邮件通知"><el-switch v-model="settings.email_notify" /></el-form-item>
          <el-form-item label="企业微信"><el-switch v-model="settings.wecom_notify" /></el-form-item>
          <el-form-item label="告警级别"><el-select v-model="settings.alert_level"><el-option label="仅严重" value="critical" /><el-option label="全部" value="all" /></el-select></el-form-item>
          <el-form-item><el-button type="primary" @click="saveSettings">💾 保存</el-button></el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script>
import request from '@/utils/request'
export default { name: 'Settings', data() { return { activeTab: 'basic', settings: {} } },
  created() { this.fetchSettings() },
  methods: {
    async fetchSettings() {
      try {
        const { data } = await request.get('/api/settings')
        if (data.code === 200) this.settings = data.data
      } catch (e) { this.$message.error('获取设置失败') }
    },
    async saveSettings() {
      try {
        await request.post('/api/settings', this.settings)
        this.$message.success('设置已保存')
      } catch (e) { this.$message.error('保存失败') }
    }
  }
}
</script>
