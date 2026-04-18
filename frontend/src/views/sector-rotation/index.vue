<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>🔄 板块轮动分析</span>
        <el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button>
      </div>
    </el-card>

    <!-- 板块排行 -->
    <el-card style="margin-bottom:20px;">
      <div slot="header"><span>📊 板块涨跌幅排行</span></div>
      <el-table :data="sectors" style="width:100%" v-loading="loading">
        <el-table-column type="index" label="排名" width="60" />
        <el-table-column prop="sector" label="板块" width="100" />
        <el-table-column prop="avg_change" label="平均涨跌幅" width="120">
          <template slot-scope="{ row }">
            <span :style="{color: row.avg_change > 0 ? '#67C23A' : '#F56C6C', fontWeight:600}">
              {{ row.avg_change > 0 ? '+' : '' }}{{ row.avg_change }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="stock_count" label="成分股数" width="100" />
        <el-table-column prop="top_stock" label="领涨股" />
        <el-table-column label="涨跌幅" min-width="200">
          <template slot-scope="{ row }">
            <el-progress :percentage="Math.min(100, Math.abs(row.avg_change) * 10)" 
              :color="row.avg_change > 0 ? '#67C23A' : '#F56C6C'" 
              :stroke-width="16" 
              :format="() => ''" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 板块热力图 -->
    <el-card>
      <div slot="header"><span>🔥 板块热力图</span></div>
      <div id="sector-heatmap" style="width:100%;height:400px;"></div>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'

export default {
  name: 'SectorRotation',
  data() { return { sectors: [], loading: false, chart: null } },
  created() { this.fetchData() },
  mounted() {
    this.chart = echarts.init(document.getElementById('sector-heatmap'))
    window.addEventListener('resize', () => this.chart?.resize())
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/sector-rotation')
        if (data.code === 200) {
          this.sectors = data.data.sectors || []
          this.renderHeatmap()
        }
      } catch (e) { this.$message.error('获取板块数据失败') }
      finally { this.loading = false }
    },
    renderHeatmap() {
      const option = {
        tooltip: { position: 'top' },
        grid: { height: '70%', top: '10%' },
        xAxis: { type: 'category', data: this.sectors.map(s => s.sector), splitArea: { show: true } },
        yAxis: { type: 'category', data: ['涨跌幅'], splitArea: { show: true } },
        visualMap: {
          min: -5, max: 5, calculable: true, orient: 'horizontal', left: 'center', bottom: '0%',
          inRange: { color: ['#F56C6C', '#ffffff', '#67C23A'] }
        },
        series: [{
          name: '板块涨跌幅',
          type: 'heatmap',
          data: this.sectors.map((s, i) => [i, 0, s.avg_change]),
          label: { show: true, formatter: p => p.data[2] + '%' },
          itemStyle: { emphasis: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } }
        }]
      }
      this.chart?.setOption(option, true)
    }
  }
}
</script>
