<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>🧠 行为分析</span>
        <el-tag size="mini" style="float:right;">风险评分: {{ riskScore }}</el-tag>
      </div>
    </el-card>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="8" v-for="b in behaviors" :key="b.bias">
        <el-card shadow="hover">
          <div style="font-weight:600;margin-bottom:8px;">{{ b.icon }} {{ b.bias }}</div>
          <el-progress :percentage="parseInt(b.severity)" :color="progressColor(b.severity)" :stroke-width="12" />
          <div style="color:#909399;font-size:12px;margin-top:8px;">{{ b.description }}</div>
          <div v-if="b.recommendation" style="margin-top:12px;padding:8px;background:#f0f9ff;border-radius:4px;font-size:12px;color:#409EFF;">
            💡 {{ b.recommendation }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:20px;" v-if="recommendations.length">
      <div slot="header"><span>📋 综合建议</span></div>
      <ul style="list-style:none;padding:0;">
        <li v-for="(r, i) in recommendations" :key="i" style="padding:8px 0;border-bottom:1px solid #eee;">
          ✅ {{ r }}
        </li>
      </ul>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Behavior',
  data() {
    return { behaviors: [], recommendations: [], riskScore: '-', loading: false }
  },
  created() { this.fetchBehavior() },
  methods: {
    async fetchBehavior() {
      this.loading = true
      try {
        const res = await request.get('/behavior')
        if (res.code === 200) {
          const d = res.data
          this.behaviors = d.behavior_patterns.map(p => ({
            ...p,
            icon: this.getIcon(p.bias)
          }))
          this.riskScore = d.overall_risk_score
          this.recommendations = d.recommendations || []
        }
      } catch (e) {
        console.error('获取行为分析失败:', e)
      } finally {
        this.loading = false
      }
    },
    getIcon(bias) {
      const map = { '过度自信': '🔄', '损失厌恶': '😰', '锚定效应': '⚓', '羊群效应': '👥', '处置效应': '📉', '近因效应': '🔍', '过度交易': '🔄', '确认偏误': '🔍', '从众心理': '👥', '风险偏好': '🎲' }
      return map[bias] || '🧠'
    },
    progressColor(severity) {
      const v = parseInt(severity)
      return v < 40 ? '#67C23A' : v < 60 ? '#E6A23C' : '#F56C6C'
    }
  }
}
</script>
