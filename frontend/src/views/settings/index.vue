<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>⚙️ 系统设置</span></div></el-card>
    <el-tabs>
      <el-tab-pane label="基本设置">
        <el-form label-width="120px" style="max-width:500px;">
          <el-form-item label="系统名称"><el-input v-model="settings.appName" /></el-form-item>
          <el-form-item label="数据源"><el-select v-model="settings.dataSource"><el-option label="Futu" value="futu" /><el-option label="AKShare" value="akshare" /><el-option label="双源" value="both" /></el-select></el-form-item>
          <el-form-item label="刷新间隔"><el-input-number v-model="settings.refreshInterval" :min="5" :max="300" :step="5" /> 秒</el-form-item>
          <el-form-item><el-button type="primary" @click="saveSettings">💾 保存</el-button></el-form-item>
        </el-form>
      </el-tab-pane>
      <el-tab-pane label="通知设置">
        <el-form label-width="120px" style="max-width:500px;">
          <el-form-item label="邮件通知"><el-switch v-model="settings.emailNotify" /></el-form-item>
          <el-form-item label="企业微信"><el-switch v-model="settings.wecomNotify" /></el-form-item>
          <el-form-item label="告警级别"><el-select v-model="settings.alertLevel"><el-option label="仅严重" value="critical" /><el-option label="全部" value="all" /></el-select></el-form-item>
          <el-form-item><el-button type="primary" @click="saveSettings">💾 保存</el-button></el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script>
export default { name: 'Settings', data() { return {
  settings: { appName: '翠花量化系统', dataSource: 'both', refreshInterval: 30, emailNotify: false, wecomNotify: true, alertLevel: 'all' }
}}, methods: { saveSettings() { this.$message.success('设置已保存') } } }
</script>
