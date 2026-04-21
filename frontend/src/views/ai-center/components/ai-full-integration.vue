/**
 * Phase 314-320: AI 全面融合前端
 * AI选股2.0、个股深度分析、图表增强、笔记增强、系统融合、研究报告
 */
<template>
  <div class="ai-full-integration">
    <el-tabs v-model="activeTab" type="border-card">
      
      <!-- Phase 314: AI 选股 2.0 -->
      <el-tab-pane label="🎯 AI选股2.0" name="stock-v2">
        <el-row :gutter="16">
          <el-col :span="16">
            <el-card>
              <div slot="header">🎯 AI 自然语言选股</div>
              <el-input v-model="screenQuery" placeholder="描述你的选股条件，如：最近放量突破的股票"
                @keyup.enter.native="runScreen" />
              <el-button type="primary" @click="runScreen" :loading="screenLoading" style="margin-top:8px;">
                🔍 AI 选股
              </el-button>
              <div v-if="screenResults.length">
                <el-table :data="screenResults" stripe border style="margin-top:12px;">
                  <el-table-column prop="code" label="代码" width="100" />
                  <el-table-column prop="name" label="名称" width="120" />
                  <el-table-column prop="price" label="价格" width="80" />
                  <el-table-column prop="change" label="涨跌幅" width="100">
                    <template slot-scope="{row}">
                      <span :style="{color: row.change>0?'#ef232a':'#14b143'}">{{row.change}}%</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="reason" label="入选理由" />
                </el-table>
                <div style="margin-top:12px;padding:12px;background:#f5f7fa;border-radius:8px;">
                  💡 {{ screenSummary }}
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <div slot="header">📊 板块轮动预测</div>
              <div v-for="s in sectorForecast" :key="s.name" class="sector-item">
                <div class="sector-name">{{ s.name }}</div>
                <el-progress :percentage="s.score" :color="sectorColor(s.score)" :stroke-width="10" />
                <el-tag size="mini" :type="sectorType(s.signal)">{{ s.signal }}</el-tag>
              </div>
              <div style="margin-top:8px;padding:8px;background:#f5f7fa;border-radius:4px;font-size:12px;">
                💡 {{ sectorComment }}
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Phase 315: AI 个股深度分析 -->
      <el-tab-pane label="🔍 深度分析" name="deep-analysis">
        <el-row :gutter="16">
          <el-col :span="24">
            <el-input v-model="deepCode" placeholder="输入股票代码，如：688256" style="width:200px;margin-right:8px;" />
            <el-button type="primary" @click="runDeepAnalysis" :loading="deepLoading">🔍 深度分析</el-button>
          </el-col>
        </el-row>
        <el-row :gutter="16" style="margin-top:16px;" v-if="deepData">
          <el-col :span="12">
            <el-card>
              <div slot="header">🏭 产业链分析</div>
              <div v-if="deepData.industryChain">
                <div class="chain-section">
                  <div class="chain-label">上游</div>
                  <el-tag v-for="u in deepData.industryChain.upstream" :key="u.name" size="small" style="margin:4px;">
                    {{ u.name }}: {{ u.companies.join(', ') }}
                  </el-tag>
                </div>
                <div class="chain-section">
                  <div class="chain-label">中游</div>
                  <el-tag v-for="m in deepData.industryChain.midstream" :key="m.name" size="small" type="success" style="margin:4px;">
                    {{ m.name }}: {{ m.companies.join(', ') }}
                  </el-tag>
                </div>
                <div class="chain-section">
                  <div class="chain-label">下游</div>
                  <el-tag v-for="d in deepData.industryChain.downstream" :key="d.name" size="small" type="warning" style="margin:4px;">
                    {{ d.name }}: {{ d.companies.join(', ') }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <div slot="header">💰 AI 估值模型</div>
              <div v-if="deepData.valuation">
                <el-table :data="valuationTable" stripe border size="mini">
                  <el-table-column prop="model" label="模型" width="80" />
                  <el-table-column prop="value" label="估值" width="80" />
                  <el-table-column prop="premium" label="溢价" width="80">
                    <template slot-scope="{row}">
                      <span :style="{color: row.premium.includes('+')?'#ef232a':'#14b143'}">{{row.premium}}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="comment" label="说明" />
                </el-table>
                <div style="margin-top:8px;text-align:center;">
                  <strong>综合估值: {{ deepData.valuation.composite_value }}</strong>
                  <span :style="{color: deepData.valuation.composite_premium.includes('+')?'#ef232a':'#14b143'}">
                    ({{ deepData.valuation.composite_premium }})
                  </span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Phase 316: AI 图表增强 -->
      <el-tab-pane label="📊 图表增强" name="chart-enhanced">
        <el-card>
          <div slot="header">📊 AI 图表增强功能</div>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-button type="primary" @click="runDrawLines" style="width:100%;">✏️ AI 自动画线</el-button>
            </el-col>
            <el-col :span="8">
              <el-button type="success" @click="runVolumePrice" style="width:100%;">📈 AI 量价分析</el-button>
            </el-col>
            <el-col :span="8">
              <el-button type="warning" @click="runWaveAnalysis" style="width:100%;">🌊 AI 波浪理论</el-button>
            </el-col>
          </el-row>
          <div v-if="chartEnhancedData" style="margin-top:16px;">
            <el-alert :title="chartEnhancedData.ai_comment" type="info" show-icon />
          </div>
        </el-card>
      </el-tab-pane>

      <!-- Phase 317: AI 笔记增强 -->
      <el-tab-pane label="📝 笔记增强" name="note-enhanced">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-card>
              <div slot="header">📝 AI 自动生成复盘</div>
              <el-button type="primary" @click="generateDailyNote" :loading="noteLoading">
                🤖 生成今日复盘
              </el-button>
              <div v-if="dailyNote" style="margin-top:12px;" v-html="formatNote(dailyNote)" />
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <div slot="header">🔄 AI 交易复盘</div>
              <el-button type="success" @click="runTradeReview" :loading="reviewLoading">
                📊 交易复盘
              </el-button>
              <div v-if="tradeReview" style="margin-top:12px;">
                <el-row :gutter="12">
                  <el-col :span="6"><el-statistic title="胜率" :value="tradeReview.review.win_rate" /></el-col>
                  <el-col :span="6"><el-statistic title="平均盈利" :value="tradeReview.review.avg_profit" /></el-col>
                  <el-col :span="6"><el-statistic title="盈亏比" :value="tradeReview.review.profit_loss_ratio" /></el-col>
                </el-row>
                <div style="margin-top:8px;" v-for="s in tradeReview.ai_suggestions" :key="s" class="suggestion-item">
                  💡 {{ s }}
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Phase 318: AI 系统融合 -->
      <el-tab-pane label="🔗 系统融合" name="system-fusion">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-card>
              <div slot="header">💬 AI 自然语言查询</div>
              <el-input v-model="nlQuery" placeholder="用自然语言查询，如：帮我找出最近放量突破的股票"
                @keyup.enter.native="runNLQuery" />
              <el-button type="primary" @click="runNLQuery" :loading="nlLoading" style="margin-top:8px;">
                🔍 查询
              </el-button>
              <div v-if="nlResults.length" style="margin-top:12px;">
                <el-table :data="nlResults" stripe border size="mini">
                  <el-table-column v-for="col in nlColumns" :key="col" :prop="col" :label="col" />
                </el-table>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <div slot="header">🤖 AI 策略市场</div>
              <el-button type="success" @click="loadStrategyMarket">📊 加载策略</el-button>
              <div v-if="strategies.length" style="margin-top:12px;">
                <el-card v-for="s in strategies" :key="s.id" shadow="hover" style="margin-bottom:8px;">
                  <div class="strategy-card-header">
                    <span class="strategy-card-name">{{ s.name }}</span>
                    <el-tag size="mini" type="success">{{ s.backtest_return }}</el-tag>
                  </div>
                  <div class="strategy-card-desc">{{ s.description }}</div>
                  <el-row :gutter="8" style="margin-top:8px;">
                    <el-col :span="8">夏普: {{ s.sharpe }}</el-col>
                    <el-col :span="8">胜率: {{ s.win_rate }}</el-col>
                    <el-col :span="8">最大回撤: {{ s.max_drawdown }}</el-col>
                  </el-row>
                </el-card>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Phase 319: AI 研究报告 -->
      <el-tab-pane label="📚 研究报告" name="research">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-card>
              <div slot="header">🏭 行业研究</div>
              <el-select v-model="researchIndustry" style="width:100%;margin-bottom:8px;">
                <el-option label="半导体" value="半导体" />
                <el-option label="新能源车" value="新能源车" />
                <el-option label="AI算力" value="AI算力" />
              </el-select>
              <el-button type="primary" @click="generateIndustryReport" :loading="researchLoading">
                📊 生成报告
              </el-button>
              <div v-if="industryReport" style="margin-top:12px;">
                <h4>{{ industryReport.report.title }}</h4>
                <el-tag :type="industryReport.report.rating === '增持' ? 'success' : 'warning'" size="small">
                  {{ industryReport.report.rating }}
                </el-tag>
                <p>{{ industryReport.report.summary }}</p>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <div slot="header">📊 策略周报</div>
              <el-button type="success" @click="loadWeeklyReport">📈 加载周报</el-button>
              <div v-if="weeklyReport" style="margin-top:12px;">
                <h4>{{ weeklyReport.report.title }}</h4>
                <p><strong>市场回顾:</strong> {{ weeklyReport.report.market_review }}</p>
                <p><strong>下周策略:</strong> {{ weeklyReport.report.next_week_strategy.outlook }}</p>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <div slot="header">🌍 宏观分析</div>
              <el-button type="warning" @click="loadMacroReport">📊 加载宏观</el-button>
              <div v-if="macroReport" style="margin-top:12px;">
                <el-table :data="macroIndicators" stripe border size="mini">
                  <el-table-column prop="name" label="指标" width="80" />
                  <el-table-column prop="value" label="数值" width="80" />
                  <el-table-column prop="trend" label="趋势" width="80" />
                  <el-table-column prop="comment" label="解读" />
                </el-table>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'AIFullIntegration',
  data() {
    return {
      activeTab: 'stock-v2',
      // 314 选股 2.0
      screenQuery: '', screenLoading: false, screenResults: [], screenSummary: '',
      sectorForecast: [], sectorComment: '',
      // 315 深度分析
      deepCode: '688256', deepLoading: false, deepData: null,
      // 316 图表增强
      chartEnhancedData: null,
      // 317 笔记增强
      dailyNote: '', noteLoading: false, tradeReview: null, reviewLoading: false,
      // 318 系统融合
      nlQuery: '', nlLoading: false, nlResults: [], nlColumns: [],
      strategies: [],
      // 319 研究报告
      researchIndustry: '半导体', researchLoading: false, industryReport: null,
      weeklyReport: null, macroReport: null, macroIndicators: [],
    }
  },
  computed: {
    valuationTable() {
      if (!this.deepData || !this.deepData.valuation) return []
      return Object.entries(this.deepData.valuation.models).map(([k, v]) => ({
        model: k, value: v.value, premium: v.premium, comment: v.comment
      }))
    },
    sectorColor(score) {
      return score > 80 ? '#67c23a' : score > 60 ? '#e6a23c' : '#f56c6c'
    },
    sectorType(signal) {
      return signal === '买入' ? 'success' : signal === '关注' ? 'warning' : 'info'
    }
  },
  methods: {
    formatNote(note) {
      return (note || '').replace(/\n/g, '<br/>')
    },
    
    // Phase 314: AI 选股 2.0
    async runScreen() {
      if (!this.screenQuery) return this.$message.warning('请输入选股条件')
      this.screenLoading = true
      try {
        const { data } = await request.post('/ai/stock-screen', { query: this.screenQuery })
        if (data.code === 200) {
          this.screenResults = data.data.results
          this.screenSummary = data.data.ai_summary
        }
      } catch (e) { this.$message.error('选股失败') }
      finally { this.screenLoading = false }
    },
    async loadSectorForecast() {
      try {
        const { data } = await request.get('/ai/sector-forecast')
        if (data.code === 200) {
          this.sectorForecast = data.data.sectors
          this.sectorComment = data.data.ai_comment
        }
      } catch (e) {}
    },
    
    // Phase 315: 深度分析
    async runDeepAnalysis() {
      if (!this.deepCode) return this.$message.warning('请输入股票代码')
      this.deepLoading = true
      try {
        const [chain, val] = await Promise.all([
          request.get(`/ai/industry-chain/${this.deepCode}`),
          request.get(`/ai/valuation/${this.deepCode}`)
        ])
        this.deepData = {
          industryChain: chain.data.data,
          valuation: val.data.data
        }
      } catch (e) { this.$message.error('分析失败') }
      finally { this.deepLoading = false }
    },
    
    // Phase 316: 图表增强
    async runDrawLines() {
      try {
        const { data } = await request.post('/ai/chart/draw-lines', {})
        if (data.code === 200) this.chartEnhancedData = data.data
      } catch (e) {}
    },
    async runVolumePrice() {
      try {
        const { data } = await request.post('/ai/chart/volume-price', {})
        if (data.code === 200) this.chartEnhancedData = data.data
      } catch (e) {}
    },
    async runWaveAnalysis() {
      try {
        const { data } = await request.post('/ai/chart/wave-analysis', {})
        if (data.code === 200) this.chartEnhancedData = data.data
      } catch (e) {}
    },
    
    // Phase 317: 笔记增强
    async generateDailyNote() {
      this.noteLoading = true
      try {
        const { data } = await request.post('/ai/note/auto-generate', { date: '今日' })
        if (data.code === 200) this.dailyNote = data.data.content
      } catch (e) { this.$message.error('生成失败') }
      finally { this.noteLoading = false }
    },
    async runTradeReview() {
      this.reviewLoading = true
      try {
        const { data } = await request.post('/ai/note/trade-review', { trades: [] })
        if (data.code === 200) this.tradeReview = data.data
      } catch (e) { this.$message.error('复盘失败') }
      finally { this.reviewLoading = false }
    },
    
    // Phase 318: 系统融合
    async runNLQuery() {
      if (!this.nlQuery) return this.$message.warning('请输入查询')
      this.nlLoading = true
      try {
        const { data } = await request.post('/ai/nl-query', { query: this.nlQuery })
        if (data.code === 200) {
          this.nlResults = data.data.results
          this.nlColumns = this.nlResults.length ? Object.keys(this.nlResults[0]) : []
        }
      } catch (e) { this.$message.error('查询失败') }
      finally { this.nlLoading = false }
    },
    async loadStrategyMarket() {
      try {
        const { data } = await request.get('/ai/strategy-market')
        if (data.code === 200) this.strategies = data.data.strategies
      } catch (e) {}
    },
    
    // Phase 319: 研究报告
    async generateIndustryReport() {
      this.researchLoading = true
      try {
        const { data } = await request.post('/ai/research/industry', { industry: this.researchIndustry })
        if (data.code === 200) this.industryReport = data.data
      } catch (e) { this.$message.error('生成失败') }
      finally { this.researchLoading = false }
    },
    async loadWeeklyReport() {
      try {
        const { data } = await request.get('/ai/research/weekly')
        if (data.code === 200) this.weeklyReport = data.data
      } catch (e) {}
    },
    async loadMacroReport() {
      try {
        const { data } = await request.get('/ai/research/macro')
        if (data.code === 200) {
          this.macroReport = data.data
          this.macroIndicators = Object.entries(data.data.report.indicators).map(([k, v]) => ({
            name: k, ...v
          }))
        }
      } catch (e) {}
    },
    
    // Init
    mounted() {
      this.loadSectorForecast()
    }
  }
}
</script>

<style scoped>
.ai-full-integration { padding: 16px; }
.sector-item { margin-bottom: 12px; }
.sector-name { font-weight: bold; margin-bottom: 4px; }
.chain-section { margin-bottom: 8px; }
.chain-label { font-weight: bold; font-size: 12px; color: #909399; margin-bottom: 4px; }
.strategy-card-header { display: flex; justify-content: space-between; align-items: center; }
.strategy-card-name { font-weight: bold; }
.strategy-card-desc { font-size: 12px; color: #909399; }
.suggestion-item { padding: 4px 0; font-size: 13px; color: #606266; }
</style>
