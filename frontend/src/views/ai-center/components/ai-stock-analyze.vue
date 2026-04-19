<template>
  <div class="ai-stock-panel">
    <el-row :gutter="16" style="margin-bottom:16px;">
      <el-col :span="8">
        <el-select v-model="selectedStock" filterable placeholder="选择股票" style="width:100%;">
          <el-option v-for="s in stockList" :key="s.code" :label="`${s.name} (${s.code})`" :value="s" />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-button type="primary" @click="analyzeStock" :loading="loading">🔍 AI 分析</el-button>
      </el-col>
    </el-row>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=''" style="margin-bottom:16px;" />

    <div v-if="result" class="analysis-result">
      <el-card>
        <div slot="header">
          <span>📊 分析结果 - {{ selectedStock.name }}</span>
          <span style="float:right;color:#909399;font-size:12px;">模型: {{ result.model }}</span>
        </div>
        <div class="result-content" v-html="formatResult(result.content)" />
        <div v-if="result.usage" style="margin-top:12px;padding-top:12px;border-top:1px solid #ebeef5;">
          <span style="font-size:12px;color:#909399;">
            用量: {{ result.usage.total_tokens }} tokens
          </span>
        </div>
      </el-card>
    </div>

    <el-empty v-else description="选择股票并点击 AI 分析" />
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'AIStockAnalyze',
  data() {
    return {
      stockList: [],
      selectedStock: null,
      loading: false,
      result: null,
      error: ''
    }
  },
  mounted() {
    this.loadStocks()
    // Auto-select from URL query params
    const { code, name } = this.$route.query
    if (code) {
      this.selectedStock = { code, name: name || code }
      this.analyzeStock()
    }
  },
  methods: {
    async loadStocks() {
      try {
        const { data } = await request.get('/api/stocks?limit=50')
        if (data.code === 200) {
          this.stockList = data.data.stocks || []
        }
      } catch (e) { /* use fallback */ }
      if (!this.stockList.length) {
        this.stockList = [
          { code: 'sh600519', name: '贵州茅台' },
          { code: 'sz000858', name: '五粮液' },
          { code: 'hk00700', name: '腾讯控股' },
          { code: 'hk09988', name: '阿里巴巴' },
          { code: 'sz300750', name: '宁德时代' },
        ]
      }
    },
    async analyzeStock() {
      if (!this.selectedStock) { this.error = '请选择股票'; return }
      this.loading = true
      this.error = ''
      try {
        const { data } = await request.post('/api/ai/analyze-stock', {
          code: this.selectedStock.code,
          name: this.selectedStock.name,
          score: 60
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
    formatResult(text) {
      return text.replace(/\n/g, '<br/>')
    }
  }
}
</script>

<style scoped>
.ai-stock-panel { padding: 12px; }
.result-content { font-size: 14px; line-height: 1.8; }
</style>
