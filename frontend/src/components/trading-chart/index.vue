<template>
  <div class="trading-chart" ref="chartContainer">
    <!-- 工具栏 -->
    <div class="chart-toolbar">
      <div class="toolbar-left">
        <span class="stock-name">{{ stockName }}</span>
        <span class="stock-price" :class="priceChange >= 0 ? 'up' : 'down'">
          {{ currentPrice }} 
          <span class="price-change">{{ priceChange >= 0 ? '+' : '' }}{{ priceChange }}%</span>
        </span>
      </div>
      <div class="toolbar-right">
        <!-- 时间周期 -->
        <el-radio-group v-model="interval" size="mini" @change="onIntervalChange">
          <el-radio-button label="1d">日线</el-radio-button>
          <el-radio-button label="1w">周线</el-radio-button>
          <el-radio-button label="1m">月线</el-radio-button>
        </el-radio-group>
        
        <!-- 指标切换 -->
        <el-dropdown trigger="click" @command="handleIndicatorChange">
          <el-button size="mini">指标 <i class="el-icon-arrow-down"></i></el-button>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item command="ma">MA 均线</el-dropdown-item>
            <el-dropdown-item command="ema">EMA 指数均线</el-dropdown-item>
            <el-dropdown-item command="macd">MACD</el-dropdown-item>
            <el-dropdown-item command="rsi">RSI</el-dropdown-item>
            <el-dropdown-item command="boll">BOLL 布林带</el-dropdown-item>
            <el-dropdown-item command="vol">成交量</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
        
        <!-- 主题切换 -->
        <el-button size="mini" @click="toggleTheme">
          <i :class="theme === 'dark' ? 'el-icon-sunny' : 'el-icon-moon'"></i>
        </el-button>
        
        <!-- 截图 -->
        <el-button size="mini" @click="takeScreenshot">📷</el-button>
      </div>
    </div>

    <!-- 图表容器 -->
    <div class="chart-main" ref="chartMain"></div>

    <!-- 指标信息 -->
    <div class="chart-indicators" v-if="indicators.length > 0">
      <span v-for="ind in indicators" :key="ind.name" :style="{ color: ind.color }">
        {{ ind.name }}: {{ ind.value }}
      </span>
    </div>
  </div>
</template>

<script>
import { createChart, ColorType, CandlestickSeries, VolumeSeries, LineSeries, MACDSeries, HistogramSeries } from 'lightweight-charts'
import request from '@/utils/request'

