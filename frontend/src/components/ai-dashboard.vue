/**
 * Phase 313: AI 智能看板
 * 自动聚合多维度数据，AI 生成洞察和摘要
 */
<template>
  <div class="ai-dashboard">
    <el-row :gutter="16">
      <!-- 顶部核心指标 -->
      <el-col :span="24">
        <el-card shadow="hover" class="summary-card">
          <div slot="header">
            <span>🤖 AI 市场洞察</span>
            <el-tag size="mini" type="success" v-if="marketStatus === 'bull'">牛市格局</el-tag>
            <el-tag size="mini" type="danger" v-else-if="marketStatus === 'bear'">熊市格局</el-tag>
            <el-tag size="mini" v-else>震荡格局</el-tag>
          </div>
          <el-row :gutter="20">
            <el-col :span="6" v-for="item in coreMetrics" :key="item.label">
              <div class="metric-item">
                <div class="metric-value" :style="{ color: item.color }">{{ item.value }}</div>
                <div class="metric-label">{{ item.label }}</div>
                <div class="metric-change" v-if="item.change" :style="{ color: item.changeColor }">
                  {{ item.change }}
                </div>
              </div>
            </el-col>
          </el-row>
          <el-divider></el-divider>
          <div class="ai-summary" v-if="aiSummary">
            <p class="summary-text">💡 {{ aiSummary }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="16" style="margin-top: 16px;">
      <!-- 左侧：板块热力图 -->
      <el-col :span="16">
        <el-card shadow="hover">
          <div slot="header">🔥 板块热力图</div>
          <div ref="heatmapChart" style="width:100%;height:300px;"></div>
        </el-card>
      </el-col>
      
      <!-- 右侧：资金流向 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <div slot="header">💰 资金流向</div>
          <div ref="capitalFlowChart" style="width:100%;height:300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="16" style="margin-top: 16px;">
      <!-- 领涨/领跌股 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header">📈 今日领涨 Top 5</div>
          <el-table :data="topGainers" stripe border size="mini">
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="price" label="价格" width="80" />
            <el-table-column prop="change" label="涨跌幅" width="100">
              <template slot-scope="{row}">
                <span :style="{ color: row.change > 0 ? '#ef232a' : '#14b143' }">
                  {{ row.change > 0 ? '+' : ''}}{{ row.change }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="AI信号" width="80">
              <template slot-scope="{row}">
                <el-tag size="mini" :type="row.signal === 'buy' ? 'success' : 'danger'">
                  {{ row.signal === 'buy' ? '🟢' : '🔴' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header">📉 今日领跌 Top 5</div>
          <el-table :data="topLosers" stripe border size="mini">
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="price" label="价格" width="80" />
            <el-table-column prop="change" label="涨跌幅" width="100">
              <template slot-scope="{row}">
                <span :style="{ color: row.change > 0 ? '#ef232a' : '#14b143' }">
                  {{ row.change > 0 ? '+' : ''}}{{ row.change }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="AI信号" width="80">
              <template slot-scope="{row}">
                <el-tag size="mini" :type="row.signal === 'buy' ? 'success' : 'danger'">
                  {{ row.signal === 'buy' ? '🟢' : '🔴' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="16" style="margin-top: 16px;">
      <!-- AI 机会扫描 -->
      <el-col :span="24">
        <el-card shadow="hover">
          <div slot="header">
            <span>🎯 AI 机会扫描</span>
            <el-button size="mini" type="primary" @click="scanOpportunities" :loading="scanning">
              🔍 立即扫描
            </el-button>
          </div>
          <el-row :gutter="12">
            <el-col :span="8" v-for="opp in opportunities" :key="opp.code">
              <el-card shadow="hover" class="opportunity-card">
                <div class="opp-header">
                  <span class="opp-name">{{ opp.name }}</span>
                  <el-tag size="mini" :type="opp.signal === 'buy' ? 'success' : 'danger'">
                    {{ opp.signal === 'buy' ? '买入机会' : '卖出风险' }}
                  </el-tag>
                </div>
                <div class="opp-score">
                  <el-progress type="dashboard" :percentage="opp.score" :color="progressColor"
                    :stroke-width="10" style="width:80px;" />
                </div>
                <div class="opp-reasons">
                  <div v-for="r in opp.reasons" :key="r" class="reason-item">✓ {{ r }}</div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          <el-empty v-if="!opportunities.length" description="点击"立即扫描"发现机会" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'AIDashboard',
  data() {
    return {
      marketStatus: 'neutral',
      aiSummary: '',
      coreMetrics: [],
      topGainers: [],
      topLosers: [],
      opportunities: [],
      scanning: false,
      progressColor: [
        { color: '#14b143', percentage: 40 },
        { color: '#e6a23c', percentage: 60 },
        { color: '#f56c6c', percentage: 80 },
        { color: '#ef232a', percentage: 100 }
      ]
    }
  },
  mounted() {
    this.loadData()
    this.renderHeatmap()
    this.renderCapitalFlow()
  },
  methods: {
    async loadData() {
      // 模拟数据 - 实际应从API获取
      this.coreMetrics = [
        { label: '上证指数', value: '3,285.42', change: '+0.85%', color: '#ef232a', changeColor: '#ef232a' },
        { label: '深证成指', value: '10,892.15', change: '+1.23%', color: '#ef232a', changeColor: '#ef232a' },
        { label: '创业板指', value: '2,156.78', change: '-0.32%', color: '#14b143', changeColor: '#14b143' },
        { label: '成交额', value: '8,523亿', change: '+12.5%', color: '#409EFF', changeColor: '#ef232a' }
      ]
      
      this.marketStatus = 'bull'
      this.aiSummary = '今日市场呈现结构性行情，科技板块领涨，建议关注AI算力、半导体方向。量能温和放大，短期偏多格局。'
      
      this.topGainers = [
        { name: '中科曙光', price: 45.32, change: 9.98, signal: 'buy' },
        { name: '工业富联', price: 28.15, change: 8.56, signal: 'buy' },
        { name: '寒武纪', price: 125.80, change: 7.23, signal: 'buy' },
        { name: '金山办公', price: 285.40, change: 6.15, signal: 'buy' },
        { name: '中芯国际', price: 52.30, change: 5.82, signal: 'hold' }
      ]
      
      this.topLosers = [
        { name: '宁德时代', price: 185.20, change: -4.25, signal: 'sell' },
        { name: '隆基绿能', price: 22.35, change: -3.80, signal: 'sell' },
        { name: '药明康德', price: 48.90, change: -3.15, signal: 'hold' },
        { name: '比亚迪', price: 245.60, change: -2.50, signal: 'hold' },
        { name: '五粮液', price: 135.80, change: -1.85, signal: 'hold' }
      ]
      
      this.opportunities = [
        {
          code: '688256', name: '寒武纪', score: 92, signal: 'buy',
          reasons: ['突破年线压制', '量能持续放大', '板块龙头领涨']
        },
        {
          code: '002415', name: '海康威视', score: 78, signal: 'buy',
          reasons: ['底部放量', 'MACD金叉', '外资持续买入']
        },
        {
          code: '300750', name: '宁德时代', score: 35, signal: 'sell',
          reasons: ['破位下行', '资金流出', '行业利空']
        }
      ]
    },

    renderHeatmap() {
      const el = this.$refs.heatmapChart
      if (!el) return
      const chart = echarts.init(el)
      
      const sectors = ['科技', '消费', '医药', '金融', '能源', '制造', '地产', '传媒']
      const values = [4.5, 2.3, -1.2, 1.8, -0.5, 3.2, -2.1, 1.5]
      
      const data = sectors.map((name, i) => [i, 0, values[i]])
      
      chart.setOption({
        tooltip: { formatter: p => `${sectors[p.value[0]]}: ${p.value[2]}%` },
        grid: { top: '10%', bottom: '10%', left: '5%', right: '5%' },
        xAxis: { type: 'category', show: false },
        yAxis: { type: 'category', show: false },
        visualMap: {
          min: -3, max: 5, calculable: true, orient: 'horizontal',
          left: 'center', bottom: '0%',
          inRange: { color: ['#14b143', '#ffffff', '#ef232a'] }
        },
        series: [{
          type: 'heatmap', data,
          label: { show: true, formatter: p => `${sectors[p.value[0]]}\n${p.value[2]}%` },
          itemStyle: { borderWidth: 2, borderColor: '#fff' }
        }]
      })
    },

    renderCapitalFlow() {
      const el = this.$refs.capitalFlowChart
      if (!el) return
      const chart = echarts.init(el)
      
      chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['主力净流入', '散户净流入'] },
        grid: { left: '15%', right: '10%', top: '15%', bottom: '15%' },
        xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五'] },
        yAxis: { type: 'value', name: '亿元' },
        series: [
          { name: '主力净流入', type: 'bar', data: [120, 85, -45, 150, 95],
            itemStyle: { color: p => p.value > 0 ? '#ef232a' : '#14b143' } },
          { name: '散户净流入', type: 'bar', data: [-30, 45, 80, -60, -25],
            itemStyle: { color: p => p.value > 0 ? '#ef232a' : '#14b143' } }
        ]
      })
    },

    async scanOpportunities() {
      this.scanning = true
      // 模拟扫描
      await new Promise(r => setTimeout(r, 1500))
      this.scanning = false
      this.$message.success('扫描完成，发现 3 个机会')
    }
  }
}
</script>

<style scoped>
.ai-dashboard { padding: 12px; }
.summary-card .metric-item { text-align: center; padding: 8px; }
.metric-value { font-size: 24px; font-weight: bold; }
.metric-label { font-size: 12px; color: #909399; margin-top: 4px; }
.metric-change { font-size: 13px; margin-top: 4px; }
.ai-summary { padding: 12px; background: #f5f7fa; border-radius: 8px; }
.summary-text { margin: 0; font-size: 14px; line-height: 1.6; color: #303133; }
.opportunity-card { margin-bottom: 12px; }
.opp-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.opp-name { font-size: 16px; font-weight: bold; }
.opp-score { text-align: center; margin: 12px 0; }
.opp-reasons { margin-top: 8px; }
.reason-item { font-size: 12px; color: #606266; margin: 4px 0; }
</style>
