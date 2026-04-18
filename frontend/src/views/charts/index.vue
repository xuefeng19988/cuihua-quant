<template>
  <div class="app-container">
    <!-- 股票选择栏 -->
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>📈 TradingView 专业图表</span>
        <div style="float:right;display:flex;gap:8px;align-items:center;">
          <el-select v-model="selectedCode" size="small" style="width:200px;" @change="onStockChange">
            <el-option v-for="s in stocks" :key="s.code" :label="s.code + ' ' + s.name" :value="s.code" />
          </el-select>
          <el-select v-model="selectedDays" size="small" style="width:100px;" @change="onDaysChange">
            <el-option :value="30" label="1个月" />
            <el-option :value="90" label="3个月" />
            <el-option :value="180" label="6个月" />
            <el-option :value="365" label="1年" />
          </el-select>
        </div>
      </div>
    </el-card>

    <!-- TradingView 图表 -->
    <trading-chart 
      ref="tradingChart"
      :code="selectedCode" 
      :days="selectedDays" 
    />

    <!-- 技术指标详情 -->
    <el-row :gutter="20" style="margin-top:20px;">
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📊 MA 均线</span></div>
          <div v-if="chartData && chartData.indicators">
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;">
              <span style="color:#ffeb3b;">MA5</span>
              <span style="font-weight:600;">{{ chartData.indicators.ma5 ? chartData.indicators.ma5.slice(-1)[0].toFixed(2) : '-' }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;">
              <span style="color:#ff9800;">MA10</span>
              <span style="font-weight:600;">{{ chartData.indicators.ma10 ? chartData.indicators.ma10.slice(-1)[0].toFixed(2) : '-' }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;">
              <span style="color:#2196f3;">MA20</span>
              <span style="font-weight:600;">{{ chartData.indicators.ma20 ? chartData.indicators.ma20.slice(-1)[0].toFixed(2) : '-' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📈 MACD</span></div>
          <div v-if="chartData && chartData.indicators">
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;">
              <span>DIF</span>
              <span style="font-weight:600;">{{ chartData.indicators.macd ? chartData.indicators.macd.slice(-1)[0].toFixed(4) : '-' }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;">
              <span>DEA</span>
              <span style="font-weight:600;">{{ chartData.indicators.macd_signal ? chartData.indicators.macd_signal.slice(-1)[0].toFixed(4) : '-' }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;">
              <span>MACD柱</span>
              <span :style="{color: (chartData.indicators.macd_hist ? chartData.indicators.macd_hist.slice(-1)[0] : 0) >= 0 ? '#26a69a' : '#ef5350', fontWeight:600}">
                {{ chartData.indicators.macd_hist ? chartData.indicators.macd_hist.slice(-1)[0].toFixed(4) : '-' }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📉 RSI</span></div>
          <div v-if="chartData && chartData.indicators">
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;">
              <span>RSI(14)</span>
              <span :style="{color: getRSIColor(chartData.indicators.rsi), fontWeight:600}">
                {{ chartData.indicators.rsi ? chartData.indicators.rsi.slice(-1)[0].toFixed(2) : '-' }}
              </span>
            </div>
            <div style="margin-top:8px;">
              <el-progress :percentage="chartData.indicators.rsi ? Math.min(100, chartData.indicators.rsi.slice(-1)[0]) : 0" 
                :color="getRSIColor(chartData.indicators.rsi)" 
                :stroke-width="12" 
                :format="() => ''" />
              <div style="display:flex;justify-content:space-between;font-size:12px;color:#909399;margin-top:4px;">
                <span>超卖 (30)</span>
                <span>超买 (70)</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'
import TradingChart from '@/components/trading-chart/index.vue'

export default {
  name: 'Charts',
  components: { TradingChart },
  data() {
    return {
      selectedCode: 'SH.600519',
      selectedDays: 90,
      stocks: [],
      chartData: null,
      loading: false
    }
  },
  created() {
    this.fetchStocks()
    this.fetchChartData()
  },
  methods: {
    async fetchStocks() {
      try {
        const { data } = await request.get('/api/stocks')
        if (data.code === 200) this.stocks = data.data.list || []
      } catch (e) {}
    },
    async fetchChartData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/charts', { 
          params: { code: this.selectedCode, days: this.selectedDays } 
        })
        if (data.code === 200) this.chartData = data.data
      } catch (e) {
        this.$message.error('获取图表数据失败')
      } finally {
        this.loading = false
      }
    },
    onStockChange() {
      this.fetchChartData()
    },
    onDaysChange() {
      this.fetchChartData()
    },
    getRSIColor(rsiArray) {
      if (!rsiArray || !rsiArray.length) return '#909399'
      const rsi = rsiArray[rsiArray.length - 1]
      if (rsi > 70) return '#ef5350'  // 超买 - 红
      if (rsi < 30) return '#26a69a'  // 超卖 - 绿
      return '#409EFF'  // 正常 - 蓝
    }
  }
}
</script>

<style scoped>
.app-container {
  background: #0f0f1a;
  min-height: 100vh;
  padding: 20px;
}

.el-card {
  background: #1a1a2e !important;
  border: 1px solid #2a2a3e !important;
}

.el-card__header {
  border-bottom: 1px solid #2a2a3e !important;
}
</style>
