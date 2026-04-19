<template>
  <div class="app-container">
    <!-- 顶部选择区 -->
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>📊 股票对比评分分析</span>
      </div>
      
      <el-row :gutter="16">
        <el-col :span="14">
          <el-select v-model="selectedStocks" multiple filterable 
            placeholder="选择对比股票 (2-10只)" 
            style="width:100%;" 
            @change="loadCompare">
            <el-option v-for="s in stocks" :key="s.code" 
              :label="s.code + ' ' + s.name" :value="s.code" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-radio-group v-model="compareMode" size="mini" @change="loadCompare">
            <el-radio-button label="price">价格</el-radio-button>
            <el-radio-button label="change">涨跌幅</el-radio-button>
            <el-radio-button label="volume">成交量</el-radio-button>
          </el-radio-group>
        </el-col>
        <el-col :span="5">
          <el-button type="primary" size="mini" @click="loadCompare" :loading="loading">
            🔍 开始对比
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 对比结果头部 -->
    <el-card v-if="compareData" style="margin-bottom:20px;" class="dark-card">
      <div slot="header"><span>🏆 综合评分排名</span></div>
      
      <el-table :data="rankings" stripe size="small" :row-class-name="tableRowClassName">
        <el-table-column label="排名" width="60" align="center">
          <template slot-scope="{ row }">
            <span class="rank-badge" :class="'rank-' + row.rank">{{ row.rank }}</span>
          </template>
        </el-table-column>
        <el-table-column label="股票" min-width="150">
          <template slot-scope="{ row }">
            <span class="stock-name">{{ row.name }}</span>
            <span class="stock-code">{{ row.code }}</span>
          </template>
        </el-table-column>
        <el-table-column label="总分" width="80" align="center">
          <template slot-scope="{ row }">
            <span class="score-value" :class="scoreColorClass(row.score_result.total)">
              {{ row.score_result.total }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="评级" width="70" align="center">
          <template slot-scope="{ row }">
            <el-tag size="mini" :type="gradeType(row.score_result.grade)" effect="dark">
              {{ row.score_result.grade }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="建议" width="80" align="center">
          <template slot-scope="{ row }">
            <span class="rec-text">{{ row.score_result.recommendation }}</span>
          </template>
        </el-table-column>
        <el-table-column label="趋势" width="70" align="center">
          <template slot-scope="{ row }">
            <span :class="row.score_result.scores.trend >= 60 ? 'text-up' : 'text-down'">
              {{ row.score_result.scores.trend }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="动量" width="70" align="center">
          <template slot-scope="{ row }">
            <span :class="row.score_result.scores.momentum >= 60 ? 'text-up' : 'text-down'">
              {{ row.score_result.scores.momentum }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="估值" width="70" align="center">
          <template slot-scope="{ row }">
            <span :class="row.score_result.scores.valuation >= 60 ? 'text-up' : 'text-down'">
              {{ row.score_result.scores.valuation }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="质量" width="70" align="center">
          <template slot-scope="{ row }">
            <span :class="row.score_result.scores.quality >= 60 ? 'text-up' : 'text-down'">
              {{ row.score_result.scores.quality }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="成长" width="70" align="center">
          <template slot-scope="{ row }">
            <span :class="row.score_result.scores.growth >= 60 ? 'text-up' : 'text-down'">
              {{ row.score_result.scores.growth }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="价格" width="90" align="right">
          <template slot-scope="{ row }">{{ row.price.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="涨跌" width="80" align="center">
          <template slot-scope="{ row }">
            <span :class="row.change >= 0 ? 'text-up' : 'text-down'">
              {{ row.change >= 0 ? '+' : '' }}{{ row.change }}%
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 雷达图 + K线对比 -->
    <el-row v-if="compareData" :gutter="20">
      <el-col :span="12">
        <el-card class="dark-card">
          <div slot="header"><span>🎯 多维评分雷达图</span></div>
          <div id="radar-compare-chart" style="width:100%;height:350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="dark-card">
          <div slot="header"><span>📈 价格对比走势</span></div>
          <compare-chart
            :stocks="compareStocks"
            :categories="compareDates"
            :type="compareMode"
            :height="350"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 维度冠军 + 评分详情柱状图 -->
    <el-row v-if="compareData" :gutter="20" style="margin-top:20px;">
      <el-col :span="12">
        <el-card class="dark-card">
          <div slot="header"><span>🏅 各维度冠军</span></div>
          <div class="dim-champions">
            <div v-for="(stat, dim) in compareData.dim_stats" :key="dim" class="dim-champ-row">
              <span class="dim-label">{{ stat.label }}</span>
              <span class="champ-best">
                👑 {{ getStockName(stat.best.code) }} 
                <span class="champ-score">{{ stat.best.score }}</span>
              </span>
              <span class="champ-worst">
                {{ getStockName(stat.worst.code) }} 
                <span class="champ-score-low">{{ stat.worst.score }}</span>
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="dark-card">
          <div slot="header"><span>📊 评分对比柱状图</span></div>
          <div id="bar-compare-chart" style="width:100%;height:350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 统计摘要 -->
    <el-card v-if="compareData && compareData.summary" style="margin-top:20px;" class="dark-card">
      <div slot="header"><span>📋 对比摘要</span></div>
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="stat-box">
            <div class="stat-num">{{ compareData.summary.total_stocks }}</div>
            <div class="stat-label">对比股票数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-box">
            <div class="stat-num text-up">{{ compareData.summary.avg_score }}</div>
            <div class="stat-label">平均评分</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-box">
            <div class="stat-num text-up">{{ compareData.summary.max_score }}</div>
            <div class="stat-label">最高评分</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-box">
            <div class="stat-num text-down">{{ compareData.summary.min_score }}</div>
            <div class="stat-label">最低评分</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import CompareChart from '@/components/charts-enhanced/compare-chart.vue'
import * as echarts from 'echarts'

const DIM_COLORS = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#9b59b6', '#1abc9c', '#e74c3c']

export default {
  name: 'StockCompare',
  components: { CompareChart },
  data() {
    return {
      stocks: [],
      selectedStocks: [],
      compareMode: 'price',
      compareData: null,
      compareStocks: [],
      compareDates: [],
      loading: false,
      radarChart: null,
      barChart: null
    }
  },
  computed: {
    rankings() {
      return this.compareData?.rankings || []
    }
  },
  created() { this.fetchStocks() },
  mounted() {
    this.radarChart = echarts.init(document.getElementById('radar-compare-chart'))
    this.barChart = echarts.init(document.getElementById('bar-compare-chart'))
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.radarChart) this.radarChart.dispose()
    if (this.barChart) this.barChart.dispose()
  },
  methods: {
    handleResize() {
      this.radarChart?.resize()
      this.barChart?.resize()
    },

    async fetchStocks() {
      try {
        const { data } = await request.get('/api/stocks')
        if (data.code === 200) {
          this.stocks = data.data.list || []
          this.selectedStocks = this.stocks.slice(0, 3).map(s => s.code)
          this.loadCompare()
        }
      } catch (e) {}
    },

    async loadCompare() {
      if (this.selectedStocks.length < 2) return
      this.loading = true
      try {
        const { data } = await request.post('/api/stock-compare', {
          codes: this.selectedStocks
        })
        if (data.code === 200) {
          this.compareData = data.data
          this.renderRadarChart()
          this.renderBarChart()
          this.loadPriceCompare()
        }
      } catch (e) {
        this.$message.error('对比失败: ' + e.message)
      } finally {
        this.loading = false
      }
    },

    async loadPriceCompare() {
      const promises = this.selectedStocks.map(code =>
        request.get('/api/charts', { params: { code, days: 30 } })
      )
      const results = await Promise.all(promises)
      this.compareStocks = []
      this.compareDates = []

      results.forEach((res, i) => {
        if (res.data.code === 200 && res.data.data.dates) {
          const d = res.data.data
          if (i === 0) this.compareDates = d.dates
          let data = this.compareMode === 'price' ? d.close :
                     this.compareMode === 'change' ? d.close.map(v => ((v - d.close[0]) / d.close[0] * 100).toFixed(2)) :
                     d.volume
          this.compareStocks.push({ name: this.getStockName(this.selectedStocks[i]), data })
        }
      })
    },

    renderRadarChart() {
      if (!this.compareData) return
      const indicator = [
        { name: '趋势', max: 100 },
        { name: '动量', max: 100 },
        { name: '波动', max: 100 },
        { name: '成交量', max: 100 },
        { name: '估值', max: 100 },
        { name: '质量', max: 100 },
        { name: '成长', max: 100 },
        { name: '情绪', max: 100 }
      ]
      const series = this.compareData.rankings.map((r, i) => ({
        name: r.name,
        type: 'radar',
        data: [{
          value: [
            r.score_result.scores.trend,
            r.score_result.scores.momentum,
            r.score_result.scores.volatility,
            r.score_result.scores.volume,
            r.score_result.scores.valuation,
            r.score_result.scores.quality,
            r.score_result.scores.growth,
            r.score_result.scores.sentiment
          ],
          name: r.name
        }],
        itemStyle: { color: DIM_COLORS[i % DIM_COLORS.length] },
        areaStyle: { opacity: 0.15 }
      }))
      this.radarChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { top: 5, textStyle: { color: '#d1d4dc' } },
        radar: { indicator, radius: '65%', axisName: { color: '#d1d4dc', fontSize: 11 } },
        series
      }, true)
    },

    renderBarChart() {
      if (!this.compareData) return
      const dims = ['trend', 'momentum', 'volatility', 'volume', 'valuation', 'quality', 'growth', 'sentiment']
      const dimLabels = ['趋势', '动量', '波动', '成交量', '估值', '质量', '成长', '情绪']
      const series = this.compareData.rankings.map((r, i) => ({
        name: r.name,
        type: 'bar',
        data: dims.map(d => r.score_result.scores[d]),
        itemStyle: { color: DIM_COLORS[i % DIM_COLORS.length] }
      }))
      this.barChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { top: 5, textStyle: { color: '#d1d4dc' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value', max: 100, axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
        yAxis: { type: 'category', data: dimLabels, axisLabel: { color: '#d1d4dc' } },
        series
      }, true)
    },

    getStockName(code) {
      const s = this.stocks.find(x => x.code === code)
      return s ? s.name : code
    },

    scoreColorClass(score) {
      if (score >= 75) return 'text-up'
      if (score >= 55) return 'text-warn'
      return 'text-down'
    },

    gradeType(grade) {
      if (grade.startsWith('A')) return 'success'
      if (grade.startsWith('B')) return 'primary'
      if (grade.startsWith('C')) return 'warning'
      return 'danger'
    },

    tableRowClassName({ row }) {
      return row.rank === 1 ? 'rank-first-row' : ''
    }
  }
}
</script>

<style scoped>
.app-container { padding: 16px; background: #0f0f1a; min-height: 100vh; }
.dark-card { background: #1a1a2e !important; border: 1px solid #2a2a3e !important; }
.dark-card ::v-deep .el-card__header { border-bottom: 1px solid #2a2a3e !important; color: #d1d4dc; background: #1a1a2e; }
.dark-card ::v-deep .el-table { background: #1a1a2e; color: #d1d4dc; }
.dark-card ::v-deep .el-table th { background: #2a2a3e !important; color: #d1d4dc !important; }
.dark-card ::v-deep .el-table tr { background: #1a1a2e; }
.dark-card ::v-deep .el-table--striped .el-table__body tr.el-table__row--striped td { background: #1e1e35; }

/* 排名徽章 */
.rank-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 50%; font-weight: 700; font-size: 13px;
  background: #2a2a3e; color: #909399;
}
.rank-1 { background: linear-gradient(135deg, #ffd700, #ffaa00); color: #000; }
.rank-2 { background: linear-gradient(135deg, #c0c0c0, #999); color: #000; }
.rank-3 { background: linear-gradient(135deg, #cd7f32, #a0522d); color: #fff; }

.stock-name { font-weight: 600; color: #d1d4dc; margin-right: 6px; }
.stock-code { color: #606266; font-size: 12px; }
.score-value { font-weight: 700; font-size: 16px; }
.rec-text { font-size: 12px; color: #d1d4dc; }
.text-up { color: #26a69a; }
.text-down { color: #ef5350; }
.text-warn { color: #E6A23C; }

/* 维度冠军 */
.dim-champions { padding: 8px 0; }
.dim-champ-row {
  display: flex; align-items: center; padding: 8px 0;
  border-bottom: 1px solid #2a2a3e;
}
.dim-label { width: 60px; color: #909399; font-size: 13px; }
.champ-best { flex: 1; color: #26a69a; font-size: 13px; }
.champ-worst { flex: 1; color: #ef5350; font-size: 12px; text-align: right; }
.champ-score { font-weight: 700; margin-left: 4px; }
.champ-score-low { font-weight: 700; margin-left: 4px; }

/* 统计框 */
.stat-box { text-align: center; padding: 16px; background: #2a2a3e; border-radius: 8px; }
.stat-num { font-size: 28px; font-weight: 700; }
.stat-label { color: #909399; font-size: 12px; margin-top: 4px; }
</style>
