<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>🔥 热力图</span><el-tag size="mini" style="float:right;">{{ sectors.length }} 个板块</el-tag></div>
    </el-card>
    <el-row :gutter="16">
      <el-col :span="8" v-for="sector in sectors" :key="sector.name">
        <el-card shadow="hover" style="margin-bottom:16px;">
          <div style="font-weight:600;margin-bottom:12px;">{{ sector.name }}</div>
          <div style="font-size:24px;font-weight:600;margin-bottom:8px;" :style="{color: sector.change > 0 ? '#67C23A' : '#F56C6C'}">{{ sector.change > 0 ? '+' : '' }}{{ sector.change }}%</div>
          <div style="color:#909399;font-size:12px;">{{ sector.stocks }} 只股票</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Heatmap',
  data() { return { sectors: [] } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try {
        const { data } = await request.get('/api/heatmap')
        if (data.code === 200) this.sectors = data.data.sectors || []
      } catch (e) { this.$message.error('获取热力图数据失败') }
    }
  }
}
</script>
