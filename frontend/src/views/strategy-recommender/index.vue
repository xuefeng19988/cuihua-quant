<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>🎯 策略推荐引擎</span></div></el-card>
    <el-card v-if="data.recommendations">
      <h3>👤 用户画像</h3>
      <p>风险偏好: {{ data.user_profile.risk_level }} | 市场: {{ data.user_profile.preferred_markets.join('/') }} | 风格: {{ data.user_profile.trading_style }}</p>
      <el-divider />
      <h3>📋 推荐策略</h3>
      <el-table :data="data.recommendations"><el-table-column prop="strategy" label="策略" /><el-table-column prop="match_score" label="匹配度"><template slot-scope="{ row }"><el-progress :percentage="row.match_score" :color="row.match_score>85?'#67C23A':'#E6A23C'" /></template></el-table-column><el-table-column prop="reason" label="推荐理由" /></el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'StrategyRecommender', data() { return { data: {} } },
  created() { this.fetchData() },
  methods: {
    async fetchData() { try { const { data } = await request.get('/api/strategy-recommender'); if (data.code === 200) this.data = data.data } catch (e) {} }
  }
}
</script>
