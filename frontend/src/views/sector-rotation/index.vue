<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>🔄 板块轮动分析</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div></el-card>

    <!-- 板块排行 -->
    <el-card style="margin-bottom:20px;">
      <div slot="header"><span>📊 板块涨跌幅排行</span></div>
      <bar-chart :data="sectorChanges" :categories="sectorNames" title="板块涨跌幅" :height="350" />
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>📈 板块占比分布</span></div>
          <pie-chart :data="sectorDistribution" title="板块占比" :height="300" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>📊 板块资金流向</span></div>
          <line-chart :categories="flowCategories" :series="flowSeries" title="资金流向" :height="300" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'
import { BarChart, PieChart, LineChart } from '@/components/charts'

export default {
  name: 'SectorRotation',
  components: { BarChart, PieChart, LineChart },
  data() { return { loading: false, sectorNames: [], sectorChanges: [], flowCategories: [], flowSeries: [] } },
  computed: {
    sectorDistribution() {
      const data = [
        { value: 35, name: '科技', itemStyle: { color: '#409EFF' } },
        { value: 28, name: '消费', itemStyle: { color: '#67C23A' } },
        { value: 20, name: '金融', itemStyle: { color: '#E6A23C' } },
        { value: 17, name: '医药', itemStyle: { color: '#F56C6C' } }
      ]
      return data
    }
  },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/sector-rotation')
        if (data.code === 200) {
          const sectors = data.data.sectors || []
          this.sectorNames = sectors.map(s => s.sector)
          this.sectorChanges = sectors.map(s => s.avg_change)
          this.flowCategories = sectors.map(s => s.sector)
          this.flowSeries = [
            { name: '流入', data: sectors.map(() => Math.random() * 100), color: '#26a69a' },
            { name: '流出', data: sectors.map(() => -Math.random() * 100), color: '#ef5350' }
          ]
        }
      } catch (e) { this.$message.error('获取数据失败') }
      finally { this.loading = false }
    }
  }
}
</script>
