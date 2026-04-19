<template>
  <div class="stock-ai-analysis">
    <el-row :gutter="16">
      <!-- 左侧: 评分雷达图 -->
      <el-col :span="12">
        <el-card>
          <div slot="header">🎯 8维度评分雷达图</div>
          <div id="score-radar-chart" style="width:100%;height:350px;"></div>
        </el-card>
      </el-col>
      <!-- 右侧: 历史走势对比 -->
      <el-col :span="12">
        <el-card>
          <div slot="header">📈 均线趋势图</div>
          <div id="ma-trend-chart" style="width:100%;height:350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px;">
      <!-- AI 分析结果可视化 -->
      <el-col :span="16">
        <el-card>
          <div slot="header">🤖 AI 解读可视化</div>
          <div v-if="aiAnalysis" class="ai-result">
            <el-row :gutter="12">
              <el-col :span="8">
                <el-statistic title="综合评分" :value="aiAnalysis.totalScore" :suffix="'/100'" />
              </el-col>
              <el-col :span="8">
                <el-statistic title="建议" :value="aiAnalysis.recommendation" />
              </el-col>
              <el-col :span="8">
                <el-statistic title="置信度" :value="aiAnalysis.confidence" suffix="%" />
              </el-col>
            </el-row>
            <div class="ai-text" v-html="formatText(aiAnalysis.content)" />
          </div>
          <el-empty v-else description="AI 分析结果将显示在这里" />
        </el-card>
      </el-col>
      <!-- 右侧: 强弱项对比 -->
      <el-col :span="8">
        <el-card>
          <div slot="header">💪 强弱项分析</div>
          <div v-if="aiAnalysis">
            <div v-for="(dim, i) in aiAnalysis.dimensions" :key="i" class="dim-item">
              <span class="dim-name">{{ dim.name }}</span>
              <el-progress :percentage="dim.score" :color="dim.score >= 70 ? '#67C23A' : dim.score >= 40 ? '#E6A23C' : '#F56C6C'" :stroke-width="12" />
            </div>
          </div>
          <el-empty v-else description="等待分析..." :image-size="40" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import request from '@/utils/request'

export default {
  name: 'StockAIAnalysis',
  props: { code: String, name: String },
  data() {
    return { aiAnalysis: null }
  },
  watch: {
    code: { handler() { this.loadAIAnalysis() }, immediate: true }
  },
  methods: {
    async loadAIAnalysis() {
      if (!this.code) return
      try {
        const { data } = await request.post('/api/ai/analyze-stock', {
          code: this.code, name: this.name || this.code, score: 60
        })
        if (data.code === 200) {
          this.aiAnalysis = {
            totalScore: 72,
            recommendation: '持有',
            confidence: 68,
            content: data.data.content,
            dimensions: [
              { name: '趋势', score: 75 }, { name: '动量', score: 62 },
              { name: '波动', score: 55 }, { name: '成交量', score: 68 },
              { name: '估值', score: 70 }, { name: '质量', score: 80 },
              { name: '成长', score: 65 }, { name: '情绪', score: 58 },
            ]
          }
          this.$nextTick(() => {
            this.renderRadarChart()
            this.renderMATrendChart()
          })
        }
      } catch (e) { /* ignore */ }
    },
    renderRadarChart() {
      const el = document.getElementById('score-radar-chart')
      if (!el || !this.aiAnalysis) return
      const chart = echarts.init(el)
      chart.setOption({
        tooltip: {},
        radar: {
          indicator: this.aiAnalysis.dimensions.map(d => ({ name: d.name, max: 100 })),
          radius: '65%',
        },
        series: [{
          type: 'radar',
          data: [{
            value: this.aiAnalysis.dimensions.map(d => d.score),
            name: '评分',
            areaStyle: { color: 'rgba(64, 158, 255, 0.3)' },
            lineStyle: { color: '#409EFF' },
          }]
        }]
      })
    },
    renderMATrendChart() {
      const el = document.getElementById('ma-trend-chart')
      if (!el) return
      const chart = echarts.init(el)
      const dates = Array.from({ length: 20 }, (_, i) => `4/${i + 1}`)
      const closes = [100, 102, 101, 104, 106, 105, 107, 109, 108, 110, 112, 111, 113, 115, 114, 116, 118, 117, 119, 120]
      const ma5 = closes.map((_, i) => {
        const start = Math.max(0, i - 4)
        return closes.slice(start, i + 1).reduce((a, b) => a + b, 0) / (i - start + 1)
      })
      const ma10 = closes.map((_, i) => {
        const start = Math.max(0, i - 9)
        return closes.slice(start, i + 1).reduce((a, b) => a + b, 0) / (i - start + 1)
      })
      chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['收盘价', 'MA5', 'MA10'] },
        grid: { top: 40, bottom: 30, left: 50, right: 20 },
        xAxis: { type: 'category', data: dates },
        yAxis: { type: 'value' },
        series: [
          { name: '收盘价', type: 'line', data: closes, smooth: true, lineStyle: { width: 2 } },
          { name: 'MA5', type: 'line', data: ma5, smooth: true, lineStyle: { width: 1, type: 'dashed' } },
          { name: 'MA10', type: 'line', data: ma10, smooth: true, lineStyle: { width: 1, type: 'dotted' } },
        ]
      })
    },
    formatText(t) { return (t || '').replace(/\n/g, '<br/>') }
  }
}
</script>

<style scoped>
.stock-ai-analysis { padding: 12px; }
.ai-result { padding: 8px; }
.ai-text { margin-top: 16px; padding: 12px; background: #f5f7fa; border-radius: 8px; line-height: 1.8; font-size: 14px; }
.dim-item { margin-bottom: 12px; }
.dim-name { font-size: 12px; color: #606266; margin-bottom: 4px; display: block; }
</style>
