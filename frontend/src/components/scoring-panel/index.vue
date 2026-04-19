<template>
  <div v-if="loading" class="score-loading">
    <i class="el-icon-loading"></i> 评分加载中...
  </div>
  <div v-else-if="scoreData" class="scoring-panel">
    <!-- 总分展示 -->
    <div class="score-hero">
      <div class="score-circle" :class="gradeClass">
        <div class="score-number">{{ scoreData.score }}</div>
        <div class="score-grade">{{ scoreData.grade }}</div>
      </div>
      <div class="score-meta">
        <div class="rec-badge" :class="recClass">{{ scoreData.recommendation }}</div>
        <div class="percentile-bar">
          <div class="percentile-label">市场百分位</div>
          <div class="percentile-track">
            <div class="percentile-fill" :style="{ width: scoreData.percentile + '%' }"></div>
          </div>
          <div class="percentile-value">{{ scoreData.percentile }}%</div>
        </div>
        <div v-if="scoreData.sector_ranking" class="sector-rank">
          行业排名: <strong>{{ scoreData.sector_ranking.rank }}</strong> / {{ scoreData.sector_ranking.total }}
          <span class="percentile-badge">Top {{ 100 - scoreData.sector_ranking.percentile }}%</span>
        </div>
      </div>
    </div>

    <!-- 8维度评分 -->
    <div class="dim-grid">
      <div v-for="dim in scoreData.dimensions" :key="dim.dim" class="dim-card">
        <div class="dim-header">
          <span class="dim-name">{{ dim.label }}</span>
          <span class="dim-level" :class="levelClass(dim.level)">{{ dim.level }}</span>
        </div>
        <div class="dim-score">{{ dim.score }}</div>
        <div class="dim-bar-track">
          <div class="dim-bar-fill" :style="{ width: dim.score + '%', background: dimBarColor(dim.score) }"></div>
        </div>
        <div class="dim-weight">权重 {{ dim.weight }}%</div>
      </div>
    </div>

    <!-- 强项/弱项 -->
    <el-row :gutter="16" style="margin-top:16px;">
      <el-col :span="12">
        <div class="strength-box">
          <div class="box-title text-up">💪 强项</div>
          <div v-for="s in scoreData.strengths" :key="s.dim" class="item-row">
            <span>{{ s.label }}</span>
            <span class="item-score text-up">{{ s.score }}</span>
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="weakness-box">
          <div class="box-title text-down">⚠️ 弱项</div>
          <div v-for="w in scoreData.weaknesses" :key="w.dim" class="item-row">
            <span>{{ w.label }}</span>
            <span class="item-score text-down">{{ w.score }}</span>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'ScoringPanel',
  props: {
    code: { type: String, default: '' }
  },
  data() {
    return { scoreData: null, loading: true }
  },
  computed: {
    gradeClass() {
      if (!this.scoreData) return ''
      const g = this.scoreData.grade
      if (g.startsWith('A')) return 'grade-a'
      if (g.startsWith('B')) return 'grade-b'
      if (g.startsWith('C')) return 'grade-c'
      return 'grade-d'
    },
    recClass() {
      if (!this.scoreData) return ''
      const r = this.scoreData.recommendation
      if (r.includes('推荐')) return 'rec-good'
      if (r === '关注') return 'rec-warn'
      return 'rec-bad'
    }
  },
  watch: {
    code: { handler() { this.loadScore() }, immediate: true }
  },
  methods: {
    async loadScore() {
      if (!this.code) return
      this.loading = true
      try {
        const { data } = await request.get('/api/stock-scoring-dashboard', {
          params: { code: this.code }
        })
        if (data.code === 200) this.scoreData = data.data
      } catch (e) {} finally { this.loading = false }
    },
    dimBarColor(score) {
      if (score >= 75) return 'linear-gradient(90deg, #26a69a, #4caf50)'
      if (score >= 60) return 'linear-gradient(90deg, #409EFF, #64b5f6)'
      if (score >= 45) return 'linear-gradient(90deg, #E6A23C, #ffb74d)'
      return 'linear-gradient(90deg, #ef5350, #e57373)'
    },
    levelClass(level) {
      if (level === '优') return 'level-good'
      if (level === '良') return 'level-ok'
      if (level === '中') return 'level-warn'
      return 'level-bad'
    }
  }
}
</script>

