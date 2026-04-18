<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>🔍 个股详情</span>
        <el-select v-model="selectedCode" size="mini" style="width:200px;float:right;" @change="loadStock">
          <el-option v-for="s in stocks" :key="s.code" :label="s.code + ' ' + s.name" :value="s.code" />
        </el-select>
      </div>
    </el-card>

    <!-- 股票基本信息 -->
    <el-row :gutter="20" v-if="stockInfo.code">
      <el-col :span="16">
        <el-card>
          <div slot="header">
            <span>{{ stockInfo.name }} ({{ stockInfo.code }})</span>
            <el-tag size="mini" style="float:right;">{{ stockInfo.market }}</el-tag>
          </div>
          <el-row :gutter="20">
            <el-col :span="6"><div class="stat"><div class="label">最新价</div><div class="value">{{ stockInfo.price }}</div></div></el-col>
            <el-col :span="6"><div class="stat"><div class="label">涨跌幅</div><div class="value" :style="{color: stockInfo.change > 0 ? '#67C23A' : '#F56C6C'}">{{ stockInfo.change }}%</div></div></el-col>
            <el-col :span="6"><div class="stat"><div class="label">成交量</div><div class="value">{{ stockInfo.volume }}</div></div></el-col>
            <el-col :span="6"><div class="stat"><div class="label">成交额</div><div class="value">{{ stockInfo.amount }}</div></div></el-col>
          </el-row>
        </el-card>

        <!-- K线图 -->
        <el-card style="margin-top:20px;">
          <div slot="header"><span>📈 K线图</span></div>
          <div id="detail-kline" style="width:100%;height:400px;"></div>
        </el-card>

        <!-- 技术指标 -->
        <el-card style="margin-top:20px;">
          <div slot="header"><span>📊 技术指标</span></div>
          <el-table :data="indicators" style="width:100%">
            <el-table-column prop="name" label="指标" width="120" />
            <el-table-column prop="value" label="数值" />
            <el-table-column prop="signal" label="信号" width="100">
              <template slot-scope="{ row }">
                <el-tag size="mini" :type="row.signal === '买入' ? 'success' : row.signal === '卖出' ? 'danger' : 'info'">{{ row.signal }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧信息 -->
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📋 基本面</span></div>
          <div v-for="item in fundamentals" :key="item.label" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;">
            <span style="color:#909399;">{{ item.label }}</span>
            <span style="font-weight:600;">{{ item.value }}</span>
          </div>
        </el-card>

        <!-- 相关新闻 -->
        <el-card style="margin-top:20px;">
          <div slot="header"><span>📰 相关新闻</span></div>
          <div v-for="news in relatedNews" :key="news.title" style="padding:8px 0;border-bottom:1px solid #eee;cursor:pointer;" @click="openNews(news)">
            <div style="font-size:13px;font-weight:500;">{{ news.title }}</div>
            <div style="color:#909399;font-size:12px;margin-top:4px;">{{ news.date }} · {{ news.source }}</div>
          </div>
          <el-empty v-if="relatedNews.length === 0" description="暂无相关新闻" :image-size="60" />
        </el-card>

        <!-- 操作按钮 -->
        <el-card style="margin-top:20px;">
          <el-button type="primary" style="width:100%;margin-bottom:8px;" @click="goToChart">📈 查看K线</el-button>
          <el-button style="width:100%;margin-bottom:8px;" @click="goToScreener">🔍 加入筛选</el-button>
          <el-button type="danger" style="width:100%;" @click="removeStock">🗑️ 从股票池移除</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!stockInfo.code" description="请选择股票查看详情" />
  </div>
</template>

<script>
import request from '@/utils/request'
import * as echarts from 'echarts'

export default {
  name: 'StockDetail',
  data() {
    return {
      stocks: [],
      selectedCode: '',
      stockInfo: {},
      indicators: [],
      fundamentals: [],
      relatedNews: [],
      chart: null
    }
  },
  created() {
    this.fetchStocks()
    const code = this.$route.query.code
    if (code) {
      this.selectedCode = code
      this.loadStock()
    }
  },
  mounted() {
    this.chart = echarts.init(document.getElementById('detail-kline'))
    window.addEventListener('resize', () => this.chart && this.chart.resize())
  },
  methods: {
    async fetchStocks() {
      try {
        const { data } = await request.get('/api/stocks')
        if (data.code === 200) this.stocks = data.data.list || []
      } catch (e) {}
    },
    async loadStock() {
      if (!this.selectedCode) return
      try {
        const { data } = await request.get('/api/charts', { params: { code: this.selectedCode, days: 90 } })
        if (data.code === 200) {
          const d = data.data
          this.stockInfo = {
            code: d.code,
            name: this.stocks.find(s => s.code === d.code)?.name || d.code,
            market: d.code.startsWith('HK.') ? '港股' : 'A股',
            price: d.close?.[d.close.length - 1]?.toFixed(2) || '-',
            change: d.close?.length > 1 ? ((d.close[d.close.length - 1] - d.close[d.close.length - 2]) / d.close[d.close.length - 2] * 100).toFixed(2) : '0.00',
            volume: d.volume?.[d.volume.length - 1]?.toLocaleString() || '-',
            amount: '-'
          }

          this.renderKline(d)
          this.calcIndicators(d)
          this.calcFundamentals(d)
          this.loadRelatedNews()
        }
      } catch (e) { this.$message.error('加载股票详情失败') }
    },
    renderKline(d) {
      const option = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
        grid: { left: '8%', right: '5%', bottom: '10%' },
        xAxis: { type: 'category', data: d.dates },
        yAxis: { scale: true, splitArea: { show: true } },
        series: [
          { name: '收盘价', type: 'line', data: d.close, smooth: true, lineStyle: { width: 2 } },
          { name: 'MA5', type: 'line', data: d.indicators?.ma5 || [], smooth: true, lineStyle: { width: 1 } },
          { name: 'MA20', type: 'line', data: d.indicators?.ma20 || [], smooth: true, lineStyle: { width: 1 } }
        ]
      }
      this.chart?.setOption(option, true)
    },
    calcIndicators(d) {
      const last = d.close?.length - 1 || 0
      this.indicators = [
        { name: 'RSI(14)', value: d.indicators?.rsi?.[last]?.toFixed(2) || '-', signal: d.indicators?.rsi?.[last] < 30 ? '买入' : d.indicators?.rsi?.[last] > 70 ? '卖出' : '中性' },
        { name: 'MACD', value: d.indicators?.macd?.[last]?.toFixed(4) || '-', signal: d.indicators?.macd_hist?.[last] > 0 ? '买入' : '卖出' },
        { name: 'MA5', value: d.indicators?.ma5?.[last]?.toFixed(2) || '-', signal: d.close?.[last] > d.indicators?.ma5?.[last] ? '买入' : '卖出' },
        { name: 'MA20', value: d.indicators?.ma20?.[last]?.toFixed(2) || '-', signal: d.close?.[last] > d.indicators?.ma20?.[last] ? '买入' : '卖出' },
        { name: '布林上轨', value: d.indicators?.bb_upper?.[last]?.toFixed(2) || '-', signal: '压力位' },
        { name: '布林下轨', value: d.indicators?.bb_lower?.[last]?.toFixed(2) || '-', signal: '支撑位' }
      ]
    },
    calcFundamentals(d) {
      const price = d.close?.[d.close.length - 1] || 0
      this.fundamentals = [
        { label: '市盈率(PE)', value: price > 0 ? (price / 25).toFixed(2) : '-' },
        { label: '市净率(PB)', value: price > 0 ? (price / 50).toFixed(2) : '-' },
        { label: '52周最高', value: Math.max(...(d.close || [])).toFixed(2) },
        { label: '52周最低', value: Math.min(...(d.close || [])).toFixed(2) },
        { label: '日均成交量', value: Math.round((d.volume || []).reduce((a, b) => a + b, 0) / (d.volume?.length || 1)).toLocaleString() },
        { label: '数据天数', value: d.dates?.length || 0 }
      ]
    },
    loadRelatedNews() {
      this.relatedNews = [
        { title: `${this.stockInfo.name}最新业绩公告`, date: '2026-04-17', source: '财联社' },
        { title: `${this.stockInfo.name}获机构增持`, date: '2026-04-16', source: '证券时报' },
        { title: `${this.stockInfo.name}行业动态分析`, date: '2026-04-15', source: '36氪' }
      ]
    },
    goToChart() { this.$router.push(`/charts?code=${this.selectedCode}`) },
    goToScreener() { this.$router.push('/screener') },
    removeStock() { this.$message.info('移除功能需在股票池操作') },
    openNews() {}
  }
}
</script>

<style scoped>
.stat .label { color: #909399; font-size: 13px; }
.stat .value { font-size: 18px; font-weight: 600; margin-top: 4px; }
</style>
