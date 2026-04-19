<template>
  <div class="llm-config-panel">
    <div style="margin-bottom:16px;">
      <el-button type="primary" size="small" @click="showAddDialog">➕ 添加模型</el-button>
      <el-button size="small" @click="testConnection">🔌 测试连接</el-button>
    </div>

    <!-- 配置列表 -->
    <el-table :data="configs" stripe border style="width:100%;">
      <el-table-column label="状态" width="60">
        <template slot-scope="{row}">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="mini">
            {{ row.is_active ? '✅ 活跃' : '⏸️' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="名称" width="120" />
      <el-table-column prop="provider" label="提供商" width="100" />
      <el-table-column prop="model" label="模型" />
      <el-table-column label="API Key" width="120">
        <template slot-scope="{row}">{{ row.api_key }}</template>
      </el-table-column>
      <el-table-column label="用量" width="100">
        <template slot-scope="{row}">
          <span style="font-size:12px;">{{ row.usage_count }} 次</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="{row}">
          <el-button v-if="!row.is_active" type="text" size="mini" @click="switchTo(row.name)">切换</el-button>
          <el-button type="text" size="mini" @click="editConfig(row)">编辑</el-button>
          <el-button type="text" size="mini" style="color:#f56c6c;" @click="deleteConfig(row.name)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 统计信息 -->
    <el-row :gutter="16" style="margin-top:16px;">
      <el-col :span="6">
        <el-statistic title="配置总数" :value="stats.total_configs" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="总调用次数" :value="stats.total_usage" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="总 Token 消耗" :value="stats.total_tokens" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="当前模型" :value="stats.active_config || '无'" />
      </el-col>
    </el-row>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="如：my-qwen" />
        </el-form-item>
        <el-form-item label="提供商">
          <el-select v-model="form.provider" style="width:100%;" @change="onProviderChange">
            <el-option label="阿里百炼 (bailian)" value="bailian" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="硅基流动" value="siliconflow" />
          </el-select>
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="form.api_key" placeholder="sk-xxx" />
        </el-form-item>
        <el-form-item label="模型">
          <el-select v-model="form.model" filterable style="width:100%;">
            <el-option v-for="m in availableModels" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存</el-button>
      </span>
    </el-dialog>

    <!-- 测试连接对话框 -->
    <el-dialog title="测试连接" :visible.sync="testDialogVisible" width="450px">
      <el-form label-width="80px">
        <el-form-item label="API Key">
          <el-input v-model="testForm.api_key" type="password" placeholder="输入 API Key" />
        </el-form-item>
        <el-form-item label="提供商">
          <el-select v-model="testForm.provider" style="width:100%;" @change="onTestProviderChange">
            <el-option label="阿里百炼" value="bailian" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="DeepSeek" value="deepseek" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型">
          <el-input v-model="testForm.model" />
        </el-form-item>
      </el-form>
      <el-alert v-if="testResult" :title="testResult" :type="testResultType" style="margin-top:8px;" show-icon />
      <span slot="footer">
        <el-button @click="testDialogVisible=false">关闭</el-button>
        <el-button type="primary" @click="doTest" :loading="testLoading">测试</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'LLMConfigManager',
  data() {
    return {
      configs: [],
      stats: { total_configs: 0, total_usage: 0, total_tokens: 0, active_config: '' },
      dialogVisible: false,
      dialogTitle: '添加模型',
      form: { name: '', provider: 'bailian', api_key: '', model: '' },
      availableModels: [],
      // Test
      testDialogVisible: false,
      testLoading: false,
      testForm: { api_key: '', provider: 'bailian', model: 'qwen-plus' },
      testResult: '',
      testResultType: 'success',
      // Provider models
      providerModels: {
        bailian: ['qwen-turbo', 'qwen-plus', 'qwen-max', 'qwen-long', 'qwen-vl-max'],
        openai: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o'],
        deepseek: ['deepseek-chat', 'deepseek-coder'],
        siliconflow: ['Qwen/Qwen2.5-72B-Instruct'],
      }
    }
  },
  mounted() { this.loadConfigs() },
  methods: {
    async loadConfigs() {
      try {
        const { data } = await request.get('/api/llm/configs')
        if (data.code === 200) {
          this.configs = data.data.configs || []
          this.stats = data.data.stats || {}
        }
      } catch (e) { /* ignore */ }
    },
    showAddDialog() {
      this.dialogTitle = '添加模型'
      this.form = { name: '', provider: 'bailian', api_key: '', model: '' }
      this.onProviderChange()
      this.dialogVisible = true
    },
    onProviderChange() {
      this.availableModels = this.providerModels[this.form.provider] || []
      if (this.availableModels.length) {
        this.form.model = this.availableModels[0]
      }
    },
    async saveConfig() {
      try {
        const { data } = await request.post('/api/llm/configs', this.form)
        if (data.code === 200) {
          this.$message.success('配置已添加')
          this.dialogVisible = false
          this.loadConfigs()
        } else {
          this.$message.error(data.message)
        }
      } catch (e) {
        this.$message.error('保存失败')
      }
    },
    editConfig(row) {
      this.dialogTitle = '编辑模型'
      this.form = { name: row.name, provider: row.provider, api_key: '', model: row.model }
      this.dialogVisible = true
    },
    async switchTo(name) {
      try {
        const { data } = await request.post(`/api/llm/switch/${name}`)
        if (data.code === 200) {
          this.$message.success('已切换')
          this.loadConfigs()
        }
      } catch (e) { this.$message.error('切换失败') }
    },
    async deleteConfig(name) {
      try {
        const { data } = await request.delete(`/api/llm/configs/${name}`)
        if (data.code === 200) {
          this.$message.success('已删除')
          this.loadConfigs()
        }
      } catch (e) { this.$message.error('删除失败') }
    },
    // Test connection
    testConnection() {
      this.testResult = ''
      this.testDialogVisible = true
      this.onTestProviderChange()
    },
    onTestProviderChange() {
      const models = this.providerModels[this.testForm.provider] || []
      if (models.length) this.testForm.model = models[0]
    },
    async doTest() {
      this.testLoading = true
      this.testResult = ''
      try {
        const { data } = await request.post('/api/llm/test', this.testForm)
        if (data.code === 200) {
          this.testResult = '✅ 连接成功！'
          this.testResultType = 'success'
        } else {
          this.testResult = '❌ ' + data.message
          this.testResultType = 'error'
        }
      } catch (e) {
        this.testResult = '❌ 连接失败: ' + e.message
        this.testResultType = 'error'
      } finally {
        this.testLoading = false
      }
    }
  }
}
</script>

<style scoped>
.llm-config-panel { padding: 12px; }
</style>
