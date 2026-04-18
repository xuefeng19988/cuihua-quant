<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>💰 资金流向分析</span>
        <el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button>
      </div>
    </el-card>

    <!-- 资金流向排行 -->
    <el-card style="margin-bottom:20px;">
      <div slot="header"><span>📊 主力资金净流入排行</span></div>
      <el-table :data="flows" style="width:100%" v-loading="loading">
        <el-table-column type="index" label="排名" width="60" />
        <el-table-column prop="code" label="代码" width="110" />
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column prop="main_in" label="主力流入(万)" width="120">
          <template slot-scope="{ row }"><span style="color:#67C23A;">{{ row.main_in.toLocaleString() }}</span></template>
        </el-table-column>
        <el-table-column prop="main_out" label="主力流出(万)" width="120">
          <template slot-scope="{ row }"><span style="color:#F56C6C;">{{ row.main_out.toLocaleString() }}</span></template>
        </el-table-column>
        <el-table-column prop="net_main" label="主力净流入(万)" width="130">
          <template slot-scope="{ row }">
            <span :style="{color: row.net_main > 0 ? '#67C23A' : '#F56C6C', fontWeight:600}">
              {{ row.net_main > 0 ? '+' : '' }}{{ row.net_main.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="net_retail" label="散户净流入(万)" width="130">
          <template slot-scope="{ row }">
            <span :style="{color: row.net_retail > 0 ? '#67C23A' : '#F56C6C'}">
              {{ row.net_retail > 0 ? '+' : '' }}{{ row.net_retail.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="net_total" label="合计净流入(万)" width="140">
          <template slot-scope="{ row }">
            <span :style="{color: row.net_total > 0 ? '#67C23A' : '#F56C6C', fontWeight:600}">
              {{ row.net_total > 0 ? '+' : '' }}{{ row.net_total.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 资金流向图表 -->
    <el-card>
      <div slot="header"><span>📈 主力资金流向图</span></div>
      <div id="fund-flow-chart" style="width:100%;height:400px;"></div>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'

export default {
  name: 'FundFlow',
  data() { return { flows: [], loading: false, chart: null } },
  created() { this.fetchData() },
  mounted() {
    this.chart = echarts.init(document.getElementById('fund-flow-chart'))
    window.addEventListener('resize', () => this.chart?.resize())
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/fund-flow')
        if (data.code === 200) {
          this.flows = data.data.flows || []
          this.renderChart()
        }
      } catch (e) { this.$message.error('获取资金流向失败') }
      finally { this.loading = false }
    },
    renderChart() {
      const top10 = this.flows.slice(0, 10)
      const option = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: ['主力净流入', '散户净流入'], top: 10 },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value', axisLabel: { formatter: '{value}万' } },
        yAxis: { type: 'category', data: top10.map(f => f.name).reverse() },
        series: [
          { name: '主力净流入', type: 'bar', data: top10.map(f => f.net_main).reverse(), itemStyle: { color: p => p.value > 0 ? '#67C23A' : '#F56C6C' } },
          { name: '散户净流入', type: 'bar', data: top10.map(f => f.net_retail).reverse(), itemStyle: { color: p => p.value > 0 ? '#409EFF' : '#E6A23C' } }
        ]
      }
      this.chart?.setOption(option, true)
    }
  }
}
</script>
