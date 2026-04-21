<template>
  <div class="indicators-advanced">
    <el-card>
      <div slot="header">
        <span>📊 高级技术指标</span>
        <div style="float:right;">
          <el-select v-model="selectedIndicator" size="mini" style="width:150px;" @change="updateIndicator">
            <el-option label="KDJ" value="kdj" />
            <el-option label="WR" value="wr" />
            <el-option label="CCI" value="cci" />
            <el-option label="DMI" value="dmi" />
            <el-option label="OBV" value="obv" />
          </el-select>
        </div>
      </div>
      
      <!-- 指标图表 -->
      <div ref="indicatorChart" style="width:100%;height:300px;"></div>
      
      <!-- 指标信号 -->
      <el-row :gutter="20" style="margin-top:20px;">
        <el-col :span="8" v-for="signal in signals" :key="signal.name">
          <el-card shadow="hover" style="text-align:center;">
            <div style="color:#909399;font-size:12px;">{{ signal.name }}</div>
            <div style="font-size:24px;font-weight:600;margin:8px 0;" :style="{color: signal.color}">
              {{ signal.value }}
            </div>
            <el-tag size="mini" :type="signal.type">{{ signal.signal }}</el-tag>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 指标说明 -->
      <el-card style="margin-top:20px;">
        <div slot="header"><span>📖 指标说明</span></div>
        <div style="color:#909399;font-size:13px;line-height:1.6;">
          <p><strong>{{ indicatorInfo.name }}</strong></p>
          <p>{{ indicatorInfo.description }}</p>
          <p><strong>使用方法：</strong>{{ indicatorInfo.usage }}</p>
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import request from '@/utils/request'

