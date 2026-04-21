<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>⚠️ 风险监控</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div></el-card>

    <!-- 风险指标 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>🕸️ 风险指标雷达图</span></div>
          <radar-chart :indicators="riskIndicators" :data="riskData" title="风险评估" :height="350" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>📊 风险等级分布</span></div>
          <pie-chart :data="riskDistribution" title="风险分布" :height="350" />
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:20px;">
      <div slot="header"><span>📈 回撤趋势</span></div>
      <line-chart :categories="drawdownCategories" :series="drawdownSeries" title="近30日回撤" :height="300" />
    </el-card>

    <el-card style="margin-top:20px;">
      <div slot="header"><span>📋 风险预警列表</span></div>
      <el-table :data="riskAlerts" stripe>
        <el-table-column prop="time" label="时间" width="160" />
        <el-table-column prop="level" label="等级" width="80">
          <template slot-scope="{ row }"><el-tag size="mini" :type="row.level === 'high' ? 'danger' : row.level === 'medium' ? 'warning' : 'info'">{{ row.level }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="message" label="预警信息" />
        <el-table-column prop="status" label="状态" width="80" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import { RadarChart, PieChart, LineChart } from '@/components/charts'

export default {
  name: 'Risk',
  components: { RadarChart, PieChart, LineChart },
  data() {
    return {
      loading: false,
      riskIndicators: [
        { name: '波动率', max: 100 },
        { name: '最大回撤', max: 100 },
        { name: 'VaR', max: 100 },
        { name: '集中度', max: 100 },
        { name: '流动性', max: 100 },
        { name: '杠杆率', max: 100 }
      ],
      riskData: [35, 28, 42, 30, 65, 20],
      drawdownCategories: Array.from({ length: 30 }, (_, i) => `${i+1}日`),
      drawdownSeries: [{ name: '回撤%', data: Array.from({ length: 30 }, () => -Math.random() * 10), color: '#F56C6C' }],
      riskAlerts: [
        { time: '2026-04-18 14:30', level: 'high', message: '单只股票仓位超过20%', status: '未处理' },
        { time: '2026-04-18 10:15', level: 'medium', message: '组合回撤接近5%', status: '已处理' },
        { time: '2026-04-17 15:00', level: 'low', message: '交易量异常', status: '已处理' }
      ]
    }
  },
  computed: {
    riskDistribution() {
      return [
        { value: 2, name: '高风险', itemStyle: { color: '#F56C6C' } },
        { value: 5, name: '中风险', itemStyle: { color: '#E6A23C' } },
        { value: 15, name: '低风险', itemStyle: { color: '#67C23A' } }
      ]
    }
  },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try { const { data } = await request.get('/risk'); if (data.code === 200) {} }
      catch (e) {}
      finally { this.loading = false }
    }
  }
}
</script>
