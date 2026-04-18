<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>📊 选股策略回测</span>
        <el-button size="mini" type="primary" style="float:right;" @click="runBacktest" :loading="loading">🚀 开始回测</el-button>
      </div>
      <el-form :inline="true" size="small">
        <el-form-item label="策略">
          <el-select v-model="selectedStrategy" style="width:180px;">
            <el-option v-for="s in strategies" :key="s.name" :label="s.name" :value="s.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="起始日期"><el-date-picker v-model="startDate" value-format="yyyy-MM-dd" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="endDate" value-format="yyyy-MM-dd" /></el-form-item>
      </el-form>
    </el-card>

    <!-- 策略列表 -->
    <el-card style="margin-bottom:20px;">
      <div slot="header"><span>📋 预设策略</span></div>
      <el-table :data="strategies" style="width:100%">
        <el-table-column prop="name" label="策略名称" />
        <el-table-column prop="desc" label="策略描述" />
        <el-table-column prop="win_rate" label="胜率" width="100">
          <template slot-scope="{ row }"><span style="color:#67C23A;font-weight:600;">{{ row.win_rate }}%</span></template>
        </el-table-column>
        <el-table-column prop="annual_return" label="年化收益" width="100">
          <template slot-scope="{ row }"><span style="color:#67C23A;font-weight:600;">{{ row.annual_return }}%</span></template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template slot-scope="{ row }"><el-button size="mini" @click="selectedStrategy=row.name;runBacktest()">回测</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 回测结果 -->
    <el-card v-if="backtestResult">
      <div slot="header"><span>📈 回测结果</span></div>
      <el-row :gutter="20" style="margin-bottom:20px;">
        <el-col :span="6" v-for="m in metrics" :key="m.label">
          <div style="text-align:center;padding:12px;background:#f5f7fa;border-radius:8px;">
            <div style="color:#909399;font-size:12px;">{{ m.label }}</div>
            <div style="font-size:18px;font-weight:600;margin-top:4px;" :style="{color:m.color}">{{ m.value }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 收益曲线 -->
      <div id="backtest-chart" style="width:100%;height:300px;"></div>

      <!-- 交易记录 -->
      <el-table :data="backtestResult.trades" style="width:100%;margin-top:20px;">
        <el-table-column prop="date" label="日期" width="110" />
        <el-table-column prop="code" label="代码" width="110" />
        <el-table-column prop="action" label="操作" width="80">
          <template slot-scope="{ row }"><el-tag size="mini" :type="row.action==='买入'?'success':'danger'">{{ row.action }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="80" />
        <el-table-column prop="qty" label="数量" width="80" />
        <el-table-column prop="pnl" label="盈亏" width="100">
          <template slot-scope="{ row }"><span :style="{color: row.pnl>0?'#67C23A':'#F56C6C'}">{{ row.pnl>0?'+':'' }}{{ row.pnl }}</span></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'

export default {
  name: 'StrategyBacktest',
  data() {
    return {
      strategies: [],
      selectedStrategy: '',
      startDate: '2025-01-01',
      endDate: '2026-04-18',
      loading: false,
      backtestResult: null,
      chart: null
    }
  },
  computed: {
    metrics() {
      const r = this.backtestResult
      if (!r) return []
      return [
        { label: '总收益', value: r.total_return + '%', color: r.total_return > 0 ? '#67C23A' : '#F56C6C' },
        { label: '年化收益', value: r.annual_return + '%', color: '#409EFF' },
        { label: '最大回撤', value: r.max_drawdown + '%', color: '#F56C6C' },
        { label: '夏普比率', value: r.sharpe, color: r.sharpe > 1 ? '#67C23A' : '#E6A23C' },
        { label: '胜率', value: r.win_rate + '%', color: r.win_rate > 55 ? '#67C23A' : '#E6A23C' },
        { label: '交易次数', value: r.total_trades, color: '#303133' }
      ]
    }
  },
  created() { this.fetchStrategies() },
  mounted() { this.chart = echarts.init(document.getElementById('backtest-chart')); window.addEventListener('resize', () => this.chart?.resize()) },
  methods: {
    async fetchStrategies() {
      try {
        const { data } = await request.get('/api/strategy-backtest')
        if (data.code === 200) { this.strategies = data.data.strategies; this.selectedStrategy = this.strategies[0]?.name }
      } catch (e) {}
    },
    async runBacktest() {
      this.loading = true
      try {
        const { data } = await request.post('/api/strategy-backtest', {
          strategy: this.selectedStrategy,
          start_date: this.startDate,
          end_date: this.endDate
        })
        if (data.code === 200) {
          this.backtestResult = data.data
          this.renderChart()
        }
      } catch (e) { this.$message.error('回测失败') }
      finally { this.loading = false }
    },
    renderChart() {
      const eq = this.backtestResult.equity_curve || []
      const option = {
        tooltip: { trigger: 'axis' },
        grid: { left: '8%', right: '5%', bottom: '10%' },
        xAxis: { type: 'category', data: eq.map((_, i) => i) },
        yAxis: { type: 'value', name: '资产' },
        series: [{ name: '资产曲线', type: 'line', data: eq, smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#409EFF' } }]
      }
      this.chart?.setOption(option, true)
    }
  }
}
</script>
