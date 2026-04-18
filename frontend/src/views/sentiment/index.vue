<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📊 市场情绪指标</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div></el-card>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card><div slot="header"><span>😱 恐慌/贪婪指数</span></div><div style="text-align:center;"><div style="font-size:48px;font-weight:600;" :style="{color:sentiment.fear_greed?.color}">{{ sentiment.fear_greed?.value }}</div><el-tag size="medium" :type="sentiment.fear_greed?.value>60?'success':'warning'">{{ sentiment.fear_greed?.level }}</el-tag></div></el-card>
      </el-col>
      <el-col :span="12">
        <el-card><div slot="header"><span>📈 市场广度</span></div>
          <el-row :gutter="20"><el-col :span="12"><div style="color:#67C23A;font-size:20px;font-weight:600;">↑ {{ sentiment.market_breadth?.advance }}</div><div style="color:#909399;">上涨</div></el-col><el-col :span="12"><div style="color:#F56C6C;font-size:20px;font-weight:600;">↓ {{ sentiment.market_breadth?.decline }}</div><div style="color:#909399;">下跌</div></el-col></el-row>
        </el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top:20px;"><div slot="header"><span>📊 情绪历史</span></div><div id="sentiment-chart" style="width:100%;height:300px;"></div></el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'
export default {
  name: 'Sentiment', data() { return { sentiment: {}, loading: false, chart: null } },
  created() { this.fetchData() },
  mounted() { this.chart = echarts.init(document.getElementById('sentiment-chart')); window.addEventListener('resize', () => this.chart?.resize()) },
  methods: {
    async fetchData() {
      this.loading = true
      try { const { data } = await request.get('/api/sentiment'); if (data.code === 200) { this.sentiment = data.data; this.renderChart() } }
      catch (e) { this.$message.error('获取数据失败') }
      finally { this.loading = false }
    },
    renderChart() {
      const h = this.sentiment.sentiment_history || []
      const option = {
        tooltip: { trigger: 'axis' }, grid: { left: '8%', right: '5%', bottom: '10%' },
        xAxis: { type: 'category', data: h.map(i => i.date) }, yAxis: { type: 'value', min: 0, max: 100 },
        series: [{ name: '情绪指数', type: 'line', data: h.map(i => i.value), smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#409EFF' } }]
      }
      this.chart?.setOption(option, true)
    }
  }
}
</script>
