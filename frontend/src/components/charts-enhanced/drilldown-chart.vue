<template>
  <div class="drilldown-chart" :style="{ height: height + 'px' }">
    <enhanced-chart
      ref="chart"
      :height="height"
      :loading="loading"
      :dark-theme="darkTheme"
      :show-toolbar="showToolbar"
      @click="onChartClick"
    />
    
    <!-- 下钻详情对话框 -->
    <el-dialog
      title="📊 数据详情"
      :visible.sync="detailVisible"
      width="60%"
      top="5vh"
    >
      <div v-if="drillData" class="drilldown-detail">
        <h3>{{ drillData.name }}</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item v-for="(value, key) in drillData" :key="key" :label="key">
            {{ value }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 下钻子图表 -->
        <div v-if="drillChartOption" style="margin-top:20px;">
          <div ref="drillChart" style="width:100%;height:300px;"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import EnhancedChart from './enhanced-chart.vue'
import * as echarts from 'echarts'

/**
 * 数据下钻图表组件
 * 点击图表元素查看详细信息和下钻数据
 */
export default {
  name: 'DrilldownChart',
  components: { EnhancedChart },
  props: {
    height: { type: Number, default: 400 },
    loading: { type: Boolean, default: false },
    darkTheme: { type: Boolean, default: true },
    showToolbar: { type: Boolean, default: true },
    categories: { type: Array, default: () => [] },
    series: { type: Array, default: () => [] },
    title: { type: String, default: '' },
    drilldownData: { type: Object, default: () => ({}) }
  },
  data() {
    return {
      detailVisible: false,
      drillData: null,
      drillChartOption: null,
      drillChartInstance: null
    }
  },
  watch: {
    categories() { this.updateChart() },
    series: { deep: true, handler() { this.updateChart() } },
    title() { this.updateChart() }
  },
  mounted() { this.updateChart() },
  beforeDestroy() {
    if (this.drillChartInstance) {
      this.drillChartInstance.dispose()
    }
  },
  methods: {
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
        title: { text: this.title, left: 'center', textStyle: { fontSize: 14, color: theme.textColor } },
        tooltip: {
          trigger: 'item',
          backgroundColor: this.darkTheme ? 'rgba(42, 42, 62, 0.9)' : 'rgba(0, 0, 0, 0.8)',
          textStyle: { color: theme.textColor },
          formatter: (params) => {
            return `${params.name}<br/>${params.seriesName}: ${params.value}<br/><span style="color:#409EFF;">点击查看详细 >></span>`
          }
        },
        grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
        xAxis: { type: 'category', data: this.categories, axisLabel: { color: theme.textColor } },
        yAxis: { type: 'value', axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.splitLine } } },
        series: this.series.map(s => ({
          type: s.type || 'bar',
          name: s.name,
          data: s.data,
          itemStyle: { color: s.color }
        }))
      }

      chart.setOption(option, true)
    },

    /**
     * 图表点击事件 - 触发下钻
     */
    onChartClick(params) {
      if (!params.name) return

      // 获取下钻数据
      this.drillData = this.drilldownData[params.name] || {
        name: params.name,
        value: params.value,
        seriesName: params.seriesName,
        dataIndex: params.dataIndex
      }

      // 生成下钻图表配置
      this.drillChartOption = this.generateDrilldownChart(params)

      // 显示详情对话框
      this.detailVisible = true

      // 渲染下钻图表
      this.$nextTick(() => {
        this.renderDrilldownChart()
      })

      // 触发事件
      this.$emit('drilldown', {
        name: params.name,
        value: params.value,
        data: this.drillData
      })
    },

    /**
     * 生成下钻图表配置
     */
    generateDrilldownChart(params) {
      // 模拟下钻数据
      const subCategories = ['子项1', '子项2', '子项3', '子项4', '子项5']
      const subData = subCategories.map(() => Math.floor(Math.random() * 1000))

      return {
        categories: subCategories,
        series: [{
          name: `${params.name} 明细`,
          data: subData,
          type: 'bar',
          color: '#409EFF'
        }]
      }
    },

    /**
     * 渲染下钻图表
     */
    renderDrilldownChart() {
      if (!this.$refs.drillChart || !this.drillChartOption) return

      if (this.drillChartInstance) {
        this.drillChartInstance.dispose()
      }

      this.drillChartInstance = echarts.init(this.$refs.drillChart)

      const theme = this.darkTheme ? {
        textColor: '#d1d4dc',
        splitLine: '#2a2a3e'
      } : {
        textColor: '#333333',
        splitLine: '#f0f0f0'
      }

      const option = {
        title: { text: `${this.drillData?.name || ''} 明细`, left: 'center', textStyle: { fontSize: 14, color: theme.textColor } },
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: 40, containLabel: true },
        xAxis: { type: 'category', data: this.drillChartOption.categories, axisLabel: { color: theme.textColor } },
        yAxis: { type: 'value', axisLabel: { color: theme.textColor }, splitLine: { lineStyle: { color: theme.splitLine } } },
        series: this.drillChartOption.series.map(s => ({
          type: s.type || 'bar',
          name: s.name,
          data: s.data,
          itemStyle: { color: s.color }
        }))
      }

      this.drillChartInstance.setOption(option, true)
    }
  }
}
</script>

<style scoped>
.drilldown-chart {
  width: 100%;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}

.drilldown-detail h3 {
  margin: 0 0 16px;
  color: #d1d4dc;
}
</style>
