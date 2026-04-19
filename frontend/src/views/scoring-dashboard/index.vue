<template>
  <div class="app-container">
    <!-- 顶部筛选 -->
    <el-card style="margin-bottom:20px;">
      <div slot="header"><span>🏆 股票评分排行榜</span></div>
      <el-row :gutter="16" align="middle">
        <el-col :span="5">
          <el-select v-model="marketFilter" size="mini" @change="loadRanking" style="width:100%;">
            <el-option label="全部市场" value="" />
            <el-option label="A股" value="A" />
            <el-option label="港股" value="HK" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="gradeFilter" size="mini" @change="loadRanking" style="width:100%;">
            <el-option label="全部评级" value="" />
            <el-option label="A+ / A" value="A" />
            <el-option label="B+ / B" value="B" />
            <el-option label="C+ / C" value="C" />
          </el-option>
        </el-col>
        <el-col :span="5">
          <el-select v-model="limitFilter" size="mini" @change="loadRanking" style="width:100%;">
            <el-option label="Top 20" :value="20" />
            <el-option label="Top 50" :value="50" />
            <el-option label="Top 100" :value="100" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-input v-model="searchCode" size="mini" placeholder="搜索代码/名称" clearable @keyup.enter.native="filterBySearch" @clear="loadRanking" />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" size="mini" @click="loadRanking" :loading="loading">🔄 刷新</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计概览 -->
    <el-row v-if="rankings.length" :gutter="16" style="margin-bottom:20px;">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value">{{ rankings.length }}</div>
          <div class="stat-label">上榜股票</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value text-up">{{ summary.avg_score }}</div>
          <div class="stat-label">平均评分</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value" style="color:#26a69a;">{{ summary.max_score }}</div>
          <div class="stat-label">最高评分</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value" style="color:#ef5350;">{{ summary.min_score }}</div>
          <div class="stat-label">最低评分</div>
        </div>
      </el-col>
    </el-row>

    <!-- 排名表格 -->
    <el-card>
      <el-table :data="displayRankings" stripe size="small" 
        :row-class-name="tableRowClassName"
        @row-click="goToDetail" style="cursor:pointer;">
        <el-table-column label="排名" width="65" align="center">
          <template slot-scope="{ row }">
            <span class="rank-badge" :class="'rank-' + row.rank">{{ row.rank }}</span>
          </template>
        </el-table-column>
        <el-table-column label="股票" min-width="160">
          <template slot-scope="{ row }">
            <div class="stock-cell">
              <span class="stock-name">{{ row.name }}</span>
              <span class="stock-code">{{ row.code }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="总分" width="85" align="center" sortable :sort-method="sortByScore">
          <template slot-scope="{ row }">
            <span class="score-big" :class="scoreColor(row.score)">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column label="评级" width="65" align="center">
          <template slot-scope="{ row }">
            <el-tag size="mini" :type="gradeType(row.grade)" effect="dark">{{ row.grade }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="建议" width="80" align="center">
          <template slot-scope="{ row }">
            <span class="rec-text">{{ row.recommendation }}</span>
          </template>
        </el-table-column>
        <el-table-column label="百分位" width="80" align="center" sortable :sort-method="sortByPercentile">
          <template slot-scope="{ row }">
            <span>{{ row.percentile }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="趋势" width="70" align="center" sortable :sort-method="sortByDim('trend')">
          <template slot-scope="{ row }">
            <span :class="row.scores.trend >= 60 ? 'text-up' : 'text-down'">{{ row.scores.trend }}</span>
          </template>
        </el-table-column>
        <el-table-column label="动量" width="70" align="center" sortable :sort-method="sortByDim('momentum')">
          <template slot-scope="{ row }">
            <span :class="row.scores.momentum >= 60 ? 'text-up' : 'text-down'">{{ row.scores.momentum }}</span>
          </template>
        </el-table-column>
        <el-table-column label="估值" width="70" align="center" sortable :sort-method="sortByDim('valuation')">
          <template slot-scope="{ row }">
            <span :class="row.scores.valuation >= 60 ? 'text-up' : 'text-down'">{{ row.scores.valuation }}</span>
          </template>
        </el-table-column>
        <el-table-column label="质量" width="70" align="center" sortable :sort-method="sortByDim('quality')">
          <template slot-scope="{ row }">
            <span :class="row.scores.quality >= 60 ? 'text-up' : 'text-down'">{{ row.scores.quality }}</span>
          </template>
        </el-table-column>
        <el-table-column label="成长" width="70" align="center" sortable :sort-method="sortByDim('growth')">
          <template slot-scope="{ row }">
            <span :class="row.scores.growth >= 60 ? 'text-up' : 'text-down'">{{ row.scores.growth }}</span>
          </template>
        </el-table-column>
        <el-table-column label="价格" width="90" align="right" sortable :sort-method="sortByPrice">
          <template slot-scope="{ row }">{{ row.price.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="涨跌" width="80" align="center" sortable :sort-method="sortByChange">
          <template slot-scope="{ row }">
            <span :class="row.change >= 0 ? 'text-up' : 'text-down'">
              {{ row.change >= 0 ? '+' : '' }}{{ row.change }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template slot-scope="{ row }">
            <el-button size="mini" type="text" @click.stop="showScore(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 评分详情弹窗 -->
    <el-dialog title="📊 评分详情" :visible.sync="scoreDialogVisible" width="500px" custom-class="dark-dialog">
      <scoring-panel v-if="scoreDialogCode" :code="scoreDialogCode" />
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
import ScoringPanel from '@/components/scoring-panel/index.vue'

export default {
  name: 'ScoringDashboard',
  components: { ScoringPanel },
  data() {
    return {
      rankings: [],
      summary: { avg_score: 0, max_score: 0, min_score: 0 },
      marketFilter: '',
      gradeFilter: '',
      limitFilter: 50,
      searchCode: '',
      loading: false,
      scoreDialogVisible: false,
      scoreDialogCode: ''
    }
  },
  computed: {
    displayRankings() {
      let list = [...this.rankings]
      if (this.gradeFilter) {
        list = list.filter(r => r.grade.startsWith(this.gradeFilter))
      }
      if (this.searchCode) {
        const q = this.searchCode.toLowerCase()
        list = list.filter(r => r.code.toLowerCase().includes(q) || (r.name && r.name.toLowerCase().includes(q)))
      }
      return list
    }
  },
  created() { this.loadRanking() },
  methods: {
    async loadRanking() {
      this.loading = true
      try {
        const params = { limit: this.limitFilter }
        if (this.marketFilter) params.market = this.marketFilter
        const { data } = await request.get('/api/stock-ranking', { params })
        if (data.code === 200) {
          this.rankings = data.data.rankings
          this.summary = {
            avg_score: data.data.avg_score,
            max_score: data.data.max_score,
            min_score: data.data.min_score
          }
        }
      } catch (e) {} finally { this.loading = false }
    },
    filterBySearch() { /* computed handles it */ },
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
      if (grade.startsWith('A')) return 'success'
      if (grade.startsWith('B')) return 'primary'
      if (grade.startsWith('C')) return 'warning'
      return 'danger'
    },
    sortByScore(a, b) { return a.score - b.score },
    sortByPercentile(a, b) { return a.percentile - b.percentile },
    sortByDim(dim) { return (a, b) => a.scores[dim] - b.scores[dim] },
    sortByPrice(a, b) { return a.price - b.price },
    sortByChange(a, b) { return a.change - b.change }
  }
}
</script>

<style scoped>
.app-container { padding: 16px; background: #0f0f1a; min-height: 100vh; }

.stat-card { background: #1a1a2e; border: 1px solid #2a2a3e; border-radius: 8px; padding: 16px; text-align: center; }
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
.rec-text { font-size: 12px; color: #d1d4dc; }
.text-up { color: #26a69a; }
.text-down { color: #ef5350; }
.text-warn { color: #E6A23C; }

/* 行高亮 */
::v-deep .rank-first-row { background: rgba(255,215,0,0.08) !important; }
::v-deep .rank-good-row { background: rgba(38,166,154,0.05) !important; }

/* 表格暗色 */
::v-deep .el-table { background: #1a1a2e; color: #d1d4dc; }
::v-deep .el-table th { background: #2a2a3e !important; color: #d1d4dc !important; }
::v-deep .el-table tr { background: #1a1a2e; }
::v-deep .el-table--striped .el-table__body tr.el-table__row--striped td { background: #1e1e35; }

/* 弹窗暗色 */
::v-deep .dark-dialog { background: #1a1a2e !important; }
::v-deep .dark-dialog .el-dialog__header { border-bottom: 1px solid #2a2a3e; }
::v-deep .dark-dialog .el-dialog__title { color: #d1d4dc; }
</style>
