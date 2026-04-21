<template>
  <div class="app-container">
    <!-- 顶部筛选 -->
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>🏆 股票评分排行榜</span>
        <div style="float:right;font-size:12px;color:#909399;">
          <span v-if="lastUpdate">更新于 {{ lastUpdate }}</span>
          <el-button size="mini" type="text" @click="loadRanking" :loading="loading">🔄 刷新</el-button>
        </div>
      </div>
      <el-row :gutter="16" align="middle">
        <el-col :span="4">
          <el-select v-model="marketFilter" size="mini" @change="loadRanking" style="width:100%;">
            <el-option label="全部市场" value="" />
            <el-option label="A股" value="A" />
            <el-option label="港股" value="HK" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="gradeFilter" size="mini" @change="loadRanking" style="width:100%;">
            <el-option label="全部评级" value="" />
            <el-option label="A+ / A" value="A" />
            <el-option label="B+ / B" value="B" />
            <el-option label="C+ / C" value="C" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="limitFilter" size="mini" @change="loadRanking" style="width:100%;">
            <el-option label="Top 20" :value="20" />
            <el-option label="Top 50" :value="50" />
            <el-option label="Top 100" :value="100" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="sortBy" size="mini" @change="loadRanking" style="width:100%;">
            <el-option label="按总分" value="score" />
            <el-option label="按趋势" value="trend" />
            <el-option label="按动量" value="momentum" />
            <el-option label="按估值" value="valuation" />
            <el-option label="按质量" value="quality" />
            <el-option label="按成长" value="growth" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-input v-model="searchCode" size="mini" placeholder="搜索代码/名称" clearable @input="filterBySearch" />
        </el-col>
        <el-col :span="4">
          <el-switch v-model="autoRefresh" active-text="自动刷新" inactive-text="" @change="toggleAutoRefresh" style="margin-right:8px;"></el-switch>
        </el-col>
      </el-row>
    </el-card>

    <!-- 加载骨架 -->
    <div v-if="loading && !rankings.length" class="skeleton-container">
      <el-skeleton :rows="3" animated style="margin-bottom:20px;" />
      <el-skeleton :rows="2" animated style="margin-bottom:20px;" />
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 空状态 -->
    <el-empty v-else-if="!loading && rankings.length === 0" description="暂无评分数据" :image-size="200">
      <el-button type="primary" @click="loadRanking">重新加载</el-button>
    </el-empty>

    <!-- 错误状态 -->
    <el-alert v-else-if="errorMsg" :title="errorMsg" type="error" show-icon closable @close="errorMsg=''" style="margin-bottom:20px;" />

    <!-- 数据内容 -->
    <template v-else>
      <!-- 统计概览 -->
      <el-row :gutter="16" style="margin-bottom:20px;">
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value">{{ rankings.length }}</div>
            <div class="stat-label">上榜股票</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value text-up">{{ summary.avg_score }}</div>
            <div class="stat-label">平均评分</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value" style="color:#26a69a;">{{ summary.max_score }}</div>
            <div class="stat-label">最高评分</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value" style="color:#ef5350;">{{ summary.min_score }}</div>
            <div class="stat-label">最低评分</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value" style="color:#409EFF;">{{ summary.gradeA }}</div>
            <div class="stat-label">A级+数量</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <div class="stat-value text-warn">{{ summary.gradeC }}</div>
            <div class="stat-label">C级及以下</div>
          </div>
        </el-col>
      </el-row>

      <!-- 评分分布直方图 -->
      <el-row :gutter="16" style="margin-bottom:20px;">
        <el-col :span="12">
          <el-card class="dark-card">
            <div slot="header"><span>📊 评分分布</span></div>
            <div id="score-distribution-chart" style="width:100%;height:250px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="dark-card">
            <div slot="header"><span>🎯 维度均值对比</span></div>
            <div id="dim-average-chart" style="width:100%;height:250px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 排名表格 -->
      <el-card class="dark-card">
        <el-table :data="paginatedRankings" stripe size="small"
          :row-class-name="tableRowClassName"
          @row-click="goToDetail" style="cursor:pointer;"
          :default-sort="{prop: 'score', order: 'descending'}">
          <el-table-column label="排名" width="65" align="center">
            <template slot-scope="{ row }">
              <span class="rank-badge" :class="'rank-' + row.rank">{{ row.rank }}</span>
            </template>
          </el-table-column>
          <el-table-column label="股票" min-width="150">
            <template slot-scope="{ row }">
              <div class="stock-cell">
                <span class="stock-name">{{ row.name }}</span>
                <span class="stock-code">{{ row.code }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="总分" width="75" align="center" sortable prop="score">
            <template slot-scope="{ row }">
              <span class="score-big" :class="scoreColor(row.score)">{{ row.score }}</span>
            </template>
          </el-table-column>
          <el-table-column label="评级" width="60" align="center">
            <template slot-scope="{ row }">
              <el-tag size="mini" :type="gradeType(row.grade)" effect="dark">{{ row.grade }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="百分位" width="65" align="center">
            <template slot-scope="{ row }">
              <span class="percentile-text">{{ row.percentile }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="趋势" width="58" align="center">
            <template slot-scope="{ row }">
              <span :class="row.scores.trend >= 60 ? 'text-up' : 'text-down'">{{ row.scores.trend }}</span>
            </template>
          </el-table-column>
          <el-table-column label="动量" width="58" align="center">
            <template slot-scope="{ row }">
              <span :class="row.scores.momentum >= 60 ? 'text-up' : 'text-down'">{{ row.scores.momentum }}</span>
            </template>
          </el-table-column>
          <el-table-column label="估值" width="58" align="center">
            <template slot-scope="{ row }">
              <span :class="row.scores.valuation >= 60 ? 'text-up' : 'text-down'">{{ row.scores.valuation }}</span>
            </template>
          </el-table-column>
          <el-table-column label="质量" width="58" align="center">
            <template slot-scope="{ row }">
              <span :class="row.scores.quality >= 60 ? 'text-up' : 'text-down'">{{ row.scores.quality }}</span>
            </template>
          </el-table-column>
          <el-table-column label="成长" width="58" align="center">
            <template slot-scope="{ row }">
              <span :class="row.scores.growth >= 60 ? 'text-up' : 'text-down'">{{ row.scores.growth }}</span>
            </template>
          </el-table-column>
          <el-table-column label="价格" width="80" align="right">
            <template slot-scope="{ row }">{{ row.price.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="涨跌" width="70" align="center">
            <template slot-scope="{ row }">
              <span :class="row.change >= 0 ? 'text-up' : 'text-down'">
                {{ row.change >= 0 ? '+' : '' }}{{ row.change }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="70" align="center" fixed="right">
            <template slot-scope="{ row }">
              <el-button size="mini" type="text" @click.stop="showScore(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            background
            layout="total, sizes, prev, pager, next"
            :total="filteredRankings.length"
            :page-size="pageSize"
            :page-sizes="[20, 50, 100]"
            :current-page.sync="currentPage"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
    </template>

    <!-- 评分详情弹窗 -->
    <el-dialog title="📊 评分详情" :visible.sync="scoreDialogVisible" width="600px" custom-class="dark-dialog" append-to-body>
      <scoring-panel v-if="scoreDialogCode" :code="scoreDialogCode" />
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
import ScoringPanel from '@/components/scoring-panel/index.vue'
import * as echarts from 'echarts'

export default {
  name: 'ScoringDashboard',
  components: { ScoringPanel },
  data() {
    return {
      rankings: [],
      filteredRankings: [],
      summary: { avg_score: 0, max_score: 0, min_score: 0, gradeA: 0, gradeC: 0 },
      marketFilter: '',
      gradeFilter: '',
      limitFilter: 50,
      sortBy: 'score',
      searchCode: '',
      loading: false,
      errorMsg: '',
      lastUpdate: '',
      autoRefresh: false,
      refreshTimer: null,
      scoreDialogVisible: false,
      scoreDialogCode: '',
      distChart: null,
      dimAvgChart: null,
      currentPage: 1,
      pageSize: 20
    }
  },
  computed: {
    paginatedRankings() {
      const start = (this.currentPage - 1) * this.pageSize
      return this.filteredRankings.slice(start, start + this.pageSize)
    }
  },
  created() { this.loadRanking() },
  mounted() {
    this.$nextTick(() => {
      this.distChart = echarts.init(document.getElementById('score-distribution-chart'))
      this.dimAvgChart = echarts.init(document.getElementById('dim-average-chart'))
    })
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.distChart) this.distChart.dispose()
    if (this.dimAvgChart) this.dimAvgChart.dispose()
    if (this.refreshTimer) clearInterval(this.refreshTimer)
  },
  methods: {
    handleResize() {
      this.distChart?.resize()
      this.dimAvgChart?.resize()
    },

    async loadRanking() {
      this.loading = true
      this.errorMsg = ''
      try {
        const params = { limit: this.limitFilter }
        if (this.marketFilter) params.market = this.marketFilter
        if (this.sortBy && this.sortBy !== 'score') params.sort_by = this.sortBy
        const { data } = await request.get('/stock-ranking', { params })
        if (data.code === 200) {
          this.rankings = data.data.rankings || []
          this.summary = {
            avg_score: data.data.avg_score || 0,
            max_score: data.data.max_score || 0,
            min_score: data.data.min_score || 0,
            gradeA: this.rankings.filter(r => r.grade && r.grade.startsWith('A')).length,
            gradeC: this.rankings.filter(r => r.grade && (r.grade.startsWith('C') || r.grade === 'D')).length
          }
          this.lastUpdate = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
          this.applyFilters()
          this.$nextTick(() => this.renderCharts())
        } else {
          this.errorMsg = data.message || '加载失败'
        }
      } catch (e) {
        this.errorMsg = '网络错误: ' + (e.message || '未知错误')
      } finally {
        this.loading = false
      }
    },

    applyFilters() {
      let list = [...this.rankings]
      if (this.gradeFilter) {
        list = list.filter(r => r.grade && r.grade.startsWith(this.gradeFilter))
      }
      if (this.searchCode) {
        const q = this.searchCode.toLowerCase()
        list = list.filter(r => r.code.toLowerCase().includes(q) || (r.name && r.name.toLowerCase().includes(q)))
      }
      this.filteredRankings = list
      this.currentPage = 1
    },

    filterBySearch() {
      this.applyFilters()
    },

    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
    },

    handlePageChange(val) {
      this.currentPage = val
    },

    toggleAutoRefresh(val) {
      if (this.refreshTimer) {
        clearInterval(this.refreshTimer)
        this.refreshTimer = null
      }
      if (val) {
        this.refreshTimer = setInterval(() => this.loadRanking(), 60000) // 1分钟刷新
      }
    },

    renderCharts() {
      this.renderDistributionChart()
      this.renderDimAvgChart()
    },

    renderDistributionChart() {
      if (!this.distChart || !this.rankings.length) return
      const ranges = ['0-20', '21-40', '41-60', '61-70', '71-80', '81-90', '91-100']
      const counts = [0, 0, 0, 0, 0, 0, 0]
      const colors = ['#ef5350', '#ef5350', '#E6A23C', '#E6A23C', '#409EFF', '#26a69a', '#26a69a']
      this.rankings.forEach(r => {
        const s = r.score || 0
        if (s <= 20) counts[0]++
        else if (s <= 40) counts[1]++
        else if (s <= 60) counts[2]++
        else if (s <= 70) counts[3]++
        else if (s <= 80) counts[4]++
        else if (s <= 90) counts[5]++
        else counts[6]++
      })
      this.distChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: { type: 'category', data: ranges, axisLabel: { color: '#d1d4dc', fontSize: 11 } },
        yAxis: { type: 'value', axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
        series: [{
          type: 'bar',
          data: counts.map((c, i) => ({ value: c, itemStyle: { color: colors[i] } })),
          label: { show: true, position: 'top', color: '#d1d4dc', fontSize: 11 },
          barWidth: '50%',
          animationDuration: 800
        }]
      }, true)
    },

    renderDimAvgChart() {
      if (!this.dimAvgChart || !this.rankings.length) return
      const dims = ['trend', 'momentum', 'volatility', 'volume', 'valuation', 'quality', 'growth', 'sentiment']
      const labels = ['趋势', '动量', '波动', '成交量', '估值', '质量', '成长', '情绪']
      const avgs = dims.map(d => {
        const total = this.rankings.reduce((sum, r) => sum + ((r.scores && r.scores[d]) || 0), 0)
        return Math.round(total / this.rankings.length)
      })
      const colors = avgs.map(v => v >= 60 ? '#26a69a' : v >= 45 ? '#E6A23C' : '#ef5350')
      this.dimAvgChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: { type: 'category', data: labels, axisLabel: { color: '#d1d4dc', fontSize: 11 } },
        yAxis: { type: 'value', min: 0, max: 100, axisLabel: { color: '#d1d4dc' }, splitLine: { lineStyle: { color: '#2a2a3e' } } },
        series: [{
          type: 'bar',
          data: avgs.map((v, i) => ({ value: v, itemStyle: { color: colors[i] } })),
          label: { show: true, position: 'top', color: '#d1d4dc', fontSize: 11 },
          barWidth: '50%',
          animationDuration: 800,
          markLine: {
            data: [{ yAxis: 60 }],
            lineStyle: { color: '#E6A23C', type: 'dashed' },
            label: { color: '#E6A23C', formatter: '及格 60' }
          }
        }]
      }, true)
    },

    goToDetail(row) {
      this.$router.push({ path: '/stock-detail', query: { code: row.code } })
    },
    showScore(row) {
      this.scoreDialogCode = row.code
      this.scoreDialogVisible = true
    },
    tableRowClassName({ row }) {
      if (row.rank === 1) return 'rank-first-row'
      if (row.score >= 75) return 'rank-good-row'
      return ''
    },
    scoreColor(score) {
      if (score >= 75) return 'text-up'
      if (score >= 55) return 'text-warn'
      return 'text-down'
    },
    gradeType(grade) {
      if (!grade) return 'info'
      if (grade.startsWith('A')) return 'success'
      if (grade.startsWith('B')) return 'primary'
      if (grade.startsWith('C')) return 'warning'
      return 'danger'
    }
  }
}
</script>

<style scoped>
.app-container { padding: 16px; background: #0f0f1a; min-height: 100vh; }

.skeleton-container { padding: 20px; background: #1a1a2e; border-radius: 8px; }

.stat-card { background: #1a1a2e; border: 1px solid #2a2a3e; border-radius: 8px; padding: 16px; text-align: center; transition: transform 0.2s; }
.stat-card:hover { transform: translateY(-2px); }
.stat-value { font-size: 28px; font-weight: 700; }
.stat-label { color: #909399; font-size: 12px; margin-top: 4px; }

.rank-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 50%; font-weight: 700; font-size: 13px;
  background: #2a2a3e; color: #909399;
}
.rank-1 { background: linear-gradient(135deg, #ffd700, #ffaa00); color: #000; }
.rank-2 { background: linear-gradient(135deg, #c0c0c0, #999); color: #000; }
.rank-3 { background: linear-gradient(135deg, #cd7f32, #a0522d); color: #fff; }

.stock-cell { display: flex; align-items: center; gap: 6px; }
.stock-name { font-weight: 600; color: #d1d4dc; }
.stock-code { color: #606266; font-size: 12px; }
.score-big { font-weight: 700; font-size: 16px; }
.percentile-text { color: #909399; font-size: 12px; }
.text-up { color: #26a69a; }
.text-down { color: #ef5350; }
.text-warn { color: #E6A23C; }

.dark-card { background: #1a1a2e !important; border: 1px solid #2a2a3e !important; }
.dark-card ::v-deep .el-card__header { border-bottom: 1px solid #2a2a3e !important; color: #d1d4dc; background: #1a1a2e; }
.dark-card ::v-deep .el-table { background: #1a1a2e; color: #d1d4dc; }
.dark-card ::v-deep .el-table th { background: #2a2a3e !important; color: #d1d4dc !important; }
.dark-card ::v-deep .el-table tr { background: #1a1a2e; }
.dark-card ::v-deep .el-table tr:hover > td { background: rgba(64,158,255,0.1) !important; }
.dark-card ::v-deep .el-table--striped .el-table__body tr.el-table__row--striped td { background: #1e1e35; }

.pagination-wrapper { margin-top: 16px; display: flex; justify-content: center; }
.dark-card ::v-deep .el-pagination { background: #1a1a2e; }
.dark-card ::v-deep .el-pagination .btn-prev,
.dark-card ::v-deep .el-pagination .btn-next,
.dark-card ::v-deep .el-pagination .el-pager li { background: #2a2a3e !important; color: #d1d4dc !important; }
.dark-card ::v-deep .el-pagination .el-pager li.active { background: #409EFF !important; color: #fff !important; }

/* 行高亮 */
::v-deep .rank-first-row { background: rgba(255,215,0,0.08) !important; }
::v-deep .rank-good-row { background: rgba(38,166,154,0.05) !important; }

/* 弹窗暗色 */
::v-deep .dark-dialog { background: #1a1a2e !important; }
::v-deep .dark-dialog .el-dialog__header { border-bottom: 1px solid #2a2a3e; }
::v-deep .dark-dialog .el-dialog__title { color: #d1d4dc; }
::v-deep .dark-dialog .el-dialog__body { color: #d1d4dc; }
</style>
