<template>
  <div class="ai-stock-features">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- Phase 282: AI 选股 -->
      <el-tab-pane label="🤖 AI 选股" name="pick">
        <el-card>
          <div slot="header">🤖 AI 智能选股</div>
          <el-form :inline="true" size="small">
            <el-form-item label="投资风格">
              <el-select v-model="pickForm.style" style="width:120px;">
                <el-option label="均衡型" value="balanced" />
                <el-option label="激进型" value="aggressive" />
                <el-option label="保守型" value="conservative" />
              </el-select>
            </el-form-item>
            <el-form-item label="推荐数量">
              <el-input-number v-model="pickForm.top_n" :min="3" :max="20" style="width:100px;" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="runStockPick" :loading="pickLoading">🔍 开始选股</el-button>
            </el-form-item>
          </el-form>
          <div v-if="pickResult" class="pick-result" v-html="sanitizeHTML(formatText(pickResult))" />
          <el-empty v-else description="选择风格并点击开始选股" />
        </el-card>
      </el-tab-pane>

      <!-- Phase 283: 异动解读 -->
      <el-tab-pane label="📈 异动解读" name="anomaly">
        <el-card>
          <div slot="header">📈 异动 AI 解读</div>
          <el-form :inline="true" size="small">
            <el-form-item label="股票代码">
              <el-input v-model="anomalyForm.code" placeholder="sh600519" style="width:150px;" />
            </el-form-item>
            <el-form-item label="涨跌幅%">
              <el-input-number v-model="anomalyForm.change_pct" style="width:100px;" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="runAnomaly" :loading="anomalyLoading">🔍 解读</el-button>
            </el-form-item>
          </el-form>
          <div v-if="anomalyResult" class="anomaly-result" v-html="sanitizeHTML(formatText(anomalyResult))" />
          <el-empty v-else description="输入股票代码并点击解读" />
        </el-card>
      </el-tab-pane>

      <!-- Phase 284: 持仓诊断 -->
      <el-tab-pane label="📊 持仓诊断" name="portfolio">
        <el-card>
          <div slot="header">📊 持仓 AI 诊断</div>
          <el-button type="primary" size="small" @click="runPortfolioDiagnosis" :loading="portfolioLoading">🔍 诊断持仓</el-button>
          <div v-if="portfolioResult" class="portfolio-result" v-html="sanitizeHTML(formatText(portfolioResult))" />
          <el-empty v-else description="点击诊断持仓" />
        </el-card>
      </el-tab-pane>

      <!-- Phase 285: 新闻摘要 -->
      <el-tab-pane label="📰 新闻摘要" name="news">
        <el-card>
          <div slot="header">📰 新闻 AI 摘要</div>
          <el-button type="primary" size="small" @click="runNewsSummary" :loading="newsLoading">🔍 生成摘要</el-button>
          <div v-if="newsResults.length">
            <el-collapse v-model="activeNews">
              <el-collapse-item v-for="(n, i) in newsResults" :key="i" :title="n.title" :name="i">
                <div v-html="sanitizeHTML(formatText(n.analysis))" />
              </el-collapse-item>
            </el-collapse>
          </div>
          <el-empty v-else description="点击生成摘要" />
        </el-card>
      </el-tab-pane>

      <!-- Phase 287: 研报中心 -->
      <el-tab-pane label="📋 研报中心" name="research">
        <el-card>
          <div slot="header">📋 AI 研报生成</div>
          <el-form :inline="true" size="small">
            <el-form-item label="股票代码">
              <el-input v-model="researchForm.code" placeholder="sh600519" style="width:150px;" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="runResearch" :loading="researchLoading">📄 生成研报</el-button>
            </el-form-item>
          </el-form>
          <div v-if="researchResult" class="research-result">
            <el-card>
              <div slot="header">
                <span>研报: {{ researchForm.code }}</span>
                <span style="float:right;font-size:12px;color:#909399;">{{ researchGeneratedAt }}</span>
              </div>
              <div v-html="sanitizeHTML(formatText(researchResult))" />
            </el-card>
          </div>
          <el-empty v-else description="输入股票代码并生成研报" />
        </el-card>
      </el-tab-pane>

      <!-- Phase 289: 风险预警 -->
      <el-tab-pane label="📉 风险预警" name="risk">
        <el-card>
          <div slot="header">📉 风险预警 AI</div>
          <el-form :inline="true" size="small">
            <el-form-item label="股票代码">
              <el-input v-model="riskForm.code" placeholder="sh600519" style="width:150px;" />
            </el-form-item>
            <el-form-item>
              <el-button type="danger" @click="runRiskAlert" :loading="riskLoading">⚠️ 风险检查</el-button>
            </el-form-item>
          </el-form>
          <div v-if="riskResult">
            <el-alert :title="`风险等级: ${riskResult.risk_level}`" :type="riskResult.risk_level === '高' ? 'error' : riskResult.risk_level === '中' ? 'warning' : 'success'" show-icon style="margin-bottom:12px;" />
            <el-card>
              <div v-html="sanitizeHTML(formatText(riskResult.advice))" />
            </el-card>
          </div>
          <el-empty v-else description="输入股票代码并检查风险" />
        </el-card>
      </el-tab-pane>

      <!-- Phase 290: 板块分析 -->
      <el-tab-pane label="🏢 板块分析" name="sector">
        <el-card>
          <div slot="header">🏢 板块 AI 分析</div>
          <el-form :inline="true" size="small">
            <el-form-item label="板块名称">
              <el-input v-model="sectorForm.sector" placeholder="如: 新能源" style="width:150px;" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="runSectorAnalysis" :loading="sectorLoading">🔍 分析板块</el-button>
            </el-form-item>
          </el-form>
          <div v-if="sectorResult" class="sector-result" v-html="sanitizeHTML(formatText(sectorResult))" />
          <el-empty v-else description="输入板块名称并分析" />
        </el-card>
      </el-tab-pane>

      <!-- Phase 293: 交易日志 -->
      <el-tab-pane label="📝 交易日志" name="journal">
        <el-card>
          <div slot="header">📝 AI 交易日志</div>
          <el-button type="primary" size="small" @click="runJournal" :loading="journalLoading">📝 生成日志</el-button>
          <div v-if="journalResult" class="journal-result" v-html="sanitizeHTML(formatText(journalResult))" />
          <el-empty v-else description="点击生成今日交易日志" />
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import request from '@/utils/request'
import sanitizeMixin from '@/mixins/sanitize'