<style scoped>
.score-loading { text-align: center; padding: 40px; color: #909399; }
.scoring-panel { padding: 16px; }

/* 总分英雄区 */
.score-hero { display: flex; align-items: center; gap: 24px; margin-bottom: 20px; }
.score-circle {
  width: 100px; height: 100px; border-radius: 50%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  border: 3px solid;
}
.grade-a { border-color: #26a69a; background: rgba(38,166,154,0.1); }
.grade-b { border-color: #409EFF; background: rgba(64,158,255,0.1); }
.grade-c { border-color: #E6A23C; background: rgba(230,162,60,0.1); }
.grade-d { border-color: #ef5350; background: rgba(239,83,80,0.1); }
.score-number { font-size: 32px; font-weight: 700; color: #d1d4dc; }
.score-grade { font-size: 16px; font-weight: 600; }
.grade-a .score-grade { color: #26a69a; }
.grade-b .score-grade { color: #409EFF; }
.grade-c .score-grade { color: #E6A23C; }
.grade-d .score-grade { color: #ef5350; }

.score-meta { flex: 1; }
.rec-badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600; margin-bottom: 12px; }
.rec-good { background: rgba(38,166,154,0.2); color: #26a69a; }
.rec-warn { background: rgba(230,162,60,0.2); color: #E6A23C; }
.rec-bad { background: rgba(239,83,80,0.2); color: #ef5350; }

.percentile-bar { margin-bottom: 8px; }
.percentile-label { color: #909399; font-size: 12px; margin-bottom: 4px; }
.percentile-track { height: 8px; background: #2a2a3e; border-radius: 4px; overflow: hidden; }
.percentile-fill { height: 100%; background: linear-gradient(90deg, #409EFF, #26a69a); border-radius: 4px; transition: width 0.5s; }
.percentile-value { font-size: 13px; color: #d1d4dc; margin-top: 2px; }

.sector-rank { color: #909399; font-size: 13px; }
.sector-rank strong { color: #d1d4dc; }
.percentile-badge { background: #2a2a3e; padding: 1px 8px; border-radius: 10px; margin-left: 8px; color: #E6A23C; font-size: 11px; }

/* 维度网格 */
.dim-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.dim-card { background: #2a2a3e; border-radius: 8px; padding: 12px; }
.dim-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.dim-name { color: #909399; font-size: 12px; }
.dim-level { font-size: 11px; padding: 1px 6px; border-radius: 8px; }
.level-good { background: rgba(38,166,154,0.2); color: #26a69a; }
.level-ok { background: rgba(64,158,255,0.2); color: #409EFF; }
.level-warn { background: rgba(230,162,60,0.2); color: #E6A23C; }
.level-bad { background: rgba(239,83,80,0.2); color: #ef5350; }
.dim-score { font-size: 22px; font-weight: 700; color: #d1d4dc; margin-bottom: 6px; }
.dim-bar-track { height: 4px; background: #1a1a2e; border-radius: 2px; overflow: hidden; margin-bottom: 4px; }
.dim-bar-fill { height: 100%; border-radius: 2px; transition: width 0.5s; }
.dim-weight { color: #606266; font-size: 11px; }

/* 强项/弱项 */
.strength-box, .weakness-box { background: #2a2a3e; border-radius: 8px; padding: 12px; }
.box-title { font-size: 14px; font-weight: 600; margin-bottom: 8px; }
.item-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #1a1a2e; font-size: 13px; }
.item-row:last-child { border-bottom: none; }
.text-up { color: #26a69a; }
.text-down { color: #ef5350; }
</style>
