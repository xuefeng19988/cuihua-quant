<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📊 宏观数据面板</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div></el-card>
    <el-row :gutter="20">
      <el-col :span="8" v-for="m in metrics" :key="m.name">
        <el-card shadow="hover"><div style="color:#909399;font-size:13px;">{{ m.name }}</div><div style="font-size:24px;font-weight:600;margin:8px 0;" :style="{color:m.trend==='up'?'#67C23A':m.trend==='down'?'#F56C6C':'#409EFF'}">{{ m.value }}{{ m.unit }}</div><el-tag size="mini" :type="m.trend==='up'?'success':m.trend==='down'?'danger':''">{{ m.date }}</el-tag></el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top:20px;"><div slot="header"><span>📈 历史趋势</span></div><div id="macro-chart" style="width:100%;height:300px;"></div></el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'
export default {
  name: 'MacroData', data() { return { macro: {}, loading: false, chart: null } },
  computed: {
    metrics() {
      const m = this.macro
      return [
        { name: 'GDP增速', value: m.gdp?.value, unit: m.gdp?.unit, date: m.gdp?.date, trend: m.gdp?.trend },
        { name: 'CPI', value: m.cpi?.value, unit: m.cpi?.unit, date: m.cpi?.date, trend: m.cpi?.trend },
        { name: 'PMI', value: m.pmi?.value, unit: m.pmi?.unit, date: m.pmi?.date, trend: m.pmi?.trend },
        { name: 'M2增速', value: m.m2?.value, unit: m.m2?.unit, date: m.m2?.date, trend: m.m2?.trend },
        { name: '失业率', value: m.unemployment?.value, unit: m.unemployment?.unit, date: m.unemployment?.date, trend: m.unemployment?.trend }
      ].filter(x => x.value !== undefined)
    }
  },
  created() { this.fetchData() },
  mounted() { this.chart = echarts.init(document.getElementById('macro-chart')); window.addEventListener('resize', () => this.chart?.resize()) },
  methods: {
    async fetchData() {
      this.loading = true
      try { const { data } = await request.get('/api/macro-data'); if (data.code === 200) { this.macro = data.data; this.renderChart() } }
      catch (e) { this.$message.error('获取数据失败') }
      finally { this.loading = false }
    },
    renderChart() {
      const h = this.macro.historical || []
      const option = {
        tooltip: { trigger: 'axis' }, legend: { data: ['GDP', 'CPI', 'PMI'] },
        xAxis: { type: 'category', data: h.map(i => i.date) }, yAxis: { type: 'value' },
        series: [
          { name: 'GDP', type: 'line', data: h.map(i => i.gdp), smooth: true },
          { name: 'CPI', type: 'line', data: h.map(i => i.cpi), smooth: true },
          { name: 'PMI', type: 'line', data: h.map(i => i.pmi), smooth: true }
        ]
      }
      this.chart?.setOption(option, true)
    }
  }
}
</script>
