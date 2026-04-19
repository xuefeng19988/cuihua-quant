<template>
  <div class="ai-center">
    <!-- 顶部标签页 -->
    <el-tabs v-model="activeTab" type="border-card">
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

export default {
  name: 'AICenter',
  components: { AIChat, AIStockAnalyze, AINoteAnalyze, AIMarketSummary, LLMConfigManager, AIStockFeatures },
  data() { return { activeTab: 'chat' } },
  watch: {
    '$route.query.tab': { handler(v) { if (v) this.activeTab = v }, immediate: true },
    activeTab(v) {
      this.$router.replace({ path: this.$route.path, query: { tab: v } })
    }
  },
  mounted() {
    const tab = this.$route.path.split('/').pop()
    if (['chat', 'stock', 'note', 'market', 'config'].includes(tab)) {
      this.activeTab = tab
    }
  }
}
</script>

<style scoped>
.ai-center { padding: 20px; }
</style>
