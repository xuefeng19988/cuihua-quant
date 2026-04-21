<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>👥 策略社区</span></div></el-card>
    <el-row :gutter="20">
      <el-col :span="6" v-for="s in stats" :key="s.label"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;">{{ s.label }}</div><div style="font-size:24px;font-weight:600;">{{ s.value }}</div></el-card></el-col>
    </el-row>
    <el-card style="margin-top:20px;"><div slot="header"><span>🔥 热门策略</span></div>
      <el-table :data="data.trending"><el-table-column prop="strategy" label="策略" /><el-table-column prop="author" label="作者" /><el-table-column prop="likes" label="点赞" /><el-table-column prop="subs" label="订阅" /></el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Community', data() { return { data: { trending: [] }, stats: [] } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try {
        const { data } = await request.get('/community/stats')
        if (data.code === 200) {
          this.data = data.data
          this.stats = [
            { label: '策略总数', value: data.data.total_strategies },
            { label: '用户总数', value: data.data.total_users },
            { label: '分享总数', value: data.data.total_shares },
            { label: '本周新增', value: 12 }
          ]
        }
      } catch (e) {}
    }
  }
}
</script>
