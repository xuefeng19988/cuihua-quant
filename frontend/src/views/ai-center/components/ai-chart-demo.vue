/**
 * Phase 313: AI 图表展示页
 * 综合展示 AI 图表功能
 */
<template>
  <div class="ai-chart-demo">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 智能 K 线图 -->
      <el-tab-pane label="📈 智能K线" name="kline">
        <ai-smart-chart :klineData="klineData" chartType="kline" :enableAi="true" />
        <ai-chart-insights :klineData="klineData" :currentPrice="currentPrice" />
      </el-tab-pane>
      
      <!-- AI 看板 -->
      <el-tab-pane label="🤖 AI看板" name="dashboard">
        <ai-dashboard />
      </el-tab-pane>
      
      <!-- 多指标对比 -->
      <el-tab-pane label="📊 指标对比" name="comparison">
        <el-card>
          <div slot="header">技术指标对比</div>
          <el-row :gutter="16">
            <el-col :span="12">
              <div ref="indicatorChart1" style="width:100%;height:300px;"></div>
            </el-col>
            <el-col :span="12">
              <div ref="indicatorChart2" style="width:100%;height:300px;"></div>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>
      
      <!-- 形态识别 -->
      <el-tab-pane label="🔍 形态识别" name="patterns">
        <el-card>
          <div slot="header">AI K线形态识别</div>
          <el-table :data="detectedPatterns" stripe border>
            <el-table-column prop="name" label="形态名称" width="120" />
            <el-table-column prop="date" label="出现日期" width="120" />
            <el-table-column prop="type" label="类型" width="80">
              <template slot-scope="{row}">
                <el-tag size="mini" :type="patternType(row.type)">{{ typeText(row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reliability" label="可靠度" width="100">
              <template slot-scope="{row}">
                <el-progress :percentage="row.reliability" :stroke-width="10"
                  :color="row.reliability > 70 ? '#67c23a' : row.reliability > 40 ? '#e6a23c' : '#f56c6c'" />
              </template>
            </el-table-column>
            <el-table-column prop="desc" label="说明" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import AISmartChart from '@/components/ai-smart-chart.vue'
import AIChartInsights from '@/components/ai-chart-insights.vue'
import AIDashboard from '@/components/ai-dashboard.vue'
import * as echarts from 'echarts'

export default {
  name: 'AIChartDemo',
  components: { AISmartChart, AIChartInsights, AIDashboard },
  data() {
    return {
      activeTab: 'kline',
      klineData: [],
      currentPrice: 0,
      detectedPatterns: [],
    }
  },
  mounted() {
    this.generateMockData()
  },
  methods: {
    generateMockData() {
      // 生成模拟 K 线数据
      const data = []
      let price = 100
      const startDate = new Date('2025-01-01')
      
      for (let i = 0; i < 120; i++) {
        const date = new Date(startDate)
        date.setDate(date.getDate() + i)
        
        const change = (Math.random() - 0.48) * 4
        const open = price
        const close = price + change
        const high = Math.max(open, close) + Math.random() * 2
        const low = Math.min(open, close) - Math.random() * 2
        const volume = Math.floor(10000 + Math.random() * 50000)
        
        data.push({
          date: date.toISOString().split('T')[0],
          open: parseFloat(open.toFixed(2)),
          close: parseFloat(close.toFixed(2)),
          high: parseFloat(high.toFixed(2)),
          low: parseFloat(low.toFixed(2)),
          volume
        })
        
        price = close
      }
      
      this.klineData = data
      this.currentPrice = data[data.length - 1].close
      
      // 检测形态
      this.detectPatterns()
      
      // 渲染指标图
      this.$nextTick(() => this.renderIndicators())
    },
    
    detectPatterns() {
      this.detectedPatterns = []
      const data = this.klineData
      
      for (let i = 1; i < data.length; i++) {
        const curr = data[i]
        const prev = data[i - 1]
        const body = Math.abs(curr.close - curr.open)
        const range = curr.high - curr.low
        
        // 十字星
        if (body < range * 0.1) {
          this.detectedPatterns.push({
            name: '十字星', date: curr.date, type: 'neutral',
            reliability: 65, desc: '多空力量均衡，可能变盘'
          })
        }
        
        // 大阳线
        if ((curr.close - curr.open) > range * 0.7) {
          this.detectedPatterns.push({
            name: '大阳线', date: curr.date, type: 'bullish',
            reliability: 75, desc: '多方强势，看涨'
          })
        }
        
        // 大阴线
        if ((curr.open - curr.close) > range * 0.7) {
          this.detectedPatterns.push({
            name: '大阴线', date: curr.date, type: 'bearish',
            reliability: 75, desc: '空方强势，看跌'
          })
        }
        
        // 锤子线
        const lowerShadow = Math.min(curr.open, curr.close) - curr.low
        if (lowerShadow > body * 2 && body < range * 0.3) {
          this.detectedPatterns.push({
            name: '锤子线', date: curr.date, type: 'bullish',
            reliability: 70, desc: '底部反转信号'
          })
        }
        
        // 吞没
        if (prev.close > prev.open && curr.close < curr.open && curr.open > prev.close && curr.close < prev.open) {
          this.detectedPatterns.push({
            name: '看跌吞没', date: curr.date, type: 'bearish',
            reliability: 80, desc: '强烈看跌信号'
          })
        }
      }
      
      // 只保留最近的 10 个
      this.detectedPatterns = this.detectedPatterns.slice(-10)
    },
    
    renderIndicators() {
      const closes = this.klineData.map(d => d.close)
      const dates = this.klineData.map(d => d.date)
      
      // RSI 图
      const rsiChart = echarts.init(this.$refs.indicatorChart1)
      const rsiData = this.calcRSI(closes, 14)
      rsiChart.setOption({
        title: { text: 'RSI (14)', left: 'center' },
        tooltip: { trigger: 'axis' },
        grid: { left: '10%', right: '8%', top: '15%', bottom: '10%' },
        xAxis: { type: 'category', data: dates, axisLabel: { rotate: 30 } },
        yAxis: { type: 'value', min: 0, max: 100 },
        series: [
          { name: 'RSI', type: 'line', data: rsiData, smooth: true },
          { name: '超买线', type: 'line', data: Array(dates.length).fill(70), lineStyle: { type: 'dashed', color: '#f56c6c' } },
          { name: '超卖线', type: 'line', data: Array(dates.length).fill(30), lineStyle: { type: 'dashed', color: '#67c23a' } }
        ]
      })
      
      // MACD 图
      const macdChart = echarts.init(this.$refs.indicatorChart2)
      const macdData = this.calcMACD(closes)
      macdChart.setOption({
        title: { text: 'MACD (12,26,9)', left: 'center' },
        tooltip: { trigger: 'axis' },
        grid: { left: '10%', right: '8%', top: '15%', bottom: '10%' },
        xAxis: { type: 'category', data: dates, axisLabel: { rotate: 30 } },
        yAxis: { type: 'value' },
        series: [
          { name: 'DIF', type: 'line', data: macdData.dif, smooth: true },
          { name: 'DEA', type: 'line', data: macdData.dea, smooth: true },
          { name: 'MACD柱', type: 'bar', data: macdData.histogram,
            itemStyle: { color: p => p.value >= 0 ? '#ef232a' : '#14b143' } }
        ]
      })
    },
    
    calcRSI(closes, period) {
      const result = []
      let avgGain = 0, avgLoss = 0
      
      for (let i = 1; i < closes.length; i++) {
        const change = closes[i] - closes[i - 1]
        const gain = change > 0 ? change : 0
        const loss = change < 0 ? Math.abs(change) : 0
        
        if (i <= period) {
          avgGain = (avgGain * (i - 1) + gain) / i
          avgLoss = (avgLoss * (i - 1) + loss) / i
          if (i === period) result.push(null)
          continue
        }
        
        avgGain = (avgGain * (period - 1) + gain) / period
        avgLoss = (avgLoss * (period - 1) + loss) / period
        
        const rs = avgLoss === 0 ? 100 : avgGain / avgLoss
        result.push(parseFloat((100 - 100 / (1 + rs)).toFixed(2)))
      }
      
      return result
    },
    
    calcMACD(closes) {
      const ema12 = this.calcEMA(closes, 12)
      const ema26 = this.calcEMA(closes, 26)
      const dif = ema12.map((v, i) => v - ema26[i])
      const dea = this.calcEMA(dif, 9)
      const histogram = dif.map((v, i) => parseFloat(((v - dea[i]) * 2).toFixed(2)))
      
      return {
        dif: ema12.map((v, i) => parseFloat((v - ema26[i]).toFixed(2))),
        dea: dea.map(v => parseFloat(v.toFixed(2))),
        histogram
      }
    },
    
    calcEMA(data, period) {
      const k = 2 / (period + 1)
      let ema = data[0]
      const result = [ema]
      for (let i = 1; i < data.length; i++) {
        ema = data[i] * k + ema * (1 - k)
        result.push(parseFloat(ema.toFixed(2)))
      }
      return result
    },
    
    patternType(t) { return t === 'bullish' ? 'success' : t === 'bearish' ? 'danger' : 'info' },
    typeText(t) { return t === 'bullish' ? '看涨' : t === 'bearish' ? '看跌' : '中性' }
  }
}
</script>

<style scoped>
.ai-chart-demo { padding: 16px; }
</style>
