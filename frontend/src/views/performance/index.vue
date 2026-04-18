<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>📊 绩效看板</span>
        <div style="float:right;">
          <el-select v-model="curveDays" size="mini" style="width:100px;" @change="fetchCurve">
            <el-option :value="30" label="近30天" />
            <el-option :value="60" label="近60天" />
            <el-option :value="90" label="近90天" />
            <el-option :value="180" label="近180天" />
          </el-select>
          <el-button size="mini" @click="fetchData" style="margin-left:8px;">🔄 刷新</el-button>
        </div>
      </div>
    </el-card>

    <!-- 核心指标 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="m in metrics" :key="m.label">
        <el-card shadow="hover">
          <div style="color:#909399;font-size:13px;">{{ m.label }}</div>
          <div style="font-size:20px;font-weight:600;margin-top:8px;" :style="{color:m.color}">{{ m.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 收益曲线图 -->
    <el-card style="margin-top:20px;" v-loading="curveLoading">
      <div slot="header"><span>📈 收益曲线 vs 基准</span></div>
      <div id="equity-chart" style="width:100%;height:350px;"></div>
    </el-card>

    <!-- 回撤曲线 -->
    <el-card style="margin-top:20px;" v-loading="curveLoading">
      <div slot="header"><span>📉 回撤曲线</span></div>
      <div id="drawdown-chart" style="width:100%;height:200px;"></div>
    </el-card>

    <!-- 月度收益表 -->
    <el-card style="margin-top:20px;">
      <div slot="header"><span>📅 月度收益</span></div>
      <el-table :data="monthly" v-loading="loading">
        <el-table-column prop="month" label="月份" width="100" />
        <el-table-column prop="return_pct" label="收益率">
          <template slot-scope="{ row }">
            <span :style="{color: row.return_pct > 0 ? '#67C23A' : '#F56C6C', fontWeight:600}">
              {{ row.return_pct > 0 ? '+' : '' }}{{ row.return_pct }}%
            </span>
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

export default {
  name: 'Performance',
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
      curveLoading: false,
      curveDays: 90,
      equityChart: null,
      drawdownChart: null
    }
  },
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
  created() { this.fetchData(); this.fetchCurve() },
  methods: {
    handleResize() {
      this.equityChart && this.equityChart.resize()
      this.drawdownChart && this.drawdownChart.resize()
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
          this.metrics[3].color = '#F56C6C'
          this.monthly = d.monthly || []
        }
      } catch (e) { this.$message.error('获取绩效数据失败') }
      finally { this.loading = false }
    },
    async fetchCurve() {
      this.curveLoading = true
      try {
        const { data } = await request.get('/api/equity-curve', { params: { days: this.curveDays } })
        if (data.code === 200) {
          this.renderEquityChart(data.data)
          this.renderDrawdownChart(data.data)
        }
      } catch (e) { this.$message.error('获取收益曲线失败') }
      finally { this.curveLoading = false }
    },
    renderEquityChart(d) {
      const option = {
        tooltip: { trigger: 'axis' },
        legend: { data: ['策略收益', '基准收益'], top: 10 },
        grid: { left: '8%', right: '5%', bottom: '10%', top: 50 },
        xAxis: { type: 'category', data: d.dates, axisLine: { lineStyle: { color: '#8392A5' } } },
        yAxis: { scale: true, splitArea: { show: true } },
        series: [
          { name: '策略收益', type: 'line', data: d.equity, smooth: true, lineStyle: { width: 2 } },
          { name: '基准收益', type: 'line', data: d.benchmark, smooth: true, lineStyle: { type: 'dashed', width: 1 } }
        ]
      }
      this.equityChart.setOption(option, true)
    },
    renderDrawdownChart(d) {
      const option = {
        tooltip: { trigger: 'axis', formatter: '{b}<br/>回撤: {c}%' },
        grid: { left: '8%', right: '5%', bottom: '10%', top: 20 },
        xAxis: { type: 'category', data: d.dates, axisLine: { lineStyle: { color: '#8392A5' } } },
        yAxis: { scale: true },
        series: [{
          name: '回撤',
          type: 'line',
          data: d.drawdown,
          smooth: true,
          areaStyle: { color: 'rgba(245,108,108,0.3)' },
          lineStyle: { color: '#F56C6C', width: 1 },
          itemStyle: { color: '#F56C6C' }
        }]
      }
      this.drawdownChart.setOption(option, true)
    }
  }
}
</script>
