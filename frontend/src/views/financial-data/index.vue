<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>💰 财务数据</span>
        <el-select v-model="selectedCode" size="mini" style="width:200px;float:right;" @change="loadFinancial">
          <el-option v-for="s in stocks" :key="s.code" :label="s.code + ' ' + s.name" :value="s.code" />
        </el-select>
      </div>
    </el-card>

    <!-- 核心财务指标 -->
    <el-row :gutter="20" v-if="financial.code">
      <el-col :span="16">
        <el-card>
          <div slot="header"><span>📊 核心指标</span></div>
          <el-row :gutter="20">
            <el-col :span="8" v-for="item in coreMetrics" :key="item.label">
              <div style="text-align:center;padding:16px;background:#f5f7fa;border-radius:8px;margin-bottom:12px;">
                <div style="color:#909399;font-size:13px;">{{ item.label }}</div>
                <div style="font-size:22px;font-weight:600;margin-top:8px;" :style="{color:item.color}">{{ item.value }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 季度趋势 -->
        <el-card style="margin-top:20px;">
          <div slot="header"><span>📈 季度趋势</span></div>
          <div id="financial-chart" style="width:100%;height:300px;"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📋 详细数据</span></div>
          <div v-for="item in details" :key="item.label" style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #eee;">
            <span style="color:#606266;">{{ item.label }}</span>
            <span style="font-weight:600;">{{ item.value }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!financial.code" description="请选择股票查看财务数据" />
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'

export default {
  name: 'FinancialData',
  data() {
    return {
      stocks: [],
      selectedCode: '',
      financial: {},
      chart: null
    }
  },
  computed: {
    coreMetrics() {
      const f = this.financial
      return [
        { label: '市盈率(PE)', value: f.pe ? f.pe.toFixed(2) : '-', color: f.pe < 20 ? '#67C23A' : f.pe > 40 ? '#F56C6C' : '#E6A23C' },
        { label: '市净率(PB)', value: f.pb ? f.pb.toFixed(2) : '-', color: f.pb < 2 ? '#67C23A' : '#E6A23C' },
        { label: 'ROE', value: f.roe ? f.roe.toFixed(2) + '%' : '-', color: f.roe > 15 ? '#67C23A' : '#409EFF' },
        { label: '毛利率', value: f.gross_margin ? f.gross_margin.toFixed(2) + '%' : '-', color: '#409EFF' },
        { label: '资产负债率', value: f.debt_ratio ? f.debt_ratio.toFixed(2) + '%' : '-', color: f.debt_ratio < 50 ? '#67C23A' : '#F56C6C' },
        { label: '股息率', value: f.dividend_yield ? f.dividend_yield.toFixed(2) + '%' : '-', color: '#E6A23C' }
      ]
    },
    details() {
      const f = this.financial
      return [
        { label: '每股收益(EPS)', value: f.eps ? f.eps.toFixed(2) + '元' : '-' },
        { label: '营业收入', value: f.revenue ? f.revenue.toFixed(0) + '亿' : '-' },
        { label: '净利润', value: f.net_profit ? f.net_profit.toFixed(0) + '亿' : '-' },
        { label: '总市值', value: f.market_cap ? f.market_cap.toFixed(0) + '亿' : '-' }
      ]
    }
  },
  created() { this.fetchStocks() },
  mounted() {
    this.chart = echarts.init(document.getElementById('financial-chart'))
    window.addEventListener('resize', () => this.chart?.resize())
  },
  methods: {
    async fetchStocks() {
      try {
        const { data } = await request.get('/api/stocks')
        if (data.code === 200) this.stocks = data.data.list || []
      } catch (e) {}
    },
    async loadFinancial() {
      if (!this.selectedCode) return
      try {
        const { data } = await request.get(`/api/financial/${this.selectedCode}`)
        if (data.code === 200) {
          this.financial = data.data
          this.renderChart()
        }
      } catch (e) { this.$message.error('获取财务数据失败') }
    },
    renderChart() {
      const q = this.financial.quarterly || []
      const option = {
        tooltip: { trigger: 'axis' },
        legend: { data: ['营业收入', '净利润'], top: 10 },
        grid: { left: '8%', right: '5%', bottom: '10%' },
        xAxis: { type: 'category', data: q.map(i => i.quarter) },
        yAxis: { type: 'value', name: '亿元' },
        series: [
          { name: '营业收入', type: 'bar', data: q.map(i => i.revenue), itemStyle: { color: '#409EFF' } },
          { name: '净利润', type: 'bar', data: q.map(i => i.profit), itemStyle: { color: '#67C23A' } }
        ]
      }
      this.chart?.setOption(option, true)
    }
  }
}
</script>
