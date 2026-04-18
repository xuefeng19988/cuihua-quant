<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>🧠 情绪分析引擎</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div></el-card>
    <el-row :gutter="20">
      <el-col :span="8"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;">综合情绪分</div><div style="font-size:36px;font-weight:600;color:#409EFF;">{{ data.overall_score }}</div></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;">新闻情绪</div><div style="font-size:36px;font-weight:600;color:#67C23A;">{{ data.news_sentiment }}</div></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;">市场情绪</div><div style="font-size:36px;font-weight:600;color:#E6A23C;">{{ data.market_sentiment }}</div></el-card></el-col>
    </el-row>
    <el-card style="margin-top:20px;"><div slot="header"><span>📈 情绪趋势</span></div><div id="sentiment-trend" style="width:100%;height:300px;"></div></el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'
export default {
  name: 'SentimentEngine', data() { return { data: {}, loading: false, chart: null } },
  created() { this.fetchData() },
  mounted() { this.chart = echarts.init(document.getElementById('sentiment-trend')); window.addEventListener('resize', () => this.chart?.resize()) },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/sentiment-engine')
        if (data.code === 200) { this.data = data.data; this.renderChart() }
      } catch (e) { this.$message.error('获取失败') }
      finally { this.loading = false }
    },
    renderChart() {
      const t = this.data.trend || []
      this.chart?.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: t.map(i => i.date) },
        yAxis: { type: 'value', min: 0, max: 100 },
        series: [{ name: '情绪分', type: 'line', data: t.map(i => i.score), smooth: true, areaStyle: { opacity: 0.3 } }]
      }, true)
    }
  }
}
</script>
