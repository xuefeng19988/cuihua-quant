<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header"><span>📋 持仓分析报告</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div>
    </el-card>

    <el-row :gutter="20" v-if="report.sector_distribution">
      <el-col :span="12">
        <el-card><div slot="header"><span>📊 行业分布</span></div><div id="sector-chart" style="width:100%;height:300px;"></div></el-card>
      </el-col>
      <el-col :span="12">
        <el-card><div slot="header"><span>⚠️ 风险指标</span></div>
          <el-table :data="riskMetrics" style="width:100%">
            <el-table-column prop="name" label="指标" /><el-table-column prop="value" label="数值" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:20px;" v-if="report.sector_distribution">
      <div slot="header"><span>📈 行业盈亏</span></div>
      <el-table :data="report.sector_distribution">
        <el-table-column prop="sector" label="行业" width="100" />
        <el-table-column prop="weight" label="权重" width="100"><template slot-scope="{ row }">{{ row.weight }}%</template></el-table-column>
        <el-table-column label="盈亏" width="120"><template slot-scope="{ row }"><span :style="{color:row.pnl>0?'#67C23A':'#F56C6C'}">{{ row.pnl>0?'+':'' }}¥{{ row.pnl.toLocaleString() }}</span></template></el-table-column>
        <el-table-column label="占比"><template slot-scope="{ row }"><el-progress :percentage="row.weight" :color="row.pnl>0?'#67C23A':'#F56C6C'" /></template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'
export default {
  name: 'PortfolioReport', data() { return { report: {}, loading: false, chart: null } },
  computed: {
    riskMetrics() {
      const r = this.report.risk_metrics || {}
      return [
        { name: 'VaR (95%)', value: r.var_95 + '%' },
        { name: '最大回撤', value: r.max_drawdown + '%' },
        { name: '夏普比率', value: r.sharpe },
        { name: '波动率', value: r.volatility + '%' },
        { name: 'Beta', value: r.beta }
      ]
    }
  },
  created() { this.fetchData() },
  mounted() { this.chart = echarts.init(document.getElementById('sector-chart')); window.addEventListener('resize', () => this.chart?.resize()) },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/portfolio-report')
        if (data.code === 200) { this.report = data.data; this.renderChart() }
      } catch (e) { this.$message.error('获取数据失败') }
      finally { this.loading = false }
    },
    renderChart() {
      const d = this.report.sector_distribution || []
      const option = {
        tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
        series: [{ type: 'pie', radius: ['40%', '70%'], data: d.map(s => ({ value: s.weight, name: s.scene })) }]
      }
      this.chart?.setOption(option, true)
    }
  }
}
</script>
