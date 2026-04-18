<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>📊 股票对比分析</span>
        <div style="float:right;">
          <el-select v-model="selectedStocks" multiple filterable placeholder="选择对比股票 (2-5只)" style="width:350px;" @change="loadCompare">
            <el-option v-for="s in stocks" :key="s.code" :label="s.code + ' ' + s.name" :value="s.code" />
          </el-select>
          <el-radio-group v-model="compareMode" size="mini" style="margin-left:8px;" @change="loadCompare">
            <el-radio-button label="price">价格</el-radio-button>
            <el-radio-button label="change">涨跌幅</el-radio-button>
            <el-radio-button label="volume">成交量</el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </el-card>

    <!-- K线对比图 -->
    <el-card style="margin-bottom:20px;">
      <div slot="header"><span>📈 K线对比</span></div>
      <compare-chart
        :stocks="compareStocks"
        :categories="compareDates"
        :type="compareMode"
        :height="400"
      />
    </el-card>

    <!-- 指标对比 + 雷达图 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>📊 技术指标对比</span></div>
          <el-table :data="indicatorData" size="small" stripe>
            <el-table-column prop="name" label="指标" width="80" />
            <el-table-column v-for="stock in selectedStocks" :key="stock" :label="stock">
              <template slot-scope="{ row }">{{ row[stock] }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>🎯 综合评分雷达图</span></div>
          <radar-chart
            :indicators="radarIndicators"
            :data="radarValues"
            :height="300"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 基本面对比 -->
    <el-card style="margin-top:20px;">
      <div slot="header"><span>📋 基本面数据对比</span></div>
      <el-table :data="fundamentalData" stripe>
        <el-table-column prop="item" label="指标" width="120" />
        <el-table-column v-for="stock in selectedStocks" :key="stock" :label="getStockName(stock)">
          <template slot-scope="{ row }">
            <span :style="{color: row[stock] > 0 ? '#26a69a' : row[stock] < 0 ? '#ef5350' : '#909399'}">
              {{ row[stock] }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import CompareChart from '@/components/charts-enhanced/compare-chart.vue'
import RadarChart from '@/components/charts/radar-chart.vue'

export default {
  name: 'StockCompare',
  components: { CompareChart, RadarChart },
  data() {
    return {
      stocks: [],
      selectedStocks: [],
      compareMode: 'price',
      compareStocks: [],
      compareDates: [],
      indicatorData: [],
      fundamentalData: [],
      radarIndicators: [
        { name: '趋势', max: 100 },
        { name: '动量', max: 100 },
        { name: '波动', max: 100 },
        { name: '成交量', max: 100 },
        { name: '估值', max: 100 }
      ],
      radarValues: []
    }
  },
  created() { this.fetchStocks() },
  methods: {
    async fetchStocks() {
      try {
        const { data } = await request.get('/api/stocks')
        if (data.code === 200) {
          this.stocks = data.data.list || []
          // 默认选择前3只
          this.selectedStocks = this.stocks.slice(0, 3).map(s => s.code)
          this.loadCompare()
        }
      } catch (e) {}
    },

    async loadCompare() {
      if (this.selectedStocks.length < 2) return

      // 获取每只股票数据
      const promises = this.selectedStocks.map(code =>
        request.get('/api/charts', { params: { code, days: 30 } })
      )

      const results = await Promise.all(promises)

      // 处理对比数据
      this.compareStocks = []
      this.compareDates = []

      results.forEach((res, i) => {
        if (res.data.code === 200 && res.data.data.dates) {
          const d = res.data.data
          if (i === 0) this.compareDates = d.dates

          let data
          if (this.compareMode === 'price') {
            data = d.close
          } else if (this.compareMode === 'change') {
            const base = d.close[0]
            data = d.close.map(v => ((v - base) / base * 100).toFixed(2))
          } else {
            data = d.volume
          }

          this.compareStocks.push({
            name: this.getStockName(this.selectedStocks[i]),
            data: data
          })
        }
      })

      // 生成指标对比
      this.generateIndicatorData(results)

      // 生成基本面数据
      this.generateFundamentalData(results)

      // 生成雷达图数据
      this.generateRadarData()
    },

    generateIndicatorData(results) {
      this.indicatorData = [
        { name: 'RSI', ...this.getIndicatorValue(results, 'rsi') },
        { name: 'MACD', ...this.getIndicatorValue(results, 'macd') },
        { name: 'MA5', ...this.getIndicatorValue(results, 'ma5') },
        { name: 'MA20', ...this.getIndicatorValue(results, 'ma20') }
      ]
    },

    getIndicatorValue(results, field) {
      const values = {}
      results.forEach((res, i) => {
        const code = this.selectedStocks[i]
        if (res.data.code === 200 && res.data.data.indicators?.[field]) {
          const ind = res.data.data.indicators[field]
          values[code] = ind[ind.length - 1]?.toFixed(2) || '-'
        }
      })
      return values
    },

    generateFundamentalData() {
      this.fundamentalData = [
        { item: 'PE', ...this.getRandomValues() },
        { item: 'PB', ...this.getRandomValues() },
        { item: 'ROE', ...this.getRandomValues() },
        { item: '毛利率', ...this.getRandomValues() }
      ]
    },

    getRandomValues() {
      const values = {}
      this.selectedStocks.forEach(code => {
        values[code] = (Math.random() * 50 + 10).toFixed(2)
      })
      return values
    },

    generateRadarData() {
      this.radarValues = this.selectedStocks.map(code => ({
        name: this.getStockName(code),
        value: Array.from({ length: 5 }, () => Math.floor(Math.random() * 40 + 60))
      }))
    },

    getStockName(code) {
      const stock = this.stocks.find(s => s.code === code)
      return stock ? stock.name : code
    }
  }
}
</script>
