<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>📈 图表分析</span>
        <el-tag size="mini" style="float:right;">{{ currentStock }}</el-tag>
      </div>
      <el-form :inline="true">
        <el-form-item label="股票">
          <el-select v-model="form.code" size="small" style="width:160px;" @change="loadChart">
            <el-option v-for="s in stocks" :key="s.code" :label="s.code + ' ' + s.name" :value="s.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="天数">
          <el-select v-model="form.days" size="small" @change="loadChart">
            <el-option :value="30" label="30天" />
            <el-option :value="60" label="60天" />
            <el-option :value="90" label="90天" />
            <el-option :value="180" label="180天" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button size="small" type="primary" @click="loadChart" :loading="loading">📊 刷新</el-button>
        </el-form-item>
      </el-form>

      <!-- 技术指标开关 -->
      <div style="margin-top: 10px;">
        <el-checkbox-group v-model="form.indicators" @change="loadChart" size="small">
          <el-checkbox-button label="ma">MA均线</el-checkbox-button>
          <el-checkbox-button label="macd">MACD</el-checkbox-button>
          <el-checkbox-button label="rsi">RSI</el-checkbox-button>
          <el-checkbox-button label="bb">布林带</el-checkbox-button>
        </el-checkbox-group>
      </div>
    </el-card>

    <!-- K线图 -->
    <el-card v-loading="loading" style="margin-bottom: 20px;">
      <div id="kline-chart" style="width: 100%; height: 500px;"></div>
      <el-empty v-if="!chartData && !loading" description="选择股票后自动生成K线图" />
    </el-card>

    <!-- MACD/RSI/布林带 子图 -->
    <el-card v-if="form.indicators.length > 0" v-loading="loading">
      <div id="indicator-chart" style="width: 100%; height: 300px;"></div>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'

export default {
  name: 'Charts',
  data() {
    return {
      form: { code: 'SH.600519', days: 90, indicators: ['ma', 'macd', 'rsi'] },
      stocks: [],
      chartData: null,
      loading: false,
      klineChart: null,
      indicatorChart: null
    }
  },
  computed: {
    currentStock() {
      const s = this.stocks.find(x => x.code === this.form.code)
      return s ? `${s.code} ${s.name}` : this.form.code
    }
  },
  mounted() {
    this.initCharts()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.klineChart) this.klineChart.dispose()
    if (this.indicatorChart) this.indicatorChart.dispose()
  },
  created() { this.fetchStocks() },
  methods: {
    initCharts() {
      this.klineChart = echarts.init(document.getElementById('kline-chart'))
      this.indicatorChart = echarts.init(document.getElementById('indicator-chart'))
    },
    handleResize() {
      this.klineChart && this.klineChart.resize()
      this.indicatorChart && this.indicatorChart.resize()
    },
    async fetchStocks() {
      try {
        const { data } = await request.get('/api/stocks')
        if (data.code === 200) this.stocks = data.data.list || []
      } catch (e) {}
    },
    async loadChart() {
      this.loading = true
      try {
        const params = { code: this.form.code, days: this.form.days, indicators: this.form.indicators.join(',') }
        const { data } = await request.get('/api/charts', { params })
        if (data.code === 200 && data.data.dates) {
          this.chartData = data.data
          this.renderKline()
          this.renderIndicators()
        } else {
          this.$message.warning('该股票暂无数据')
        }
      } catch (e) {
        this.$message.error('获取K线数据失败')
      } finally {
        this.loading = false
      }
    },
    renderKline() {
      const d = this.chartData
      const dates = d.dates
      const klineData = d.open.map((o, i) => [o, d.close[i], d.low[i], d.high[i]])

      const series = [{
        name: 'K线',
        type: 'candlestick',
        data: klineData,
        itemStyle: {
          color: '#ef232a',        // 阳线
          color0: '#14b143',       // 阴线
          borderColor: '#ef232a',
          borderColor0: '#14b143'
        }
      }]

      // MA均线
      if (d.indicators.ma5) {
        series.push({ name: 'MA5', type: 'line', data: d.indicators.ma5, smooth: true, lineStyle: { width: 1 } })
      }
      if (d.indicators.ma10) {
        series.push({ name: 'MA10', type: 'line', data: d.indicators.ma10, smooth: true, lineStyle: { width: 1 } })
      }
      if (d.indicators.ma20) {
        series.push({ name: 'MA20', type: 'line', data: d.indicators.ma20, smooth: true, lineStyle: { width: 1 } })
      }

      // 布林带
      if (d.indicators.bb_upper) {
        series.push({ name: 'BOLL上轨', type: 'line', data: d.indicators.bb_upper, smooth: true, lineStyle: { type: 'dashed', width: 1 } })
        series.push({ name: 'BOLL中轨', type: 'line', data: d.indicators.bb_middle, smooth: true, lineStyle: { type: 'dashed', width: 1 } })
        series.push({ name: 'BOLL下轨', type: 'line', data: d.indicators.bb_lower, smooth: true, lineStyle: { type: 'dashed', width: 1 } })
      }

      const option = {
        title: { text: `${this.currentStock} K线图`, left: 'center' },
        tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
        legend: { data: series.map(s => s.name), top: 30 },
        grid: { left: '10%', right: '5%', bottom: '10%' },
        xAxis: { type: 'category', data: dates, axisLine: { lineStyle: { color: '#8392A5' } } },
        yAxis: { scale: true, splitArea: { show: true } },
        dataZoom: [
          { type: 'inside', start: 50, end: 100 },
          { type: 'slider', show: true, bottom: 10, start: 50, end: 100 }
        ],
        series: series
      }

      this.klineChart.setOption(option, true)
    },
    renderIndicators() {
      const d = this.chartData
      const dates = d.dates
      const series = []

      // MACD
      if (this.form.indicators.includes('macd') && d.indicators.macd) {
        series.push({
          name: 'MACD',
          type: 'bar',
          data: d.indicators.macd_hist.map((v, i) => ({ value: v, itemStyle: { color: v >= 0 ? '#ef232a' : '#14b143' } })),
          xAxisIndex: 0,
          yAxisIndex: 0
        })
        series.push({ name: 'DIF', type: 'line', data: d.indicators.macd, smooth: true, lineStyle: { width: 1 } })
        series.push({ name: 'DEA', type: 'line', data: d.indicators.macd_signal, smooth: true, lineStyle: { width: 1 } })
      }

      // RSI
      if (this.form.indicators.includes('rsi') && d.indicators.rsi) {
        series.push({ name: 'RSI(14)', type: 'line', data: d.indicators.rsi, smooth: true, lineStyle: { width: 2 } })
      }

      if (series.length === 0) {
        this.indicatorChart.clear()
        return
      }

      const option = {
        title: { text: '技术指标', left: 'center', top: 10 },
        tooltip: { trigger: 'axis' },
        legend: { data: series.map(s => s.name), top: 30 },
        grid: { left: '10%', right: '5%', bottom: '10%', top: 60 },
        xAxis: { type: 'category', data: dates },
        yAxis: { scale: true },
        dataZoom: [{ type: 'inside', start: 50, end: 100 }],
        series: series
      }

      this.indicatorChart.setOption(option, true)
    }
  }
}
</script>