export default {
  mixins: [sanitizeMixin],
  name: 'AIStockFeatures',
  data() {
    return {
      activeTab: 'pick',
      // 282 选股
      pickForm: { style: 'balanced', top_n: 10, criteria: '' },
      pickLoading: false, pickResult: '',
      // 283 异动
      anomalyForm: { code: '', name: '', change_pct: 0 },
      anomalyLoading: false, anomalyResult: '',
      // 284 持仓诊断
      portfolioLoading: false, portfolioResult: '',
      // 285 新闻
      newsLoading: false, newsResults: [], activeNews: [],
      // 287 研报
      researchForm: { code: '' },
      researchLoading: false, researchResult: '', researchGeneratedAt: '',
      // 289 风险
      riskForm: { code: '' },
      riskLoading: false, riskResult: null,
      // 290 板块
      sectorForm: { sector: '' },
      sectorLoading: false, sectorResult: '',
      // 293 日志
      journalLoading: false, journalResult: '',
    }
  },
  methods: {
    formatText(t) { return (t || '').replace(/\n/g, '<br/>') },

    // Phase 282: AI 选股
    async runStockPick() {
      this.pickLoading = true
      try {
        const { data } = await request.post('/ai/stock-pick', this.pickForm)
        this.pickResult = data.code === 200 ? data.data.picks : data.message
      } catch (e) { this.pickResult = '请求失败: ' + e.message }
      finally { this.pickLoading = false }
    },

    // Phase 283: 异动解读
    async runAnomaly() {
      if (!this.anomalyForm.code) return this.$message.warning('请输入股票代码')
      this.anomalyLoading = true
      try {
        const { data } = await request.post('/ai/analyze-anomaly', this.anomalyForm)
        this.anomalyResult = data.code === 200 ? data.data.analysis : data.message
      } catch (e) { this.anomalyResult = '请求失败: ' + e.message }
      finally { this.anomalyLoading = false }
    },

    // Phase 284: 持仓诊断
    async runPortfolioDiagnosis() {
      this.portfolioLoading = true
      try {
        const positions = [] // TODO: 从真实持仓接口获取
        const { data } = await request.post('/ai/portfolio-diagnosis', { positions })
        this.portfolioResult = data.code === 200 ? data.data.diagnosis : data.message
      } catch (e) { this.portfolioResult = '请求失败: ' + e.message }
      finally { this.portfolioLoading = false }
    },

    // Phase 285: 新闻摘要
    async runNewsSummary() {
      this.newsLoading = true
      try {
        const news = [] // TODO: 从新闻接口获取
        const { data } = await request.post('/ai/news-summary', { news })
        if (data.code === 200) this.newsResults = data.data.summaries
      } catch (e) { this.$message.error('请求失败') }
      finally { this.newsLoading = false }
    },

    // Phase 287: 研报生成
    async runResearch() {
      if (!this.researchForm.code) return this.$message.warning('请输入股票代码')
      this.researchLoading = true
      try {
        const { data } = await request.post('/ai/generate-research', { code: this.researchForm.code })
        if (data.code === 200) {
          this.researchResult = data.data.report
          this.researchGeneratedAt = data.data.generated_at
        } else this.researchResult = data.message
      } catch (e) { this.researchResult = '请求失败: ' + e.message }
      finally { this.researchLoading = false }
    },

    // Phase 289: 风险预警
    async runRiskAlert() {
      if (!this.riskForm.code) return this.$message.warning('请输入股票代码')
      this.riskLoading = true
      try {
        const { data } = await request.post('/ai/risk-alert', { code: this.riskForm.code })
        if (data.code === 200) this.riskResult = data.data
        else this.$message.error(data.message)
      } catch (e) { this.$message.error('请求失败') }
      finally { this.riskLoading = false }
    },

    // Phase 290: 板块分析
    async runSectorAnalysis() {
      if (!this.sectorForm.sector) return this.$message.warning('请输入板块名称')
      this.sectorLoading = true
      try {
        const { data } = await request.post('/ai/sector-analysis', this.sectorForm)
        this.sectorResult = data.code === 200 ? data.data.analysis : data.message
      } catch (e) { this.sectorResult = '请求失败: ' + e.message }
      finally { this.sectorLoading = false }
    },

    // Phase 293: 交易日志
    async runJournal() {
      this.journalLoading = true
      try {
        const { data } = await request.post('/ai/trading-journal', { trades: [], market_summary: '' })
        this.journalResult = data.code === 200 ? data.data.journal : data.message
      } catch (e) { this.journalResult = '请求失败: ' + e.message }
      finally { this.journalLoading = false }
    },
  }
}
</script>

<style scoped>
.ai-stock-features { padding: 20px; }
.pick-result, .anomaly-result, .portfolio-result, .sector-result, .journal-result, .research-result { margin-top: 16px; }
.pick-result, .anomaly-result, .portfolio-result, .sector-result, .journal-result { padding: 12px; background: #f5f7fa; border-radius: 8px; line-height: 1.8; font-size: 14px; }
.research-result >>> .el-card__body { line-height: 1.8; font-size: 14px; white-space: pre-wrap; }
</style>
