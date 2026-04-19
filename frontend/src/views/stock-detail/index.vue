<template>
  <div class="stock-detail-futu">
    <!-- 顶部行情栏 (仿Futu) -->
    <div class="quote-header" :class="priceChange >= 0 ? 'up' : 'down'">
      <div class="header-left">
        <h1 class="stock-name">{{ stockInfo.name || '-' }}</h1>
        <span class="stock-code">{{ stockInfo.code || '-' }}</span>
        <el-tag size="mini" class="market-tag">{{ stockInfo.market || '-' }}</el-tag>
      </div>
      <div class="header-center">
        <div class="current-price">{{ stockInfo.price || '-' }}</div>
        <div class="price-change">
          <span class="change-value">{{ priceChange >= 0 ? '+' : '' }}{{ priceChange }}</span>
          <span class="change-percent">({{ priceChangePercent >= 0 ? '+' : '' }}{{ priceChangePercent }}%)</span>
        </div>
      </div>
      <div class="header-right">
        <el-button size="mini" :type="isWatched ? 'warning' : ''" @click="toggleWatchlist">
          {{ isWatched ? '⭐ 已关注' : '☆ 关注' }}
        </el-button>
        <el-button size="mini" type="primary" @click="goToTrade">💹 交易</el-button>
      </div>
    </div>

    <!-- 子Tab切换 -->
    <div class="tab-bar">
      <el-tabs v-model="activeTab" type="card" @tab-click="onTabChange">
        <el-tab-pane label="📊 概览" name="overview" />
        <el-tab-pane label="📈 K线" name="kline" />
        <el-tab-pane label="📋 财务" name="financials" />
        <el-tab-pane label="🎯 评分" name="scoring" />
        <el-tab-pane label="📊 分析" name="analysis" />
        <el-tab-pane label="🤖 AI" name="ai" />
        <el-tab-pane label="📰 新闻" name="news" />
      </el-tabs>
    </div>

    <!-- 概览 Tab -->
    <div v-show="activeTab === 'overview'" class="tab-content">
      <el-row :gutter="16">
        <!-- 左侧: 分时图 + 盘口 -->
        <el-col :span="16">
          <!-- 分时图 -->
          <el-card class="futu-card">
            <div slot="header" class="card-header">
              <span>⏱️ 分时走势</span>
              <el-radio-group v-model="intradayPeriod" size="mini" @change="loadIntraday">
                <el-radio-button label="today">今日</el-radio-button>
                <el-radio-button label="5d">5日</el-radio-button>
              </el-radio-group>
            </div>
            <div id="intraday-chart" style="width:100%;height:350px;"></div>
          </el-card>

          <!-- 核心指标 -->
          <el-card class="futu-card" style="margin-top:16px;">
            <div slot="header"><span>📊 核心指标</span></div>
            <div class="metrics-grid">
              <div v-for="m in coreMetrics" :key="m.label" class="metric-item">
                <div class="metric-label">{{ m.label }}</div>
                <div class="metric-value" :class="m.colorClass">{{ m.value }}</div>
              </div>
            </div>
          </el-card>

          <!-- 技术指标摘要 -->
          <el-card class="futu-card" style="margin-top:16px;">
            <div slot="header"><span>📈 技术指标摘要</span></div>
            <el-table :data="indicatorSummary" size="small" stripe>
              <el-table-column prop="name" label="指标" width="100" />
              <el-table-column prop="value" label="数值" width="120" />
              <el-table-column prop="signal" label="信号" width="80">
                <template slot-scope="{ row }">
                  <el-tag size="mini" :type="row.signalType">{{ row.signal }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="desc" label="说明" />
            </el-table>
          </el-card>
        </el-col>

        <!-- 右侧: 盘口 + 交易统计 -->
        <el-col :span="8">
          <!-- 盘口 (买卖盘) -->
          <el-card class="futu-card">
            <div slot="header"><span>📋 买卖盘口</span></div>
            <div class="order-book">
              <!-- 卖盘 -->
              <div class="ask-side">
                <div v-for="level in askLevels" :key="'ask'+level.price" class="order-row">
                  <span class="order-label">卖{{ 5-level+1 }}</span>
                  <span class="order-price down">{{ level.price }}</span>
                  <span class="order-volume">{{ level.volume }}</span>
                  <div class="order-bar" :style="{ width: level.barWidth + '%', background: 'rgba(239,83,80,0.3)' }"></div>
                </div>
              </div>
              
              <!-- 最新价 -->
              <div class="current-price-row">
                <span class="price-label">最新</span>
                <span class="price-value" :class="priceChange >= 0 ? 'up' : 'down'">{{ stockInfo.price }}</span>
              </div>

              <!-- 买盘 -->
              <div class="bid-side">
                <div v-for="level in bidLevels" :key="'bid'+level.price" class="order-row">
                  <span class="order-label">买{{ bidLevels.indexOf(level)+1 }}</span>
                  <span class="order-price up">{{ level.price }}</span>
                  <span class="order-volume">{{ level.volume }}</span>
                  <div class="order-bar" :style="{ width: level.barWidth + '%', background: 'rgba(38,166,154,0.3)' }"></div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 交易统计 -->
          <el-card class="futu-card" style="margin-top:16px;">
            <div slot="header"><span>📊 交易统计</span></div>
            <div class="trade-stats">
              <div v-for="item in tradeStats" :key="item.label" class="stat-row">
                <span class="stat-label">{{ item.label }}</span>
                <span class="stat-value" :class="item.colorClass">{{ item.value }}</span>
              </div>
            </div>
          </el-card>

          <!-- 资金流向 -->
          <el-card class="futu-card" style="margin-top:16px;">
            <div slot="header"><span>💰 资金流向</span></div>
            <div class="capital-flow">
              <div class="flow-item">
                <span class="flow-label">主力净流入</span>
                <span class="flow-value" :class="capitalFlow.main_net_inflow >= 0 ? 'up' : 'down'">{{ formatMoney(capitalFlow.main_net_inflow) }}</span>
              </div>
              <div class="flow-item">
                <span class="flow-label">超大单</span>
                <span class="flow-value" :class="capitalFlow.super_large_net_inflow >= 0 ? 'up' : 'down'">{{ formatMoney(capitalFlow.super_large_net_inflow) }}</span>
              </div>
              <div class="flow-item">
                <span class="flow-label">大单</span>
                <span class="flow-value" :class="capitalFlow.large_net_inflow >= 0 ? 'up' : 'down'">{{ formatMoney(capitalFlow.large_net_inflow) }}</span>
              </div>
              <div class="flow-item">
                <span class="flow-label">中单</span>
                <span class="flow-value" :class="capitalFlow.medium_net_inflow >= 0 ? 'up' : 'down'">{{ formatMoney(capitalFlow.medium_net_inflow) }}</span>
              </div>
              <div class="flow-item">
                <span class="flow-label">小单(散户)</span>
                <span class="flow-value" :class="capitalFlow.small_net_inflow >= 0 ? 'up' : 'down'">{{ formatMoney(capitalFlow.small_net_inflow) }}</span>
              </div>
              <div class="flow-item" v-if="stockInfo.market === 'A股'">
                <span class="flow-label">北向资金</span>
                <span class="flow-value" :class="capitalFlow.northbound_net_inflow >= 0 ? 'up' : 'down'">{{ formatMoney(capitalFlow.northbound_net_inflow) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- K线 Tab -->
    <div v-show="activeTab === 'kline'" class="tab-content">
      <trading-chart ref="tradingChart" :code="selectedCode" :days="klineDays" />
    </div>

    <!-- 财务 Tab -->
    <div v-show="activeTab === 'financials'" class="tab-content">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-card class="futu-card">
            <div slot="header"><span>📈 PE/PB 趋势</span></div>
            <line-chart :categories="financialCategories" :series="financialSeries" title="估值趋势" :height="300" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="futu-card">
            <div slot="header"><span>💰 营收/净利润</span></div>
            <bar-chart :data="revenueData" :categories="financialCategories" title="营收趋势" :height="300" />
          </el-card>
        </el-col>
      </el-row>

      <el-card class="futu-card" style="margin-top:16px;">
        <div slot="header"><span>📋 财务摘要</span></div>
        <el-table :data="financialSummary" size="small" stripe>
          <el-table-column prop="item" label="指标" width="120" />
          <el-table-column prop="ttm" label="TTM" width="100" />
          <el-table-column prop="q1" label="Q1" width="80" />
          <el-table-column prop="q2" label="Q2" width="80" />
          <el-table-column prop="q3" label="Q3" width="80" />
          <el-table-column prop="q4" label="Q4" width="80" />
        </el-table>
      </el-card>
    </div>

    <!-- 评分 Tab -->
    <div v-show="activeTab === 'scoring'" class="tab-content">
      <el-card class="futu-card">
        <div slot="header"><span>🎯 综合评分</span></div>
        <scoring-panel :code="selectedCode" />
      </el-card>
    </div>

    <!-- 分析 Tab -->
    <div v-show="activeTab === 'analysis'" class="tab-content">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-card class="futu-card">
            <div slot="header"><span>🎯 技术面评估</span></div>
            <radar-chart :indicators="analysisRadarIndicators" :data="analysisRadarData" title="技术评分" :height="300" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="futu-card">
            <div slot="header"><span>📊 支撑/压力位</span></div>
            <el-table :data="supportResistance" size="small">
              <el-table-column prop="type" label="类型" width="80">
                <template slot-scope="{ row }">
                  <el-tag size="mini" :type="row.type === '压力' ? 'danger' : 'success'">{{ row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="price" label="价格" />
              <el-table-column prop="distance" label="距离" />
              <el-table-column prop="strength" label="强度" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- AI 解读 Tab -->
    <div v-show="activeTab === 'ai'" class="tab-content">
      <el-row :gutter="16">
        <!-- 左侧: 股票数据面板 -->
        <el-col :span="10">
          <el-card class="futu-card">
            <div slot="header">
              <span>📊 实时数据</span>
              <el-button size="mini" style="float:right;" @click="loadStockDataForAI" :loading="loadingData">🔄 刷新</el-button>
            </div>
            <div class="stock-data-panel">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="股票代码">{{ stockInfo.code }}</el-descriptions-item>
                <el-descriptions-item label="股票名称">{{ stockInfo.name }}</el-descriptions-item>
                <el-descriptions-item label="最新价">{{ stockInfo.price }}</el-descriptions-item>
                <el-descriptions-item label="涨跌幅">
                  <span :class="priceChange >= 0 ? 'up' : 'down'">{{ priceChangePercent }}%</span>
                </el-descriptions-item>
                <el-descriptions-item label="成交量">{{ stockInfo.volume || '-' }}</el-descriptions-item>
                <el-descriptions-item label="成交额">{{ stockInfo.turnover || '-' }}</el-descriptions-item>
                <el-descriptions-item label="5日 均线">{{ stockData.ma5 || '-' }}</el-descriptions-item>
                <el-descriptions-item label="20日 均线">{{ stockData.ma20 || '-' }}</el-descriptions-item>
                <el-descriptions-item label="60日 均线">{{ stockData.ma60 || '-' }}</el-descriptions-item>
                <el-descriptions-item label="评分">{{ stockData.score || '-' }}/100</el-descriptions-item>
              </el-descriptions>

              <div style="margin-top:16px;">
                <div style="font-size:13px;font-weight:bold;margin-bottom:8px;">📈 近10日走势</div>
                <div class="mini-chart">
                  <div v-for="(p, i) in recentPrices" :key="i" class="chart-bar"
                    :class="p.up ? 'up-bar' : 'down-bar'"
                    :style="{ height: p.height + '%' }">
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧: AI 对话 -->
        <el-col :span="14">
          <el-card class="futu-card">
            <div slot="header">
              <span>🤖 AI 解读</span>
              <el-button size="mini" type="primary" style="float:right;" @click="autoAnalyze" :loading="aiLoading">
                🔍 自动分析
              </el-button>
            </div>
            <div class="ai-chat-area">
              <!-- 快捷问题 -->
              <div class="quick-questions">
                <el-button size="mini" round @click="askQuick('这只股票近期走势如何？')">📈 走势分析</el-button>
                <el-button size="mini" round @click="askQuick('这只股票估值是否合理？')">💰 估值分析</el-button>
                <el-button size="mini" round @click="askQuick('这只股票有哪些风险？')">⚠️ 风险提示</el-button>
                <el-button size="mini" round @click="askQuick('给出买卖建议')">🎯 买卖建议</el-button>
              </div>

              <div class="chat-messages" ref="aiChatRef">
                <div v-for="(msg, idx) in aiMessages" :key="idx" class="chat-msg" :class="msg.role">
                  <div class="msg-bubble">
                    <span class="msg-role">{{ msg.role === 'user' ? '🧑' : '🤖' }}</span>
                    <div class="msg-content" v-html="sanitizeHTML(formatMsg(msg.content))" />
                  </div>
                </div>
                <div v-if="aiLoading" class="chat-msg ai">
                  <div class="msg-bubble">
                    <span class="msg-role">🤖</span>
                    <div class="msg-content">分析中...</div>
                  </div>
                </div>
                <el-empty v-if="!aiMessages.length && !aiLoading" description="点击上方快捷问题或输入自定义问题" :image-size="60" />
              </div>

              <div class="chat-input">
                <el-input v-model="aiInput" placeholder="输入关于这只股票的问题..."
                  @keyup.enter.native="sendAiMessage" :disabled="aiLoading" size="small" />
                <el-button type="primary" size="small" @click="sendAiMessage" :loading="aiLoading" style="margin-top:6px;">发送</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 新闻 Tab -->
    <div v-show="activeTab === 'news'" class="tab-content">
      <el-card class="futu-card">
        <div slot="header"><span>📰 相关新闻</span></div>
        <div v-for="news in relatedNews" :key="news.title" class="news-item">
          <div class="news-header">
            <h4 class="news-title">{{ news.title }}</h4>
            <el-tag size="mini" :type="news.sentiment > 0 ? 'success' : news.sentiment < 0 ? 'danger' : 'info'">
              {{ news.sentiment > 0 ? '利好' : news.sentiment < 0 ? '利空' : '中性' }}
            </el-tag>
          </div>
          <p class="news-summary">{{ news.summary }}</p>
          <div class="news-footer">
            <span class="news-source">{{ news.source }}</span>
            <span class="news-date">{{ news.date }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'
import TradingChart from '@/components/trading-chart/index.vue'
import { LineChart, BarChart, RadarChart } from '@/components/charts'
import ScoringPanel from '@/components/scoring-panel/index.vue'
import sanitizeMixin from '@/mixins/sanitize'

export default {
  mixins: [sanitizeMixin],
  name: 'StockDetail',
  components: { TradingChart, LineChart, BarChart, RadarChart, ScoringPanel },
  data() {
    return {
      selectedCode: '',
      activeTab: 'overview',
      stocks: [],
      stockInfo: {},
      intradayChart: null,
      intradayPeriod: 'today',
      klineDays: 90,
      isWatched: false,
      priceChange: 0,
      priceChangePercent: 0,
      prevPrice: 0,
      futuData: null,
      financialData: null,
      capitalFlow: {},

      // 盘口数据
      askLevels: [],
      bidLevels: [],

      // 核心指标
      coreMetrics: [],
      
      // 技术指标
      indicatorSummary: [],

      // 交易统计
      tradeStats: [],

      // 财务数据
      financialCategories: ['Q1', 'Q2', 'Q3', 'Q4', 'TTM'],
      financialSeries: [],
      revenueData: [],

      // 财务摘要
      financialSummary: [],

      // 分析雷达
      analysisRadarIndicators: [
        { name: '趋势', max: 100 },
        { name: '动量', max: 100 },
        { name: '波动', max: 100 },
        { name: '成交量', max: 100 },
        { name: '支撑', max: 100 },
        { name: '估值', max: 100 }
      ],
      analysisRadarData: [72, 65, 58, 80, 68, 75],

      // 支撑压力位
      supportResistance: [],

      // 相关新闻
      relatedNews: [],

      // AI 解读
      stockData: { ma5: null, ma20: null, ma60: null, score: null },
      recentPrices: [],
      aiMessages: [],
      aiInput: '',
      aiLoading: false,
      loadingData: false
    }
  },
  created() {
    this.fetchStocks()
    const code = this.$route.params.id || this.$route.query.code
    if (code) {
      this.selectedCode = code
      this.loadStock()
    }
  },
  mounted() {
    this.intradayChart = echarts.init(document.getElementById('intraday-chart'))
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.intradayChart) this.intradayChart.dispose()
  },
  methods: {
    handleResize() { this.intradayChart?.resize() },
    onTabChange() {},

    async fetchStocks() {
      try {
        const { data } = await request.get('/api/stocks')
        if (data.code === 200) this.stocks = data.data.list || []
      } catch (e) {}
    },

    async loadStock() {
      if (!this.selectedCode) return
      try {
        // 并行加载Futu风格数据
        const [quoteRes, intradayRes, financialsRes] = await Promise.all([
          request.get(`/api/futu/quote/${this.selectedCode}`),
          request.get(`/api/futu/intraday/${this.selectedCode}`, { params: { period: this.intradayPeriod } }),
          request.get(`/api/futu/financials/${this.selectedCode}`)
        ])
        
        if (quoteRes.data.code === 200) {
          const quote = quoteRes.data.data
          this.futuData = quote
          this.stockInfo = {
            code: quote.basic.code,
            name: quote.basic.name,
            market: quote.basic.market,
            sector: quote.basic.sector,
            industry: quote.basic.industry,
            exchange: quote.basic.exchange,
            listDate: quote.basic.list_date,
            price: quote.quote.current_price.toFixed(2)
          }
          this.priceChange = quote.quote.change
          this.priceChangePercent = quote.quote.change_pct
          this.prevPrice = quote.quote.prev_close
          
          // 盘口数据
          this.askLevels = quote.order_book.asks.map(a => ({...a, barWidth: a.volume / 5}))
          this.bidLevels = quote.order_book.bids.map(b => ({...b, barWidth: b.volume / 5}))
          
          // 核心指标
          this.coreMetrics = [
            { label: '今开', value: quote.quote.open.toFixed(2), colorClass: '' },
            { label: '最高', value: quote.quote.high.toFixed(2), colorClass: 'up' },
            { label: '最低', value: quote.quote.low.toFixed(2), colorClass: 'down' },
            { label: '昨收', value: quote.quote.prev_close.toFixed(2), colorClass: '' },
            { label: '成交量', value: (quote.quote.volume / 10000).toFixed(0) + '万', colorClass: '' },
            { label: '成交额', value: (quote.quote.turnover / 100000000).toFixed(2) + '亿', colorClass: '' },
            { label: '换手率', value: quote.quote.turnover_rate.toFixed(2) + '%', colorClass: '' },
            { label: '量比', value: quote.quote.volume_ratio.toFixed(2), colorClass: '' },
            { label: '市盈率(TTM)', value: quote.valuation.pe_ttm.toFixed(2), colorClass: '' },
            { label: '市净率', value: quote.valuation.pb.toFixed(2), colorClass: '' },
            { label: '总市值', value: (quote.market_cap.total_market_cap / 100000000).toFixed(2) + '亿', colorClass: '' },
            { label: '流通市值', value: (quote.market_cap.float_market_cap / 100000000).toFixed(2) + '亿', colorClass: '' }
          ]
          
          // 交易统计
          this.tradeStats = [
            { label: '52周最高', value: quote.price_range.week52_high.toFixed(2), colorClass: 'up' },
            { label: '52周最低', value: quote.price_range.week52_low.toFixed(2), colorClass: 'down' },
            { label: '涨停价', value: quote.price_range.day_limit_up?.toFixed(2) || '-', colorClass: 'up' },
            { label: '跌停价', value: quote.price_range.day_limit_down?.toFixed(2) || '-', colorClass: 'down' }
          ]
          
          // 支撑压力位
          this.supportResistance = quote.support_resistance
          
          // 技术指标
          const tech = quote.technical
          this.indicatorSummary = [
            { name: 'RSI(14)', value: tech.rsi14.toFixed(2), signal: tech.rsi14 < 30 ? '超卖' : tech.rsi14 > 70 ? '超买' : '中性', signalType: tech.rsi14 < 30 ? 'success' : tech.rsi14 > 70 ? 'danger' : 'info', desc: '相对强弱指标' },
            { name: 'MACD', value: tech.macd_dif.toFixed(4), signal: tech.macd_hist > 0 ? '金叉' : '死叉', signalType: tech.macd_hist > 0 ? 'success' : 'danger', desc: '异同移动平均线' },
            { name: 'MA5', value: tech.ma5.toFixed(2), signal: quote.quote.current_price > tech.ma5 ? '多头' : '空头', signalType: quote.quote.current_price > tech.ma5 ? 'success' : 'danger', desc: '5日均线' },
            { name: 'MA20', value: tech.ma20.toFixed(2), signal: quote.quote.current_price > tech.ma20 ? '多头' : '空头', signalType: quote.quote.current_price > tech.ma20 ? 'success' : 'danger', desc: '20日均线' },
            { name: 'BOLL上轨', value: tech.boll_upper.toFixed(2), signal: '压力', signalType: 'warning', desc: '布林带上轨' },
            { name: 'BOLL下轨', value: tech.boll_lower.toFixed(2), signal: '支撑', signalType: 'success', desc: '布林带下轨' }
          ]
          
          // 资金流向
          this.capitalFlow = quote.capital_flow
          
          // 财务数据
          if (financialsRes.data.code === 200) {
            this.financialData = financialsRes.data.data
            this.financialCategories = ['Q1', 'Q2', 'Q3', 'Q4', 'TTM']
            this.financialSeries = [
              { name: 'PE', data: [this.futuData?.valuation.pe_static, this.futuData?.valuation.pe_dynamic, this.futuData?.valuation.pe_ttm, this.futuData?.valuation.pe_ttm, this.futuData?.valuation.pe_ttm], color: '#409EFF' },
              { name: 'PB', data: [this.futuData?.valuation.pb * 0.9, this.futuData?.valuation.pb * 0.95, this.futuData?.valuation.pb, this.futuData?.valuation.pb * 1.05, this.futuData?.valuation.pb], color: '#67C23A' }
            ]
            this.revenueData = [financialsRes.data.data.income_statement.revenue.q1, financialsRes.data.data.income_statement.revenue.q2, financialsRes.data.data.income_statement.revenue.q3, financialsRes.data.data.income_statement.revenue.q4, financialsRes.data.data.income_statement.revenue.ttm]
          }
          
          // 加载分时图
          if (intradayRes.data.code === 200) {
            this.renderIntradayChart(intradayRes.data.data)
          }
          
          // 加载新闻
          this.loadRelatedNews()
        }
      } catch (e) { this.$message.error('加载股票详情失败: ' + e.message) }
    },

    generateOrderBook(currentPrice) {
      const askLevels = []
      const bidLevels = []
      for (let i = 0; i < 5; i++) {
        const askPrice = (currentPrice + (i + 1) * 0.01 * currentPrice * 0.01).toFixed(2)
        const bidPrice = (currentPrice - (i + 1) * 0.01 * currentPrice * 0.01).toFixed(2)
        const askVol = Math.floor(Math.random() * 500 + 50)
        const bidVol = Math.floor(Math.random() * 500 + 50)
        askLevels.push({ price: askPrice, volume: askVol, barWidth: askVol / 5 })
        bidLevels.push({ price: bidPrice, volume: bidVol, barWidth: bidVol / 5 })
      }
      this.askLevels = askLevels.reverse()
      this.bidLevels = bidLevels
    },

    generateCoreMetrics(d) {
      const prices = d.close || []
      const volumes = d.volume || []
      const currentPrice = prices[prices.length - 1] || 0
      this.coreMetrics = [
        { label: '今开', value: prices[0]?.toFixed(2) || '-', colorClass: '' },
        { label: '最高', value: Math.max(...prices).toFixed(2), colorClass: 'up' },
        { label: '最低', value: Math.min(...prices).toFixed(2), colorClass: 'down' },
        { label: '昨收', value: this.prevPrice.toFixed(2), colorClass: '' },
        { label: '成交量', value: (volumes[volumes.length - 1] / 10000).toFixed(1) + '万', colorClass: '' },
        { label: '成交额', value: (currentPrice * volumes[volumes.length - 1] / 100000000).toFixed(2) + '亿', colorClass: '' },
        { label: '换手率', value: (Math.random() * 5 + 1).toFixed(2) + '%', colorClass: '' },
        { label: '市盈率', value: (currentPrice / 25).toFixed(2), colorClass: '' },
        { label: '市净率', value: (currentPrice / 50).toFixed(2), colorClass: '' },
        { label: '总股本', value: (Math.random() * 50 + 10).toFixed(1) + '亿', colorClass: '' },
        { label: '流通市值', value: (currentPrice * 30 / 100).toFixed(2) + '亿', colorClass: '' },
        { label: '振幅', value: ((Math.max(...prices) - Math.min(...prices)) / this.prevPrice * 100).toFixed(2) + '%', colorClass: '' }
      ]
    },

    generateIndicatorSummary(d) {
      const last = d.close?.length - 1 || 0
      const indicators = d.indicators || {}
      this.indicatorSummary = [
        { name: 'RSI(14)', value: indicators.rsi?.[last]?.toFixed(2) || '-', signal: indicators.rsi?.[last] < 30 ? '超卖' : indicators.rsi?.[last] > 70 ? '超买' : '中性', signalType: indicators.rsi?.[last] < 30 ? 'success' : indicators.rsi?.[last] > 70 ? 'danger' : 'info', desc: '相对强弱指标' },
        { name: 'MACD', value: indicators.macd?.[last]?.toFixed(4) || '-', signal: indicators.macd_hist?.[last] > 0 ? '金叉' : '死叉', signalType: indicators.macd_hist?.[last] > 0 ? 'success' : 'danger', desc: '指数平滑异同移动平均线' },
        { name: 'MA5', value: indicators.ma5?.[last]?.toFixed(2) || '-', signal: d.close?.[last] > indicators.ma5?.[last] ? '多头' : '空头', signalType: d.close?.[last] > indicators.ma5?.[last] ? 'success' : 'danger', desc: '5日均线' },
        { name: 'MA20', value: indicators.ma20?.[last]?.toFixed(2) || '-', signal: d.close?.[last] > indicators.ma20?.[last] ? '多头' : '空头', signalType: d.close?.[last] > indicators.ma20?.[last] ? 'success' : 'danger', desc: '20日均线' },
        { name: 'BOLL上轨', value: indicators.bb_upper?.[last]?.toFixed(2) || '-', signal: '压力', signalType: 'warning', desc: '布林带上轨' },
        { name: 'BOLL下轨', value: indicators.bb_lower?.[last]?.toFixed(2) || '-', signal: '支撑', signalType: 'success', desc: '布林带下轨' }
      ]
    },

    generateTradeStats(d) {
      this.tradeStats = [
        { label: '52周最高', value: Math.max(...(d.close || [])).toFixed(2), colorClass: 'up' },
        { label: '52周最低', value: Math.min(...(d.close || [])).toFixed(2), colorClass: 'down' },
        { label: '日均成交量', value: Math.round((d.volume || []).reduce((a, b) => a + b, 0) / (d.volume?.length || 1)).toLocaleString(), colorClass: '' },
        { label: '涨停价', value: (this.prevPrice * 1.1).toFixed(2), colorClass: 'up' },
        { label: '跌停价', value: (this.prevPrice * 0.9).toFixed(2), colorClass: 'down' }
      ]
    },

    generateSupportResistance(d) {
      const prices = d.close || []
      const currentPrice = prices[prices.length - 1] || 0
      this.supportResistance = [
        { type: '压力', price: (currentPrice * 1.05).toFixed(2), distance: '+5%', strength: '强' },
        { type: '压力', price: (currentPrice * 1.03).toFixed(2), distance: '+3%', strength: '中' },
        { type: '支撑', price: (currentPrice * 0.97).toFixed(2), distance: '-3%', strength: '中' },
        { type: '支撑', price: (currentPrice * 0.95).toFixed(2), distance: '-5%', strength: '强' }
      ]
    },

    generateFinancialSummary(d) {
      this.financialSummary = [
        { item: '营收(亿)', ttm: '125.3', q1: '28.5', q2: '31.2', q3: '32.8', q4: '32.8' },
        { item: '净利润(亿)', ttm: '45.6', q1: '10.2', q2: '11.5', q3: '12.1', q4: '11.8' },
        { item: '毛利率', ttm: '52.3%', q1: '51.2%', q2: '52.8%', q3: '53.1%', q4: '52.1%' },
        { item: 'ROE', ttm: '18.5%', q1: '17.2%', q2: '18.8%', q3: '19.2%', q4: '18.8%' },
        { item: 'EPS', ttm: '5.62', q1: '1.25', q2: '1.42', q3: '1.52', q4: '1.43' }
      ]
    },

    loadRelatedNews() {
      this.relatedNews = [
        { title: `${this.stockInfo.name}发布最新财报，业绩超预期`, summary: '公司最新季度财报显示，营收和净利润均超过市场一致预期，毛利率同比提升2.3个百分点，ROE达到18.5%...', source: '财联社', date: '2026-04-17 14:30', sentiment: 0.8 },
        { title: `机构上调${this.stockInfo.name}目标价至XXX元`, summary: '多家机构发布研报，一致看好公司未来发展前景，维持买入评级...', source: '证券时报', date: '2026-04-16 10:15', sentiment: 0.6 },
        { title: `${this.stockInfo.name}获北向资金连续3日净买入`, summary: '沪深港通数据显示，北向资金连续3个交易日净买入该股，累计净买入超5000万元...', source: '东方财富', date: '2026-04-15 18:00', sentiment: 0.5 },
        { title: `行业政策利好，${this.stockInfo.name}受益明显`, summary: '最新行业政策发布，公司作为行业龙头将直接受益，预计未来2年业绩增速维持在15%以上...', source: '36氪', date: '2026-04-14 09:30', sentiment: 0.7 }
      ]
    },

    renderIntradayChart(d) {
      const data = d.data || []
      if (!data.length) return
      
      const times = data.map(p => p.time)
      const prices = data.map(p => p.price)
      const avgPrices = data.map(p => p.avg_price)
      const volumes = data.map(p => p.volume)
      
      this.intradayChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
        legend: { data: ['价格', '均价'], top: 5, textStyle: { color: '#d1d4dc' } },
        grid: [{ left: '3%', right: '3%', top: '15%', height: '55%' }, { left: '3%', right: '3%', top: '75%', height: '20%' }],
        xAxis: [
          { type: 'category', data: times, gridIndex: 0, axisLabel: { color: '#d1d4dc', rotate: 30, fontSize: 10 } },
          { type: 'category', data: times, gridIndex: 1, axisLabel: { color: '#d1d4dc', rotate: 30, fontSize: 10 } }
        ],
        yAxis: [
          { type: 'value', scale: true, gridIndex: 0, axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
          { type: 'value', gridIndex: 1, axisLabel: { show: false }, splitLine: { show: false } }
        ],
        series: [
          { name: '价格', type: 'line', data: prices, smooth: false, xAxisIndex: 0, yAxisIndex: 0, lineStyle: { width: 1.5 }, itemStyle: { color: '#409EFF' }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(64,158,255,0.3)' }, { offset: 1, color: 'rgba(64,158,255,0.05)' }]) } },
          { name: '均价', type: 'line', data: avgPrices, smooth: false, xAxisIndex: 0, yAxisIndex: 0, lineStyle: { width: 1, type: 'dashed' }, itemStyle: { color: '#E6A23C' } },
          { name: '成交量', type: 'bar', data: volumes, xAxisIndex: 1, yAxisIndex: 1, itemStyle: { color: '#26a69a' } }
        ]
      }, true)
    },

    toggleWatchlist() {
      this.isWatched = !this.isWatched
      this.$message.success(this.isWatched ? '已添加到自选' : '已从自选移除')
    },

    goToTrade() {
      this.$router.push('/trade-simulator')
    },

    loadIntraday() {
      this.loadStock()
    },
    formatMoney(val) {
      if (val === null || val === undefined) return '-'
      const num = Number(val)
      if (Math.abs(num) >= 100000000) return (num / 100000000).toFixed(2) + '亿'
      if (Math.abs(num) >= 10000) return (num / 10000).toFixed(2) + '万'
      return num.toFixed(0)
    },

    // ========== AI 解读 ==========
    async loadStockDataForAI() {
      this.loadingData = true
      try {
        // 获取历史K线数据
        const { data } = await request.get(`/api/stock-kline/${this.selectedCode}`, {
          params: { days: 30 }
        })
        if (data.code === 200 && data.data.kline) {
          const kline = data.data.kline
          const closes = kline.map(k => k.close).filter(v => v)
          const volumes = kline.map(k => k.volume).filter(v => v)
          
          // 计算均线
          if (closes.length >= 5) {
            const ma5 = closes.slice(-5).reduce((a, b) => a + b, 0) / 5
            this.stockData.ma5 = ma5.toFixed(2)
          }
          if (closes.length >= 20) {
            const ma20 = closes.slice(-20).reduce((a, b) => a + b, 0) / 20
            this.stockData.ma20 = ma20.toFixed(2)
          }
          if (closes.length >= 60) {
            const ma60 = closes.slice(-60).reduce((a, b) => a + b, 0) / 60
            this.stockData.ma60 = ma60.toFixed(2)
          }

          // 近10日走势
          const recent = closes.slice(-10)
          if (recent.length > 0) {
            const min = Math.min(...recent)
            const max = Math.max(...recent)
            const range = max - min || 1
            this.recentPrices = recent.map((p, i) => {
              const prev = i > 0 ? recent[i - 1] : p
              return {
                price: p,
                up: p >= prev,
                height: ((p - min) / range) * 80 + 20
              }
            })
          }

          this.stockData.history = closes.slice(-30).map((c, i) => ({
            date: kline[kline.length - 30 + i]?.date || '',
            close: c.toFixed(2)
          }))
        }

        // 获取评分
        try {
          const { data: sd } = await request.get(`/api/stock-score/${this.selectedCode}`)
          if (sd.code === 200) {
            this.stockData.score = sd.data?.total_score || sd.data?.score || '-'
          }
        } catch (e) { /* ignore */ }

        this.stockInfo.code = this.selectedCode
        this.stockInfo.name = this.stockInfo.name || this.selectedCode
        this.$message.success('数据已刷新')
      } catch (e) {
        this.$message.error('获取数据失败')
      } finally {
        this.loadingData = false
      }
    },

    askQuick(question) {
      this.aiMessages.push({ role: 'user', content: question })
      this.sendAiQuery(question)
    },

    async sendAiMessage() {
      const q = this.aiInput.trim()
      if (!q || this.aiLoading) return
      this.aiMessages.push({ role: 'user', content: q })
      this.aiInput = ''
      this.sendAiQuery(q)
    },

    async autoAnalyze() {
      const q = `请全面分析 ${this.stockInfo.name || this.selectedCode} (${this.selectedCode})，包括：走势分析、估值评估、风险提示和买卖建议。`
      this.aiMessages.push({ role: 'user', content: q })
      this.sendAiQuery(q)
    },

    async sendAiQuery(question) {
      this.aiLoading = true
      // 确保有数据
      if (!this.stockData.history) {
        await this.loadStockDataForAI()
      }

      const context = this.buildStockContext()
      try {
        const { data } = await request.post('/api/ai/chat', {
          question: `关于股票 ${this.stockInfo.name || this.selectedCode} 的数据如下：\n${context}\n\n请回答：${question}`
        })
        if (data.code === 200) {
          this.aiMessages.push({ role: 'ai', content: data.data.content })
        } else {
          this.aiMessages.push({ role: 'ai', content: '❌ ' + data.message })
        }
      } catch (e) {
        this.aiMessages.push({ role: 'ai', content: '❌ 请求失败: ' + e.message })
      } finally {
        this.aiLoading = false
        this.$nextTick(() => {
          const el = this.$refs.aiChatRef
          if (el) el.scrollTop = el.scrollHeight
        })
      }
    },

    buildStockContext() {
      const lines = []
      lines.push(`股票: ${this.stockInfo.name || ''} (${this.stockInfo.code || this.selectedCode})`)
      lines.push(`最新价: ${this.stockInfo.price || '-'}`)
      lines.push(`涨跌幅: ${this.priceChangePercent}%`)
      if (this.stockData.ma5) lines.push(`5日均线: ${this.stockData.ma5}`)
      if (this.stockData.ma20) lines.push(`20日均线: ${this.stockData.ma20}`)
      if (this.stockData.ma60) lines.push(`60日均线: ${this.stockData.ma60}`)
      if (this.stockData.score) lines.push(`综合评分: ${this.stockData.score}/100`)
      if (this.stockData.history && this.stockData.history.length) {
        lines.push(`近30日收盘价: ${this.stockData.history.map(h => h.close).join(', ')}`)
      }
      return lines.join('\n')
    },

    formatMsg(text) {
      return text.replace(/\n/g, '<br/>')
    }
  }
}
</script>

<style scoped>
.stock-detail-futu {
  background: #0f0f1a;
  min-height: 100vh;
  padding: 16px;
}

/* 顶部行情栏 */
.quote-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #1a1a2e;
  border-radius: 8px;
  margin-bottom: 16px;
  border-left: 4px solid;
}

.quote-header.up { border-left-color: #26a69a; }
.quote-header.down { border-left-color: #ef5350; }

.header-left { display: flex; align-items: center; gap: 12px; }
.stock-name { margin: 0; font-size: 24px; color: #d1d4dc; }
.stock-code { color: #909399; font-size: 14px; }
.market-tag { background: #2a2a3e; border: none; color: #d1d4dc; }

.header-center { text-align: center; }
.current-price { font-size: 32px; font-weight: 700; color: #d1d4dc; }
.price-change { display: flex; gap: 8px; align-items: center; }
.change-value { font-size: 18px; font-weight: 600; }
.change-percent { font-size: 14px; color: #909399; }

.quote-header.up .current-price,
.quote-header.up .change-value { color: #26a69a; }
.quote-header.down .current-price,
.quote-header.down .change-value { color: #ef5350; }

.header-right { display: flex; gap: 8px; }

/* Tab栏 */
.tab-bar { margin-bottom: 16px; }
.tab-bar ::v-deep .el-tabs__header { margin: 0; background: #1a1a2e; border-radius: 8px; }
.tab-bar ::v-deep .el-tabs__item { color: #909399; }
.tab-bar ::v-deep .el-tabs__item.is-active { color: #409EFF; background: #2a2a3e; }

/* 卡片 */
.futu-card { background: #1a1a2e !important; border: 1px solid #2a2a3e !important; }
.futu-card ::v-deep .el-card__header { border-bottom: 1px solid #2a2a3e !important; color: #d1d4dc; }
.card-header { display: flex; justify-content: space-between; align-items: center; }

/* 指标网格 */
.metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.metric-item { background: #2a2a3e; padding: 12px; border-radius: 6px; text-align: center; }
.metric-label { color: #909399; font-size: 12px; margin-bottom: 4px; }
.metric-value { font-size: 16px; font-weight: 600; color: #d1d4dc; }
.metric-value.up { color: #26a69a; }
.metric-value.down { color: #ef5350; }

/* 盘口 */
.order-book { font-family: 'SFMono-Regular', Consolas, monospace; }
.order-row { display: flex; align-items: center; padding: 4px 0; position: relative; }
.order-label { width: 40px; color: #909399; font-size: 12px; }
.order-price { width: 70px; font-size: 13px; font-weight: 600; }
.order-price.up { color: #26a69a; }
.order-price.down { color: #ef5350; }
.order-volume { width: 60px; font-size: 12px; color: #d1d4dc; }
.order-bar { position: absolute; right: 0; top: 0; bottom: 0; z-index: -1; }

.current-price-row {
  display: flex; align-items: center; justify-content: center;
  padding: 8px 0; margin: 8px 0; border-top: 1px solid #2a2a3e; border-bottom: 1px solid #2a2a3e;
}
.price-label { color: #909399; margin-right: 12px; }
.price-value { font-size: 18px; font-weight: 700; }
.price-value.up { color: #26a69a; }
.price-value.down { color: #ef5350; }

/* 交易统计 */
.trade-stats .stat-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #2a2a3e; }
.stat-label { color: #909399; font-size: 13px; }
.stat-value { font-weight: 600; color: #d1d4dc; }
.stat-value.up { color: #26a69a; }
.stat-value.down { color: #ef5350; }

/* 资金流向 */
.capital-flow .flow-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #2a2a3e; }
.flow-label { color: #909399; font-size: 13px; }
.flow-value { font-weight: 600; }
.flow-value.up { color: #26a69a; }
.flow-value.down { color: #ef5350; }

/* 新闻列表 */
.news-item { padding: 12px 0; border-bottom: 1px solid #2a2a3e; }
.news-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.news-title { margin: 0; font-size: 14px; color: #d1d4dc; }
.news-summary { color: #909399; font-size: 12px; margin: 4px 0; line-height: 1.4; }
.news-footer { display: flex; justify-content: space-between; color: #606266; font-size: 11px; }

/* AI 解读 */
.stock-data-panel { font-size: 13px; }
.mini-chart { display: flex; align-items: flex-end; height: 60px; gap: 3px; padding: 4px 0; }
.chart-bar { flex: 1; border-radius: 2px 2px 0 0; min-height: 4px; transition: height 0.3s; }
.up-bar { background: #26a69a; }
.down-bar { background: #ef5350; }

.ai-chat-area { display: flex; flex-direction: column; height: 500px; }
.quick-questions { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.chat-messages { flex: 1; overflow-y: auto; padding: 8px 0; }
.chat-msg { margin-bottom: 10px; display: flex; }
.chat-msg.user { justify-content: flex-end; }
.chat-msg.ai { justify-content: flex-start; }
.msg-bubble { max-width: 85%; padding: 8px 12px; border-radius: 10px; background: #2a2a3e; font-size: 13px; }
.chat-msg.user .msg-bubble { background: #1a3a5c; }
.msg-role { margin-right: 6px; font-size: 12px; }
.msg-content { line-height: 1.6; white-space: pre-wrap; color: #d1d4dc; }
.chat-input { border-top: 1px solid #2a2a3e; padding-top: 10px; }
</style>
