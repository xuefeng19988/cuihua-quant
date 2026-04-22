<template>
  <div class="ai-center">
    <!-- 顶部标签页 -->
    <el-tabs :key="$route.fullPath" v-model="activeTab" type="border-card">
      <el-tab-pane label="🤖 AI 对话" name="chat">
        <ai-chat />
      </el-tab-pane>
      <el-tab-pane label="📈 个股分析" name="stock">
        <ai-stock-analyze />
      </el-tab-pane>
      <el-tab-pane label="📝 笔记分析" name="note">
        <ai-note-analyze />
      </el-tab-pane>
      <el-tab-pane label="📊 市场总结" name="market">
        <ai-market-summary />
      </el-tab-pane>
      <el-tab-pane label="⚙️ 模型管理" name="config">
        <llm-config-manager />
      </el-tab-pane>
      <el-tab-pane label="🤖 股票 AI" name="stock-ai">
        <ai-stock-features />
      </el-tab-pane>
      <el-tab-pane label="🚀 深度集成" name="extended">
        <ai-extended-features />
      </el-tab-pane>
      <el-tab-pane label="📊 AI图表" name="chart-demo">
        <ai-chart-demo />
      </el-tab-pane>
      <el-tab-pane label="🚀 AI融合" name="full-integration">
        <ai-full-integration />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import AIChat from './components/ai-chat.vue'
import AIStockAnalyze from './components/ai-stock-analyze.vue'
import AINoteAnalyze from './components/ai-note-analyze.vue'
import AIMarketSummary from './components/ai-market-summary.vue'
import LLMConfigManager from './components/llm-config-manager.vue'
import AIStockFeatures from './components/ai-stock-features.vue'
import AIExtendedFeatures from './components/ai-extended.vue'
import AIChartDemo from './components/ai-chart-demo.vue'
import AIFullIntegration from './components/ai-full-integration.vue'

export default {
  name: 'AICenter',
  components: { AIChat, AIStockAnalyze, AINoteAnalyze, AIMarketSummary, LLMConfigManager, AIStockFeatures, AIExtendedFeatures, AIChartDemo, AIFullIntegration },
  data() { return { activeTab: 'chat' } },
  watch: {
    '$route.path': {
      handler(v) {
        const tab = v.split('/').pop()
        const valid = ['chat', 'stock', 'note', 'market', 'config', 'stock-ai', 'extended', 'chart-demo', 'full-integration']
        console.log('[AI-Center] watch $route.path:', v, '→ tab:', tab, 'activeTab before:', this.activeTab)
        if (valid.includes(tab)) {
          this.activeTab = tab
          console.log('[AI-Center] activeTab after:', this.activeTab)
        }
      },
      immediate: true
    }
  },
  beforeRouteUpdate(to, from, next) {
    const tab = to.path.split('/').pop()
    const valid = ['chat', 'stock', 'note', 'market', 'config', 'stock-ai', 'extended', 'chart-demo', 'full-integration']
    console.log('[AI-Center] beforeRouteUpdate from:', from.path, 'to:', to.path, '→ tab:', tab)
    if (valid.includes(tab)) {
      this.activeTab = tab
    }
    next()
  },
  created() {
    const tab = this.$route.path.split('/').pop()
    const valid = ['chat', 'stock', 'note', 'market', 'config', 'stock-ai', 'extended', 'chart-demo', 'full-integration']
    console.log('[AI-Center] created, path:', this.$route.path, '→ tab:', tab)
    if (valid.includes(tab)) {
      this.activeTab = tab
    }
  }
}
</script>

<style scoped>
.ai-center { padding: 20px; }
</style>
