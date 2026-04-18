<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>{{ $route.meta.title }}</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div></el-card>
    <el-card v-if="data"><pre style="white-space:pre-wrap;font-size:12px;">{{ JSON.stringify(data, null, 2) }}</pre></el-card>
    <el-empty v-else description="暂无数据" />
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'GenericPage',
  data() { return { data: null, loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/stats')
        if (data.code === 200) this.data = data.data
      } catch (e) {}
      finally { this.loading = false }
    }
  }
}
</script>
