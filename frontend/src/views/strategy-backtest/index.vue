<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📊 选股策略回测</span><el-button size="mini" type="primary" style="float:right;" @click="runBacktest" :loading="loading">🚀 开始回测</el-button></div></el-card>

    <!-- 策略选择 -->
    <el-card style="margin-bottom:20px;">
      <div slot="header"><span>⚙️ 回测参数</span></div>
      <el-form :inline="true">
        <el-form-item label="策略"><el-select v-model="selectedStrategy" style="width:180px;"><el-option v-for="s in strategies" :key="s.name" :label="s.name" :value="s.name" /></el-select></el-form-item>
        <el-form-item label="起始日期"><el-date-picker v-model="startDate" value-format="yyyy-MM-dd" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="endDate" value-format="yyyy-MM-dd" /></el-form-item>
        <el-form-item><el-button type="primary" @click="runBacktest" :loading="loading">🚀 回测</el-button></el-form-item>
      </el-form>
    </el-card>

    <!-- 策略对比图 -->
    <el-card style="margin-bottom:20px;">
      <div slot="header"><span>📊 策略收益对比</span></div>
      <bar-chart :data="strategyReturns" :categories="strategyNames" title="年化收益率" :height="300" />
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>📈 策略胜率对比</span></div>
          <bar-chart :data="strategyWinRates" :categories="strategyNames" title="胜率%" :height="280" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>📉 策略最大回撤对比</span></div>
          <bar-chart :data="strategyDrawdowns" :categories="strategyNames" title="最大回撤%" :height="280" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 策略列表 -->
    <el-card style="margin-top:20px;">
      <div slot="header"><span>📋 预设策略</span></div>
      <el-table :data="strategies" stripe>
        <el-table-column prop="name" label="策略名称" />
        <el-table-column prop="desc" label="描述" />
        <el-table-column prop="win_rate" label="胜率" width="100"><template slot-scope="{ row }"><span style="color:#67C23A;font-weight:600;">{{ row.win_rate }}%</span></template></el-table-column>
        <el-table-column prop="annual_return" label="年化收益" width="100"><template slot-scope="{ row }"><span style="color:#67C23A;font-weight:600;">{{ row.annual_return }}%</span></template></el-table-column>
        <el-table-column label="操作" width="80"><template slot-scope="{ row }"><el-button size="mini" @click="selectedStrategy=row.name;runBacktest()">回测</el-button></template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import { BarChart } from '@/components/charts'

export default {
  name: 'StrategyBacktest',
  components: { BarChart },
  data() {
    return {
      strategies: [],
      selectedStrategy: '',
      startDate: '2025-01-01',
      endDate: '2026-04-18',
      loading: false,
      results: null,
      strategyNames: ['双均线', 'RSI反转', 'MACD金叉', '布林突破'],
      strategyReturns: [22.4, 18.3, 15.7, 25.1],
      strategyWinRates: [62, 58, 55, 65],
      strategyDrawdowns: [-12.5, -8.2, -15.3, -18.7]
    }
  },
  created() { this.fetchStrategies() },
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
        const { data } = await request.post('/api/strategy-backtest', { strategy: this.selectedStrategy, start_date: this.startDate, end_date: this.endDate })
        if (data.code === 200) { this.results = data.data; this.$message.success('回测完成') }
      } catch (e) { this.$message.error('回测失败') }
      finally { this.loading = false }
    }
  }
}
</script>
