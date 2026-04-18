<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📊 绩效看板</span>
      <el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button>
    </div></el-card>

    <!-- 核心指标 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="m in metrics" :key="m.label">
        <el-card shadow="hover">
          <div style="color:#909399;font-size:13px;">{{ m.label }}</div>
          <div style="font-size:20px;font-weight:600;margin-top:8px;" :style="{color:m.color}">{{ m.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="20" style="margin-top:20px;">
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>📈 收益曲线</span></div>
          <div id="equity-chart" style="width:100%;height:300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>📉 回撤曲线</span></div>
          <div id="drawdown-chart" style="width:100%;height:300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top:20px;">
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📊 盈亏分布</span></div>
          <pie-chart :data="winLossData" title="盈利 vs 亏损" :height="250" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📈 胜率趋势</span></div>
          <line-chart :categories="winRateCategories" :series="winRateSeries" title="月度胜率" :height="250" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📊 夏普比率趋势</span></div>
          <line-chart :categories="sharpeCategories" :series="sharpeSeries" title="滚动夏普" :height="250" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 月度收益 -->
    <el-card style="margin-top:20px;">
      <div slot="header"><span>📅 月度收益</span></div>
      <el-table :data="monthly" v-loading="loading" stripe>
        <el-table-column prop="month" label="月份" width="100" />
        <el-table-column prop="return_pct" label="收益率">
          <template slot-scope="{ row }">
            <span :style="{color: row.return_pct > 0 ? '#67C23A' : '#F56C6C', fontWeight:600}">{{ row.return_pct > 0 ? '+' : '' }}{{ row.return_pct }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="benchmark" label="基准" width="80" />
        <el-table-column prop="alpha" label="Alpha" width="80" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'
import { PieChart, LineChart } from '@/components/charts'

export default {
  name: 'Performance',
  components: { PieChart, LineChart },
  data() {
    return {
      metrics: [
        { label: '累计收益', value: '--', color: '#303133' },
        { label: '年化收益', value: '--', color: '#303133' },
        { label: '夏普比率', value: '--', color: '#303133' },
        { label: '最大回撤', value: '--', color: '#303133' }
      ],
      monthly: [],
      loading: false,
      equityChart: null,
      drawdownChart: null,
      curveDays: 90,
      // 图表数据
      winRateCategories: ['1月', '2月', '3月', '4月', '5月', '6月'],
      winRateSeries: [{ name: '胜率', data: [62, 58, 65, 70, 68, 62.5], color: '#409EFF' }],
      sharpeCategories: ['1月', '2月', '3月', '4月', '5月', '6月'],
      sharpeSeries: [{ name: '夏普', data: [1.2, 1.35, 1.28, 1.42, 1.38, 1.35], color: '#67C23A' }]
    }
  },
  computed: {
    winLossData() {
      return [
        { value: 62, name: '盈利交易' },
        { value: 38, name: '亏损交易' }
      ]
    }
  },
  created() { this.fetchData() },
  mounted() {
    this.equityChart = echarts.init(document.getElementById('equity-chart'))
    this.drawdownChart = echarts.init(document.getElementById('drawdown-chart'))
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.equityChart) this.equityChart.dispose()
    if (this.drawdownChart) this.drawdownChart.dispose()
  },
  methods: {
    handleResize() {
      this.equityChart?.resize()
      this.drawdownChart?.resize()
    },
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/performance')
        if (data.code === 200) {
          const d = data.data
          this.metrics[0].value = d.total_return ? '+' + d.total_return + '%' : '--'
          this.metrics[0].color = d.total_return > 0 ? '#67C23A' : '#F56C6C'
          this.metrics[1].value = d.annual_return ? '+' + d.annual_return + '%' : '--'
          this.metrics[1].color = d.annual_return > 0 ? '#67C23A' : '#F56C6C'
          this.metrics[2].value = d.sharpe || '--'
          this.metrics[3].value = d.max_drawdown ? d.max_drawdown + '%' : '--'
          this.monthly = d.monthly || []
          this.renderEquityChart(d)
          this.renderDrawdownChart(d)
        }
      } catch (e) { this.$message.error('获取绩效数据失败') }
      finally { this.loading = false }
    },
    renderEquityChart(d) {
      const curve = d.equity_curve || [100, 102, 105, 103, 108, 112, 110, 115, 118, 115.2]
      const dates = curve.map((_, i) => `2026-${String(i+1).padStart(2,'0')}`)
      this.equityChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: 30, containLabel: true },
        xAxis: { type: 'category', data: dates, axisLabel: { color: '#d1d4dc' } },
        yAxis: { type: 'value', axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
        series: [{ type: 'line', data: curve, smooth: true, areaStyle: { color: '#409EFF', opacity: 0.3 }, itemStyle: { color: '#409EFF' } }]
      }, true)
    },
    renderDrawdownChart(d) {
      const dd = d.drawdown || [0, -1, -2, -3, -1, 0, -1, -2, -1, -0.5]
      const dates = dd.map((_, i) => `2026-${String(i+1).padStart(2,'0')}`)
      this.drawdownChart.setOption({
        tooltip: { formatter: '{b}: {c}%' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: 30, containLabel: true },
        xAxis: { type: 'category', data: dates, axisLabel: { color: '#d1d4dc' } },
        yAxis: { type: 'value', axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
        series: [{ type: 'line', data: dd, smooth: true, areaStyle: { color: '#F56C6C', opacity: 0.3 }, itemStyle: { color: '#F56C6C' } }]
      }, true)
    }
  }
}
</script>
