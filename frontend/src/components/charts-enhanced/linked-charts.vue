<template>
  <div class="linked-charts" :style="{ height: height + 'px' }">
    <div class="charts-container">
      <div v-for="(chart, index) in charts" :key="index" class="chart-wrapper" :style="{ height: chartHeight + 'px' }">
        <enhanced-chart
          :ref="'chart' + index"
          :height="chartHeight"
          :loading="chart.loading"
          :dark-theme="darkTheme"
          :show-toolbar="false"
        />
      </div>
    </div>
  </div>
</template>

<script>
import EnhancedChart from './enhanced-chart.vue'
import * as echarts from 'echarts'

/**
 * 图表联动组件
 * 支持多个图表之间的时间轴同步、高亮联动、数据联动
 */
export default {
  name: 'LinkedCharts',
  components: { EnhancedChart },
  props: {
    height: { type: Number, default: 600 },
    charts: { type: Array, default: () => [] },
    darkTheme: { type: Boolean, default: true },
    linkType: { type: String, default: 'axis' } // axis/highlight/data
  },
  data() {
    return {
      chartInstances: [],
      isSyncing: false
    }
  },
  computed: {
    chartHeight() {
      return Math.floor(this.height / this.charts.length) - 10
    }
  },
  watch: {
    charts: {
      deep: true,
      handler() { this.updateCharts() }
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initCharts()
      this.setupLinkage()
    })
  },
  beforeDestroy() {
    this.chartInstances.forEach(chart => chart?.dispose())
  },
  methods: {
    initCharts() {
      this.charts.forEach((chart, index) => {
        const ref = this.$refs['chart' + index]
        if (ref && ref[0]) {
          const instance = ref[0].getInstance()
          if (instance) {
            this.chartInstances[index] = instance
            this.updateChartOption(index, chart)
          }
        }
      })
    },

    updateCharts() {
      this.charts.forEach((chart, index) => {
        this.updateChartOption(index, chart)
      })
    },

    updateChartOption(index, chart) {
      const instance = this.chartInstances[index]
      if (!instance) return

      const theme = this.darkTheme ? {
        textColor: '#d1d4dc',
        splitLine: '#2a2a3e'
      } : {
        textColor: '#333333',
        splitLine: '#f0f0f0'
      }

      const option = {
        backgroundColor: this.darkTheme ? '#1a1a2e' : '#ffffff',
        title: { text: chart.title, left: 'center', textStyle: { fontSize: 12, color: theme.textColor } },
        tooltip: {
          trigger: 'axis',
          backgroundColor: this.darkTheme ? 'rgba(42, 42, 62, 0.9)' : 'rgba(0, 0, 0, 0.8)',
          textStyle: { color: theme.textColor }
        },
        grid: { left: '3%', right: '4%', bottom: '3%', top: 30, containLabel: true },
        xAxis: {
          type: 'category',
          data: chart.categories || [],
          axisLabel: { color: theme.textColor }
        },
        yAxis: {
          type: 'value',
          axisLabel: { color: theme.textColor },
          splitLine: { lineStyle: { color: theme.splitLine } }
        },
        series: chart.series?.map((s, i) => ({
          type: s.type || 'line',
          name: s.name,
          data: s.data,
          smooth: s.smooth !== false,
          lineStyle: { width: s.lineWidth || 2 },
          itemStyle: { color: s.color }
        })) || []
      }

      instance.setOption(option, true)
    },

    /**
     * 设置图表联动
     */
    setupLinkage() {
      if (this.chartInstances.length < 2) return

      this.chartInstances.forEach((chart, index) => {
        if (!chart) return

        // 时间轴联动
        chart.on('updateAxisPointer', (params) => {
          if (this.isSyncing) return
          this.isSyncing = true

          const dataIndex = params.dataIndex
          if (dataIndex !== undefined) {
            this.chartInstances.forEach((otherChart, otherIndex) => {
              if (otherIndex !== index && otherChart) {
                otherChart.dispatchAction({
                  type: 'showTip',
                  seriesIndex: 0,
                  dataIndex: dataIndex
                })
              }
            })
          }

          this.$nextTick(() => {
            this.isSyncing = false
          })
        })

        // 高亮联动
        chart.on('highlight', (params) => {
          if (this.isSyncing) return
          this.isSyncing = true

          this.chartInstances.forEach((otherChart, otherIndex) => {
            if (otherIndex !== index && otherChart) {
              otherChart.dispatchAction({
                type: 'highlight',
                seriesIndex: params.seriesIndex,
                dataIndex: params.dataIndex
              })
            }
          })

          this.$nextTick(() => {
            this.isSyncing = false
          })
        })
      })
    },

    /**
     * 导出所有图表
     */
    exportAllCharts(type = 'png') {
      this.chartInstances.forEach((chart, index) => {
        if (chart) {
          const url = chart.getDataURL({
            type,
            pixelRatio: 2,
            backgroundColor: this.darkTheme ? '#1a1a2e' : '#ffffff'
          })
          const link = document.createElement('a')
          link.download = `chart_${index}_${Date.now()}.${type}`
          link.href = url
          link.click()
        }
      })
    }
  }
}
</script>

<style scoped>
.linked-charts {
  width: 100%;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
  padding: 8px;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
}

.chart-wrapper {
  width: 100%;
  background: #1a1a2e;
  border-radius: 4px;
  overflow: hidden;
}
</style>
