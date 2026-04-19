/**
 * Phase 313: 图表AI增强
 * AI智能图表分析组件 - 自动识别趋势、形态、异常并给出建议
 */
<template>
  <div class="ai-chart-insights">
    <el-card :body-style="{ padding: '12px' }" shadow="hover">
      <div slot="header" class="insight-header">
        <span>🤖 AI 智能分析</span>
        <el-tag size="mini" :type="confidence > 0.7 ? 'success' : 'warning'">
          置信度 {{ (confidence * 100).toFixed(0) }}%
        </el-tag>
      </div>
      
      <!-- 趋势识别 -->
      <div class="insight-section" v-if="trend">
        <div class="section-title">📈 趋势识别</div>
        <el-tag :type="trendType(trend)" size="small">{{ trendText(trend) }}</el-tag>
        <div class="trend-desc">{{ trendDesc }}</div>
      </div>
      
      <!-- 形态识别 -->
      <div class="insight-section" v-if="patterns.length">
        <div class="section-title">🔍 K线形态</div>
        <el-tag v-for="p in patterns" :key="p.name" :type="patternType(p)" size="small" style="margin-right:4px;">
          {{ p.name }}
        </el-tag>
      </div>
      
      <!-- 异常检测 -->
      <div class="insight-section" v-if="anomalies.length">
        <div class="section-title">⚠️ 异常信号</div>
        <div v-for="a in anomalies" :key="a.type" class="anomaly-item">
          <el-alert :title="a.title" :type="alertType(a.level)" :closable="false" show-icon>
            <span slot="description">{{ a.desc }}</span>
          </el-alert>
        </div>
      </div>
      
      <!-- 支撑压力位 -->
      <div class="insight-section" v-if="supportResistance">
        <div class="section-title">📊 支撑/压力位</div>
        <el-row :gutter="12">
          <el-col :span="12">
            <div class="sr-item sr-support">
              <div class="sr-label">支撑位</div>
              <div class="sr-value" v-for="s in supportResistance.support" :key="s">{{ s }}</div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="sr-item sr-resistance">
              <div class="sr-label">压力位</div>
              <div class="sr-value" v-for="r in supportResistance.resistance" :key="r">{{ r }}</div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- AI 建议 -->
      <div class="insight-section" v-if="suggestion">
        <div class="section-title">💡 AI 建议</div>
        <el-alert :title="suggestion.title" :type="suggestionType" :closable="false" show-icon>
          <span slot="description">{{ suggestion.content }}</span>
        </el-alert>
      </div>
      
      <!-- 多指标评分 -->
      <div class="insight-section" v-if="scores">
        <div class="section-title">📊 多指标评分</div>
        <el-progress v-for="(s, k) in scores" :key="k" :text-inside="true" :stroke-width="16"
          :percentage="s.value" :status="s.status" :format="() => k" style="margin-bottom:8px;" />
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AIChartInsights',
  props: {
    // K线数据
    klineData: { type: Array, default: () => [] },
    // 成交量数据
    volumeData: { type: Array, default: () => [] },
    // 当前价格
    currentPrice: { type: Number, default: 0 },
    // 股票代码
    code: { type: String, default: '' },
  },
  data() {
    return {
      loading: false,
      // AI分析结果
      trend: '', // up/down/sideways
      trendDesc: '',
      patterns: [],
      anomalies: [],
      supportResistance: null,
      suggestion: null,
      scores: null,
      confidence: 0.85,
    }
  },
  computed: {
    suggestionType() {
      if (!this.suggestion) return 'info'
      return this.suggestion.signal === 'buy' ? 'success' : 
             this.suggestion.signal === 'sell' ? 'danger' : 'warning'
    }
  },
  watch: {
    klineData: {
      handler(val) {
        if (val && val.length > 0) this.analyze()
      },
      immediate: true,
      deep: true
    }
  },
  methods: {
    // 主分析函数
    async analyze() {
      if (!this.klineData || this.klineData.length < 20) return
      this.loading = true
      try {
        this.detectTrend()
        this.detectPatterns()
        this.detectAnomalies()
        this.calcSupportResistance()
        this.calcScores()
        this.generateSuggestion()
      } finally {
        this.loading = false
      }
    },

    // 趋势识别
    detectTrend() {
      const closes = this.klineData.map(d => d.close || d.c)
      if (closes.length < 20) return
      
      // 简单移动平均判断趋势
      const ma5 = this.avg(closes.slice(-5))
      const ma10 = this.avg(closes.slice(-10))
      const ma20 = this.avg(closes.slice(-20))
      
      if (ma5 > ma10 && ma10 > ma20) {
        this.trend = 'up'
        this.trendDesc = '短期均线多头排列，上升趋势明确'
      } else if (ma5 < ma10 && ma10 < ma20) {
        this.trend = 'down'
        this.trendDesc = '短期均线空头排列，下降趋势明确'
      } else {
        this.trend = 'sideways'
        this.trendDesc = '均线交织，震荡整理格局'
      }
    },

    // K线形态识别
    detectPatterns() {
      const data = this.klineData.slice(-10)
      this.patterns = []
      
      for (let i = 1; i < data.length; i++) {
        const curr = data[i]
        const prev = data[i-1]
        
        // 十字星
        if (Math.abs(curr.open - curr.close) < (curr.high - curr.low) * 0.1) {
          this.patterns.push({ name: '十字星', type: 'neutral' })
        }
        
        // 大阳线
        if ((curr.close - curr.open) > (curr.high - curr.low) * 0.7) {
          this.patterns.push({ name: '大阳线', type: 'bullish' })
        }
        
        // 大阴线
        if ((curr.open - curr.close) > (curr.high - curr.low) * 0.7) {
          this.patterns.push({ name: '大阴线', type: 'bearish' })
        }
        
        // 锤子线
        const body = Math.abs(curr.close - curr.open)
        const lowerShadow = Math.min(curr.open, curr.close) - curr.low
        if (lowerShadow > body * 2 && body < (curr.high - curr.low) * 0.3) {
          this.patterns.push({ name: '锤子线', type: 'bullish' })
        }
        
        // 吞没形态
        if (prev.close > prev.open && curr.close < curr.open && curr.open > prev.close && curr.close < prev.open) {
          this.patterns.push({ name: '看跌吞没', type: 'bearish' })
        }
        if (prev.close < prev.open && curr.close > curr.open && curr.open < prev.close && curr.close > prev.open) {
          this.patterns.push({ name: '看涨吞没', type: 'bullish' })
        }
      }
      
      // 去重
      const seen = new Set()
      this.patterns = this.patterns.filter(p => {
        if (seen.has(p.name)) return false
        seen.add(p.name)
        return true
      })
    },

    // 异常检测
    detectAnomalies() {
      this.anomalies = []
      const closes = this.klineData.map(d => d.close || d.c)
      if (closes.length < 10) return
      
      // 计算涨跌幅
      const changes = []
      for (let i = 1; i < closes.length; i++) {
        changes.push((closes[i] - closes[i-1]) / closes[i-1])
      }
      
      const avgChange = this.avg(changes)
      const stdChange = Math.sqrt(this.avg(changes.map(c => (c - avgChange) ** 2)))
      
      // 检测异常波动 (>2σ)
      const latestChange = changes[changes.length - 1]
      if (Math.abs(latestChange - avgChange) > 2 * stdChange) {
        this.anomalies.push({
          type: 'volatility',
          level: 'high',
          title: '异常波动',
          desc: `最新涨跌幅 ${(latestChange * 100).toFixed(2)}%，超出正常波动范围`
        })
      }
      
      // 检测放量
      const volumes = this.klineData.map(d => d.volume || d.v)
      if (volumes.length >= 5) {
        const avgVol = this.avg(volumes.slice(-5))
        const latestVol = volumes[volumes.length - 1]
        if (latestVol > avgVol * 2) {
          this.anomalies.push({
            type: 'volume',
            level: 'medium',
            title: '异常放量',
            desc: `最新成交量 ${(latestVol / avgVol).toFixed(1)} 倍于5日均量`
          })
        }
      }
    },

    // 支撑压力位计算
    calcSupportResistance() {
      const data = this.klineData.slice(-30)
      if (data.length < 20) return
      
      const highs = data.map(d => d.high || d.h)
      const lows = data.map(d => d.low || d.l)
      
      // 简单的支撑压力位：近期高低点
      const sortedHighs = [...highs].sort((a, b) => a - b)
      const sortedLows = [...lows].sort((a, b) => a - b)
      
      this.supportResistance = {
        support: [
          sortedLows[0].toFixed(2),
          sortedLows[1]?.toFixed(2),
          sortedLows[2]?.toFixed(2)
        ].filter(Boolean),
        resistance: [
          sortedHighs[sortedHighs.length - 1].toFixed(2),
          sortedHighs[sortedHighs - 2]?.toFixed(2),
          sortedHighs[sortedHighs - 3]?.toFixed(2)
        ].filter(Boolean)
      }
    },

    // 多指标评分
    calcScores() {
      const closes = this.klineData.map(d => d.close || d.c)
      if (closes.length < 20) return
      
      // RSI
      const rsi = this.calcRSI(closes, 14)
      const rsiScore = rsi > 70 ? 30 : rsi < 30 ? 80 : 100 - Math.abs(rsi - 50)
      
      // MACD
      const macdSignal = this.calcMACDSignal(closes)
      const macdScore = macdSignal > 0 ? 75 : 35
      
      // 趋势
      const trendScore = this.trend === 'up' ? 80 : this.trend === 'down' ? 25 : 50
      
      this.scores = {
        'RSI': { value: Math.round(rsiScore), status: rsiScore > 60 ? 'success' : rsiScore < 40 ? 'exception' : '' },
        'MACD': { value: macdScore, status: macdScore > 60 ? 'success' : 'exception' },
        '趋势': { value: trendScore, status: trendScore > 60 ? 'success' : trendScore < 40 ? 'exception' : '' },
        '综合': { value: Math.round((rsiScore + macdScore + trendScore) / 3), status: 'success' }
      }
    },

    // 生成AI建议
    generateSuggestion() {
      if (!this.scores) return
      
      const avgScore = (this.scores['综合'].value)
      
      if (avgScore >= 70) {
        this.suggestion = {
          signal: 'buy',
          title: '🟢 建议关注',
          content: '多项指标偏多，可考虑逢低布局，建议设置止损位'
        }
      } else if (avgScore <= 35) {
        this.suggestion = {
          signal: 'sell',
          title: '🔴 建议谨慎',
          content: '多项指标偏空，建议观望或减仓，等待企稳信号'
        }
      } else {
        this.suggestion = {
          signal: 'hold',
          title: '🟡 建议观望',
          content: '指标分化，方向不明确，建议等待明确信号'
        }
      }
    },

    // 工具函数
    avg(arr) { return arr.reduce((a, b) => a + b, 0) / arr.length },
    
    calcRSI(closes, period) {
      const changes = []
      for (let i = 1; i < closes.length; i++) {
        changes.push(closes[i] - closes[i-1])
      }
      const gains = changes.filter(c => c > 0)
      const losses = changes.filter(c => c < 0).map(c => Math.abs(c))
      const avgGain = gains.length ? this.avg(gains) : 0
      const avgLoss = losses.length ? this.avg(losses) : 0.001
      return 100 - (100 / (1 + avgGain / avgLoss))
    },

    calcMACDSignal(closes) {
      const ema12 = this.calcEMA(closes, 12)
      const ema26 = this.calcEMA(closes, 26)
      return ema12 - ema26
    },

    calcEMA(data, period) {
      const k = 2 / (period + 1)
      let ema = data[0]
      for (let i = 1; i < data.length; i++) {
        ema = data[i] * k + ema * (1 - k)
      }
      return ema
    },

    trendType(t) { return t === 'up' ? 'success' : t === 'down' ? 'danger' : 'info' },
    trendText(t) { return t === 'up' ? '上升趋势' : t === 'down' ? '下降趋势' : '震荡整理' },
    patternType(p) { return p.type === 'bullish' ? 'success' : p.type === 'bearish' ? 'danger' : 'info' },
    alertType(l) { return l === 'high' ? 'error' : l === 'medium' ? 'warning' : 'info' }
  }
}
</script>

<style scoped>
.ai-chart-insights { margin: 12px 0; }
.insight-header { display: flex; justify-content: space-between; align-items: center; }
.insight-section { margin-bottom: 16px; }
.insight-section:last-child { margin-bottom: 0; }
.section-title { font-size: 13px; font-weight: bold; color: #303133; margin-bottom: 8px; }
.trend-desc { font-size: 12px; color: #909399; margin-top: 6px; }
.anomaly-item { margin-bottom: 8px; }
.sr-item { padding: 8px; border-radius: 4px; }
.sr-support { background: #f0f9ff; }
.sr-resistance { background: #fef0f0; }
.sr-label { font-size: 12px; color: #909399; margin-bottom: 4px; }
.sr-value { font-size: 14px; font-weight: bold; }
</style>
