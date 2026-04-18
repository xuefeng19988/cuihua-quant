<template>
  <div class="chart-wrapper" :style="{ height: height + 'px' }">
    <!-- 加载状态 -->
    <div v-if="loading" class="chart-loading">
      <i class="el-icon-loading"></i>
      <p>{{ loadingText }}</p>
    </div>
    
    <!-- 空状态 -->
    <div v-else-if="empty" class="chart-empty">
      <i class="el-icon-data-line"></i>
      <p>{{ emptyText }}</p>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="error" class="chart-error">
      <i class="el-icon-warning"></i>
      <p>{{ errorText }}</p>
      <el-button size="mini" type="primary" @click="$emit('retry')">🔄 重试</el-button>
    </div>
    
    <!-- 图表容器 -->
    <div v-show="!loading && !empty && !error" ref="chartRef" class="chart-content" :style="{ height: '100%' }"></div>
    
    <!-- 工具栏 -->
    <div v-if="showToolbar && !loading && !empty && !error" class="chart-toolbar">
      <el-button size="mini" icon="el-icon-download" @click="exportChart('png')" title="导出PNG">PNG</el-button>
      <el-button size="mini" icon="el-icon-download" @click="exportChart('svg')" title="导出SVG">SVG</el-button>
      <el-button size="mini" icon="el-icon-refresh" @click="$emit('refresh')" title="刷新">🔄</el-button>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { getThemeConfig, applyTheme } from './theme'

export default {
  name: 'EnhancedChart',
  props: {
    height: { type: Number, default: 300 },
    loading: { type: Boolean, default: false },
    empty: { type: Boolean, default: false },
    error: { type: Boolean, default: false },
    loadingText: { type: String, default: '加载中...' },
    emptyText: { type: String, default: '暂无数据' },
    errorText: { type: String, default: '加载失败' },
    showToolbar: { type: Boolean, default: true },
    darkTheme: { type: Boolean, default: true }
  },
  data() { return { chart: null } },
  watch: {
    darkTheme() { this.updateTheme() }
  },
  mounted() { this.initChart() },
  beforeDestroy() { this.dispose() },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chartRef, null, { renderer: 'canvas' })
      this.updateTheme()
      this.chart.on('click', params => this.$emit('click', params))
      window.addEventListener('resize', this.resize)
    },
    
    updateTheme() {
      if (this.chart) {
        applyTheme(this.chart, this.darkTheme)
      }
    },
    
    resize() {
      if (this.chart) {
        this.chart.resize()
      }
    },
    
    setOption(option, notMerge = true) {
      if (this.chart) {
        this.chart.setOption(option, notMerge)
      }
    },
    
    clear() {
      if (this.chart) {
        this.chart.clear()
      }
    },
    
    dispose() {
      if (this.chart) {
        this.chart.dispose()
        this.chart = null
      }
      window.removeEventListener('resize', this.resize)
    },
    
    /**
     * 导出图表为图片
     */
    exportChart(type = 'png') {
      if (!this.chart) return
      
      const url = this.chart.getDataURL({
        type: type,
        pixelRatio: 2,
        backgroundColor: this.darkTheme ? '#1a1a2e' : '#ffffff'
      })
      
      const link = document.createElement('a')
      link.download = `chart_${new Date().getTime()}.${type}`
      link.href = url
      link.click()
      
      this.$message.success(`图表已导出为${type.toUpperCase()}`)
    },
    
    /**
     * 获取图表实例
     */
    getInstance() {
      return this.chart
    }
  }
}
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  width: 100%;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}

.chart-content {
  width: 100%;
  height: 100%;
}

.chart-loading,
.chart-empty,
.chart-error {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
  background: rgba(26, 26, 46, 0.9);
}

.chart-loading i,
.chart-empty i,
.chart-error i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #409EFF;
}

.chart-error i {
  color: #F56C6C;
}

.chart-toolbar {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
  display: flex;
  gap: 4px;
  background: rgba(42, 42, 62, 0.8);
  padding: 4px;
  border-radius: 4px;
}

.chart-toolbar .el-button {
  background: transparent;
  border: none;
  color: #d1d4dc;
  padding: 4px 8px;
}

.chart-toolbar .el-button:hover {
  background: rgba(64, 158, 255, 0.2);
  color: #409EFF;
}
</style>