export default {
  name: 'TradingChart',
  props: {
    code: { type: String, default: 'SH.600519' },
    days: { type: Number, default: 90 }
  },
  data() {
    return {
      chart: null,
      candlestickSeries: null,
      volumeSeries: null,
      maSeries: [],
      macdSeries: null,
      rsiSeries: null,
      bollSeries: [],
      interval: '1d',
      theme: 'dark',
      indicators: [],
      stockName: '',
      currentPrice: 0,
      priceChange: 0,
      rawData: null
    }
  },
  watch: {
    code() { this.loadChart() },
    days() { this.loadChart() }
  },
  mounted() {
    this.initChart()
    this.loadChart()
    window.addEventListener('resize', this.onResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResize)
    if (this.chart) this.chart.remove()
  },
  methods: {
    initChart() {
      const container = this.$refs.chartMain
      if (!container) return

      this.chart = createChart(container, {
        width: container.clientWidth,
        height: 500,
        layout: {
          background: { type: ColorType.Solid, color: this.theme === 'dark' ? '#1a1a2e' : '#ffffff' },
          textColor: this.theme === 'dark' ? '#d1d4dc' : '#333333'
        },
        grid: {
          vertLines: { color: this.theme === 'dark' ? '#2a2a3e' : '#f0f0f0' },
          horzLines: { color: this.theme === 'dark' ? '#2a2a3e' : '#f0f0f0' }
        },
        crosshair: {
          mode: 0,
          vertLine: {
            width: 1,
            color: this.theme === 'dark' ? '#758696' : '#758696',
            style: 2,
            labelBackgroundColor: '#758696'
          },
          horzLine: {
            width: 1,
            color: this.theme === 'dark' ? '#758696' : '#758696',
            style: 2,
            labelBackgroundColor: '#758696'
          }
        },
        timeScale: {
          borderColor: this.theme === 'dark' ? '#2a2a3e' : '#e0e0e0',
          timeVisible: false,
          rightOffset: 5
        },
        rightPriceScale: {
          borderColor: this.theme === 'dark' ? '#2a2a3e' : '#e0e0e0',
          scaleMargins: { top: 0.1, bottom: 0.2 }
        }
      })

      // K线系列
      this.candlestickSeries = this.chart.addSeries(CandlestickSeries, {
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderUpColor: '#26a69a',
        borderDownColor: '#ef5350',
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350'
      })

      // 成交量系列
      this.volumeSeries = this.chart.addSeries(VolumeSeries, {
        priceFormat: { type: 'volume' },
        priceScaleId: 'volume',
        scaleMargins: { top: 0.8, bottom: 0 }
      })
      
      this.chart.priceScale('volume').applyOptions({
        scaleMargins: { top: 0.8, bottom: 0 }
      })

      // 十字光标联动
      this.chart.subscribeCrosshairMove((param) => {
        if (param.time && param.seriesData) {
          const candle = param.seriesData.get(this.candlestickSeries)
          const vol = param.seriesData.get(this.volumeSeries)
          
          if (candle) {
            this.currentPrice = candle.close
            this.indicators = [
              { name: 'O', value: candle.open.toFixed(2), color: '#d1d4dc' },
              { name: 'H', value: candle.high.toFixed(2), color: '#d1d4dc' },
              { name: 'L', value: candle.low.toFixed(2), color: '#d1d4dc' },
              { name: 'C', value: candle.close.toFixed(2), color: '#d1d4dc' }
            ]
            if (vol) {
              this.indicators.push({ name: 'V', value: vol.value.toLocaleString(), color: '#d1d4dc' })
            }
          }
        }
      })
    },

    async loadChart() {
      try {
        const { data } = await request.get('/api/charts', { 
          params: { code: this.code, days: this.days } 
        })
        
        if (data.code === 200 && data.data.dates) {
          this.rawData = data.data
          this.processChartData(data.data)
          
          // 更新股票信息
          const prices = data.data.close
          if (prices.length >= 2) {
            this.currentPrice = prices[prices.length - 1]
            this.priceChange = ((prices[prices.length - 1] - prices[prices.length - 2]) / prices[prices.length - 2] * 100).toFixed(2)
            this.stockName = this.code
          }
        }
      } catch (e) {
        this.$message.error('加载图表数据失败')
      }
    },

    processChartData(data) {
      const { dates, open, high, low, close, volume, indicators } = data
      
      // K线数据
      const candleData = dates.map((date, i) => ({
        time: date,
        open: open[i],
        high: high[i],
        low: low[i],
        close: close[i]
      }))
      this.candlestickSeries.setData(candleData)

      // 成交量数据
      const volumeData = dates.map((date, i) => ({
        time: date,
        value: volume[i],
        color: close[i] >= open[i] ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)'
      }))
      this.volumeSeries.setData(volumeData)

      // 均线
      this.addMovingAverages(indicators, dates)
      
      // 自动缩放
      this.chart.timeScale().fitContent()
    },

    addMovingAverages(indicators, dates) {
      // 清除旧均线
      this.maSeries.forEach(s => this.chart.removeSeries(s))
      this.maSeries = []

      if (!indicators) return

      // MA5
      if (indicators.ma5) {
        const ma5Series = this.chart.addSeries(LineSeries, {
          color: '#ffeb3b',
          lineWidth: 1,
          title: 'MA5'
        })
        ma5Series.setData(dates.map((date, i) => ({ time: date, value: indicators.ma5[i] })))
        this.maSeries.push(ma5Series)
      }

      // MA10
      if (indicators.ma10) {
        const ma10Series = this.chart.addSeries(LineSeries, {
          color: '#ff9800',
          lineWidth: 1,
          title: 'MA10'
        })
        ma10Series.setData(dates.map((date, i) => ({ time: date, value: indicators.ma10[i] })))
        this.maSeries.push(ma10Series)
      }

      // MA20
      if (indicators.ma20) {
        const ma20Series = this.chart.addSeries(LineSeries, {
          color: '#2196f3',
          lineWidth: 1,
          title: 'MA20'
        })
        ma20Series.setData(dates.map((date, i) => ({ time: date, value: indicators.ma20[i] })))
        this.maSeries.push(ma20Series)
      }
    },

    handleIndicatorChange(command) {
      this.$message.info(`切换指标: ${command}`)
    },

    toggleTheme() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark'
      this.chart.applyOptions({
        layout: {
          background: { type: ColorType.Solid, color: this.theme === 'dark' ? '#1a1a2e' : '#ffffff' },
          textColor: this.theme === 'dark' ? '#d1d4dc' : '#333333'
        },
        grid: {
          vertLines: { color: this.theme === 'dark' ? '#2a2a3e' : '#f0f0f0' },
          horzLines: { color: this.theme === 'dark' ? '#2a2a3e' : '#f0f0f0' }
        }
      })
    },

    takeScreenshot() {
      // TradingView 图表截图功能
      this.$message.info('截图功能开发中')
    },

    onIntervalChange() {
      this.loadChart()
    },

    onResize() {
      if (this.chart && this.$refs.chartMain) {
        this.chart.applyOptions({
          width: this.$refs.chartMain.clientWidth
        })
      }
    }
  }
}
</script>

<style scoped>
.trading-chart {
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.chart-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #1a1a2e;
  border-bottom: 1px solid #2a2a3e;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stock-name {
  font-size: 16px;
  font-weight: 600;
  color: #d1d4dc;
}

.stock-price {
  font-size: 20px;
  font-weight: 600;
}

.stock-price.up { color: #26a69a; }
.stock-price.down { color: #ef5350; }

.price-change {
  font-size: 14px;
  margin-left: 8px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-main {
  position: relative;
  background: #1a1a2e;
}

.chart-indicators {
  display: flex;
  gap: 16px;
  padding: 8px 16px;
  background: #1a1a2e;
  border-top: 1px solid #2a2a3e;
  font-size: 12px;
  font-family: monospace;
}
</style>
