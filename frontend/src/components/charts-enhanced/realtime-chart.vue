<template>
  <div class="realtime-chart" :style="{ height: height + 'px' }">
    <enhanced-chart
      ref="chart"
      :height="height"
      :loading="loading"
      :dark-theme="darkTheme"
      :show-toolbar="showToolbar"
    />
    <div class="realtime-indicator">
      <span class="pulse"></span>
      <span class="text">{{ connected ? '实时连接' : '未连接' }}</span>
    </div>
  </div>
</template>

<script>
import EnhancedChart from './enhanced-chart.vue'

export default {
  name: 'RealtimeChart',
  components: { EnhancedChart },
  props: {
    height: { type: Number, default: 300 },
    loading: { type: Boolean, default: false },
    darkTheme: { type: Boolean, default: true },
    showToolbar: { type: Boolean, default: true },
    url: { type: String, required: true },
    maxPoints: { type: Number, default: 100 }
  },
  data() {
    return {
      ws: null,
      connected: false,
      dataBuffer: [],
      categories: [],
      values: []
    }
  },
  mounted() { this.connect() },
  beforeDestroy() { this.disconnect() },
  methods: {
    connect() {
      try {
        this.ws = new WebSocket(this.url)
        
        this.ws.onopen = () => {
          this.connected = true
          console.log('实时图表已连接')
        }
        
        this.ws.onmessage = (event) => {
          const data = JSON.parse(event.data)
          this.handleNewData(data)
        }
        
        this.ws.onclose = () => {
          this.connected = false
          console.log('实时图表已断开')
          // 3秒后重连
          setTimeout(() => this.connect(), 3000)
        }
        
        this.ws.onerror = (error) => {
          console.error('实时图表错误:', error)
          this.connected = false
        }
      } catch (e) {
        console.error('WebSocket连接失败:', e)
        this.connected = false
      }
    },
    
    disconnect() {
      if (this.ws) {
        this.ws.close()
        this.ws = null
      }
    },
    
    handleNewData(data) {
      // 添加新数据
      this.categories.push(data.time || new Date().toLocaleTimeString())
      this.values.push(data.value)
      
      // 保持最大点数
      if (this.categories.length > this.maxPoints) {
        this.categories.shift()
        this.values.shift()
      }
      
      // 更新图表
      this.updateChart()
      
      // 触发事件
      this.$emit('newData', data)
    },
    
    updateChart() {
      const chart = this.$refs.chart
      if (!chart) return

      const theme = this.darkTheme ? {
        textColor: '#d1d4dc',
        splitLine: '#2a2a3e'
      } : {
        textColor: '#333333',
        splitLine: '#f0f0f0'
      }

      const option = {
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: { type: 'category', data: this.categories, axisLabel: { color: theme.textColor } },
        yAxis: { type: 'value', axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.splitLine } } },
        series: [{
          type: 'line',
          data: this.values,
          smooth: false,
          lineStyle: { width: 1.5 },
          itemStyle: { color: '#409EFF' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64,158,255,0.3)' },
              { offset: 1, color: 'rgba(64,158,255,0.05)' }
            ])
          }
        }]
      }

      chart.setOption(option, true)
    }
  }
}
</script>

<style scoped>
.realtime-chart {
  position: relative;
  width: 100%;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}

.realtime-indicator {
  position: absolute;
  top: 8px;
  left: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(42, 42, 62, 0.8);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #909399;
}

.pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #67C23A;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
