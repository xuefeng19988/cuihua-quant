<template>
  <div class="ai-note-panel">
    <el-row :gutter="16" style="margin-bottom:16px;">
      <el-col :span="8">
        <el-select v-model="selectedNote" filterable placeholder="选择笔记" style="width:100%;">
          <el-option v-for="n in noteList" :key="n.id" :label="n.title" :value="n" />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-button type="primary" @click="analyzeNote" :loading="loading">🔍 AI 分析</el-button>
      </el-col>
      <el-col :span="4">
        <el-button type="warning" @click="generateReport" :loading="loading">📄 生成研报</el-button>
      </el-col>
    </el-row>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=''" style="margin-bottom:16px;" />

    <div v-if="result" class="analysis-result">
      <el-card>
        <div slot="header">
          <span>📝 笔记 AI 分析</span>
        </div>
        <div class="result-content" v-html="formatResult(result.content)" />
        <div v-if="result.usage" style="margin-top:12px;padding-top:12px;border-top:1px solid #ebeef5;">
          <span style="font-size:12px;color:#909399;">用量: {{ result.usage.total_tokens }} tokens</span>
        </div>
      </el-card>
    </div>

    <el-empty v-else description="选择笔记并点击 AI 分析或生成研报" />
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'AINoteAnalyze',
  data() {
    return {
      noteList: [],
      selectedNote: null,
      loading: false,
      result: null,
      error: ''
    }
  },
  mounted() { this.loadNotes() },
  methods: {
    async loadNotes() {
      try {
        const { data } = await request.get('/api/notes')
        if (data.code === 200) {
          this.noteList = (data.data.notes || []).slice(0, 50)
        }
      } catch (e) { /* fallback */ }
      if (!this.noteList.length) {
        this.noteList = [
          { id: 1, title: '2024年投资策略笔记' },
          { id: 2, title: '新能源行业分析' },
          { id: 3, title: '科技股估值研究' },
        ]
      }
    },
    async analyzeNote() {
      if (!this.selectedNote) { this.error = '请选择笔记'; return }
      this.loading = true
      this.error = ''
      try {
        const { data } = await request.post('/api/ai/chat', {
          question: `请分析以下笔记的核心观点，并给出投资建议：\n\n${this.selectedNote.title}`
        })
        if (data.code === 200) {
          this.result = data.data
        } else {
          this.error = data.message
        }
      } catch (e) {
        this.error = '分析请求失败: ' + e.message
      } finally {
        this.loading = false
      }
    },
    async generateReport() {
      if (!this.selectedNote) { this.error = '请选择笔记'; return }
      this.loading = true
      this.error = ''
      try {
        const { data } = await request.post('/api/ai/generate-report', {
          context: `笔记标题: ${this.selectedNote.title}\n\n请基于该笔记生成一份专业研报。`
        })
        if (data.code === 200) {
          this.result = data.data
        } else {
          this.error = data.message
        }
      } catch (e) {
        this.error = '研报生成失败: ' + e.message
      } finally {
        this.loading = false
      }
    },
    formatResult(text) {
      return text.replace(/\n/g, '<br/>')
    }
  }
}
</script>

<style scoped>
.ai-note-panel { padding: 12px; }
.result-content { font-size: 14px; line-height: 1.8; }
</style>
