<template>
  <div class="capital-flow-enhanced">
    <el-card>
      <div slot="header">
        <span>💰 资金流向分析</span>
        <el-radio-group v-model="period" size="mini" @change="loadData">
          <el-radio-button label="today">今日</el-radio-button>
          <el-radio-button label="3d">3日</el-radio-button>
          <el-radio-button label="5d">5日</el-radio-button>
          <el-radio-button label="10d">10日</el-radio-button>
        </el-radio-group>
      </div>
      
      <!-- 资金流向总览 -->
      <el-row :gutter="20" style="margin-bottom:20px;">
        <el-col :span="6" v-for="item in flowSummary" :key="item.label">
          <el-card shadow="hover" style="text-align:center;">
            <div style="color:#909399;font-size:12px;">{{ item.label }}</div>
            <div style="font-size:20px;font-weight:600;margin:8px 0;" :style="{color: item.value >= 0 ? '#26a69a' : '#ef5350'}">
              {{ item.value >= 0 ? '+' : '' }}{{ item.value.toFixed(2) }}万
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 资金流向趋势图 -->
      <div ref="flowChart" style="width:100%;height:300px;"></div>
      
      <!-- 资金流向明细 -->
      <el-table :data="flowDetails" style="width:100%;margin-top:20px;" stripe size="small">
        <el-table-column prop="date" label="日期" width="100" />
        <el-table-column label="主力净流入" width="120">
          <template slot-scope="{ row }">
            <span :style="{color: row.mainNetInflow >= 0 ? '#26a69a' : '#ef5350'}">
              {{ row.mainNetInflow >= 0 ? '+' : '' }}{{ row.mainNetInflow.toFixed(2) }}万
            </span>
          </template>
        </el-table-column>
        <el-table-column label="超大单" width="100">
          <template slot-scope="{ row }">
            <span :style="{color: row.superLarge >= 0 ? '#26a69a' : '#ef5350'}">
              {{ row.superLarge >= 0 ? '+' : '' }}{{ row.superLarge.toFixed(2) }}万
            </span>
          </template>
        </el-table-column>
        <el-table-column label="大单" width="100">
          <template slot-scope="{ row }">
            <span :style="{color: row.large >= 0 ? '#26a69a' : '#ef5350'}">
              {{ row.large >= 0 ? '+' : '' }}{{ row.large.toFixed(2) }}万
            </span>
          </template>
        </el-table-column>
        <el-table-column label="中单" width="100">
          <template slot-scope="{ row }">
            <span :style="{color: row.medium >= 0 ? '#26a69a' : '#ef5350'}">
              {{ row.medium >= 0 ? '+' : '' }}{{ row.medium.toFixed(2) }}万
            </span>
          </template>
        </el-table-column>
        <el-table-column label="小单" width="100">
          <template slot-scope="{ row }">
            <span :style="{color: row.small >= 0 ? '#26a69a' : '#ef5350'}">
              {{ row.small >= 0 ? '+' : '' }}{{ row.small.toFixed(2) }}万
            </span>
          </template>
        </el-table-column>
        <el-table-column label="北向资金" width="100">
          <template slot-scope="{ row }">
            <span :style="{color: row.northbound >= 0 ? '#26a69a' : '#ef5350'}">
              {{ row.northbound >= 0 ? '+' : '' }}{{ row.northbound.toFixed(2) }}万
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import request from '@/utils/request'

export default {
  name: 'CapitalFlowEnhanced',
  props: {
    code: { type: String, required: true }
  },
  data() {
    return {
      period: 'today',
      flowSummary: [],
      flowDetails: [],
      chart: null
    }
  },
  created() { this.loadData() },
  mounted() {
    this.chart = echarts.init(this.$refs.flowChart)
    window.addEventListener('resize', this.resize)
  },
  beforeDestroy() {
    if (this.chart) this.chart.dispose()
    window.removeEventListener('resize', this.resize)
  },
  methods: {
    async loadData() {
      try {
        const { data } = await request.get(`/futu/capital-flow/${this.code}`, {
          params: { period: this.period }
        })
        
        if (data.code === 200) {
          this.processFlowData(data.data)
        }
      } catch (e) {
        console.error('加载资金流向失败:', e)
      }
    },
    
    processFlowData(flowData) {
      // 处理资金流向总览
      this.flowSummary = [
        { label: '主力净流入', value: flowData.main_net_inflow || 0 },
        { label: '超大单', value: flowData.super_large_net_inflow || 0 },
        { label: '大单', value: flowData.large_net_inflow || 0 },
        { label: '北向资金', value: flowData.northbound_net_inflow || 0 }
      ]
      
      // 处理资金流向明细
      this.flowDetails = (flowData.history || []).map(item => ({
        date: item.date,
        mainNetInflow: item.main_net_inflow,
        superLarge: item.super_large_net_inflow,
        large: item.large_net_inflow,
        medium: item.medium_net_inflow,
        small: item.small_net_inflow,
        northbound: item.northbound_net_inflow
      }))
      
      // 渲染图表
      this.renderFlowChart(flowData.history || [])
    },
    
    renderFlowChart(history) {
      if (!this.chart) return
      
      const dates = history.map(h => h.date)
      const mainFlow = history.map(h => h.main_net_inflow)
      const northbound = history.map(h => h.northbound_net_inflow)
      
      const option = {
        title: { text: '资金流向趋势', left: 'center', textStyle: { fontSize: 14, color: '#d1d4dc' } },
        tooltip: { trigger: 'axis' },
        legend: { data: ['主力净流入', '北向资金'], top: 30, textStyle: { color: '#d1d4dc' } },
        grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
        xAxis: { type: 'category', data: dates, axisLabel: { color: '#d1d4dc' } },
        yAxis: { type: 'value', axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
        series: [
          {
            name: '主力净流入',
            type: 'bar',
            data: mainFlow,
            itemStyle: {
              color: params => params.value >= 0 ? '#26a69a' : '#ef5350'
            }
          },
          {
            name: '北向资金',
            type: 'line',
            data: northbound,
            smooth: true,
            lineStyle: { width: 2 },
            itemStyle: { color: '#409EFF' }
          }
        ]
      }
      
      this.chart.setOption(option, true)
    },
    
    resize() {
      this.chart?.resize()
    }
  }
}
</script>

<style scoped>
.capital-flow-enhanced {
  width: 100%;
}
</style>
