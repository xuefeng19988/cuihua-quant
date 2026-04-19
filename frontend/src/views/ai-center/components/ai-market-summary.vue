<template>
  <div class="ai-market-panel">
    <el-button type="primary" @click="generateSummary" :loading="loading" size="small">📊 生成今日市场总结</el-button>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=''" style="margin:12px 0;" />

    <div v-if="result" style="margin-top:16px;">
      <el-card>
        <div slot="header">📊 AI 市场总结</div>
        <div class="summary-content" v-html="sanitizeHTML(formatResult(result.content))" />
        <div v-if="result.usage" style="margin-top:12px;font-size:12px;color:#909399;">
          用量: {{ result.usage.total_tokens }} tokens
        </div>
      </el-card>
    </div>

    <el-empty v-else description="点击按钮生成今日市场总结" />
  </div>
</template>

<script>
import request from '@/utils/request'
import sanitizeMixin from '@/mixins/sanitize'

export default {
  mixins: [sanitizeMixin],
  name: 'AIMarketSummary',
  data() {
    return { loading: false, result: null, error: '' }
  },
  methods: {
    async generateSummary() {
      this.loading = true
      this.error = ''
      const context = '今日A股市场数据：上证指数、深证成指、创业板指。板块热点：AI、新能源、半导体。资金流向：北向资金、主力净流入。'
      try {
        const { data } = await request.post('/api/ai/market-summary', { context })
        if (data.code === 200) {
          this.result = data.data
        } else {
          this.error = data.message
        }
      } catch (e) {
        this.error = '生成失败: ' + e.message
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
.ai-market-panel { padding: 12px; }
.summary-content { font-size: 14px; line-height: 1.8; }
</style>