export default {
  name: 'IndicatorsAdvanced',
  props: {
    code: { type: String, required: true }
  },
  data() {
    return {
      selectedIndicator: 'kdj',
      signals: [],
      indicatorInfo: {},
      chart: null,
      indicatorData: {}
    }
  },
  created() { this.loadIndicator() },
  mounted() {
    this.chart = echarts.init(this.$refs.indicatorChart)
    window.addEventListener('resize', this.resize)
  },
  beforeDestroy() {
    if (this.chart) this.chart.dispose()
    window.removeEventListener('resize', this.resize)
  },
  watch: {
    code() { this.loadIndicator() }
  },
  methods: {
    async loadIndicator() {
      try {
        const { data } = await request.get(`/futu/technical/${this.code}`)
        if (data.code === 200) {
          this.indicatorData = data.data
          this.updateIndicator()
        }
      } catch (e) {
        console.error('加载技术指标失败:', e)
      }
    },
    
    updateIndicator() {
      this.generateIndicatorData()
      this.renderChart()
      this.updateIndicatorInfo()
    },
    
    generateIndicatorData() {
      const indicator = this.selectedIndicator
      
      // 模拟高级指标数据 (实际应从后端获取)
      const data = {
        kdj: {
          k: Array.from({ length: 30 }, () => Math.random() * 100),
          d: Array.from({ length: 30 }, () => Math.random() * 100),
          j: Array.from({ length: 30 }, () => Math.random() * 100)
        },
        wr: {
          wr1: Array.from({ length: 30 }, () => Math.random() * -100),
          wr2: Array.from({ length: 30 }, () => Math.random() * -100)
        },
        cci: {
          cci: Array.from({ length: 30 }, () => Math.random() * 400 - 200)
        },
        dmi: {
          pdi: Array.from({ length: 30 }, () => Math.random() * 50),
          mdi: Array.from({ length: 30 }, () => Math.random() * 50),
          adx: Array.from({ length: 30 }, () => Math.random() * 60)
        },
        obv: {
          obv: Array.from({ length: 30 }, (_, i) => i * 100 + Math.random() * 1000)
        }
      }
      
      this.currentIndicatorData = data[indicator] || data.kdj
    },
    
    renderChart() {
      if (!this.chart || !this.currentIndicatorData) return
      
      const dates = Array.from({ length: 30 }, (_, i) => {
        const d = new Date()
        d.setDate(d.getDate() - 29 + i)
        return `${d.getMonth()+1}/${d.getDate()}`
      })
      
      const series = Object.entries(this.currentIndicatorData).map(([name, data], i) => ({
        name: name.toUpperCase(),
        type: 'line',
        data,
        smooth: true,
        lineStyle: { width: 2 },
        itemStyle: { color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C'][i % 4] }
      }))
      
      const option = {
        title: { text: this.selectedIndicator.toUpperCase() + ' 指标', left: 'center', textStyle: { fontSize: 14, color: '#d1d4dc' } },
        tooltip: { trigger: 'axis' },
        legend: { data: series.map(s => s.name), top: 30, textStyle: { color: '#d1d4dc' } },
        grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
        xAxis: { type: 'category', data: dates, axisLabel: { color: '#d1d4dc' } },
        yAxis: { type: 'value', axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
        series
      }
      
      this.chart.setOption(option, true)
      
      // 生成信号
      this.generateSignals()
    },
    
    generateSignals() {
      const indicator = this.selectedIndicator
      const data = this.currentIndicatorData
      
      const signals = []
      
      if (indicator === 'kdj') {
        const k = data.k[data.k.length - 1]
        const d = data.d[data.d.length - 1]
        const j = data.j[data.j.length - 1]
        
        signals.push(
          { name: 'K值', value: k.toFixed(2), signal: k > 80 ? '超买' : k < 20 ? '超卖' : '中性', type: k > 80 ? 'danger' : k < 20 ? 'success' : 'info', color: '#d1d4dc' },
          { name: 'D值', value: d.toFixed(2), signal: d > 80 ? '超买' : d < 20 ? '超卖' : '中性', type: d > 80 ? 'danger' : d < 20 ? 'success' : 'info', color: '#d1d4dc' },
          { name: 'J值', value: j.toFixed(2), signal: j > 100 ? '超买' : j < 0 ? '超卖' : '中性', type: j > 100 ? 'danger' : j < 0 ? 'success' : 'info', color: '#d1d4dc' }
        )
      } else if (indicator === 'wr') {
        const wr1 = data.wr1[data.wr1.length - 1]
        signals.push(
          { name: 'WR1', value: wr1.toFixed(2), signal: wr1 > -20 ? '超买' : wr1 < -80 ? '超卖' : '中性', type: wr1 > -20 ? 'danger' : wr1 < -80 ? 'success' : 'info', color: '#d1d4dc' }
        )
      } else if (indicator === 'cci') {
        const cci = data.cci[data.cci.length - 1]
        signals.push(
          { name: 'CCI', value: cci.toFixed(2), signal: cci > 100 ? '超买' : cci < -100 ? '超卖' : '中性', type: cci > 100 ? 'danger' : cci < -100 ? 'success' : 'info', color: '#d1d4dc' }
        )
      }
      
      this.signals = signals
    },
    
    updateIndicatorInfo() {
      const info = {
        kdj: {
          name: 'KDJ 随机指标',
          description: 'KDJ指标是一种相当新颖和实用的技术分析指标，它起先用于期货市场的分析，后被广泛用于股市的中短期趋势分析。',
          usage: 'K值>80为超买，<20为超卖；J值>100为超买，<0为超卖；K线上穿D线为金叉买入信号。'
        },
        wr: {
          name: 'WR 威廉指标',
          description: '威廉指标是利用摆动点来衡量市场的超买超卖现象，从而预测短期内价格走势。',
          usage: 'WR>80为超卖，<20为超买；WR从超卖区向上突破时为买入信号。'
        },
        cci: {
          name: 'CCI 顺势指标',
          description: 'CCI指标用于测量股价是否已超出常态分布范围，是专门用来测量股价是否超出常态分布范围。',
          usage: 'CCI>+100为超买，<-100为超卖；CCI从下向上突破-100线为买入信号。'
        },
        dmi: {
          name: 'DMI 趋向指标',
          description: 'DMI指标是通过分析价格在涨跌过程中买卖双方力量的均衡点的变化情况，提供对趋势判断依据。',
          usage: 'PDI上升突破MDI为买入信号；ADX>20时趋势成立；ADX转折表示趋势可能反转。'
        },
        obv: {
          name: 'OBV 能量潮指标',
          description: 'OBV指标通过统计成交量变动趋势和股价变动趋势，分析买卖双方力量对比。',
          usage: 'OBV上升表示买方力量强，下降表示卖方力量强；OBV与股价背离时可能反转。'
        }
      }
      
      this.indicatorInfo = info[this.selectedIndicator] || info.kdj
    },
    
    resize() {
      this.chart?.resize()
    }
  }
}
</script>

<style scoped>
.indicators-advanced {
  width: 100%;
}
</style>
