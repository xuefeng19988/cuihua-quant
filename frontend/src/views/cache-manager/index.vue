<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>⚡ API缓存管理</span></div></el-card>
    <el-card v-if="data.enabled !== undefined">
      <p>缓存状态: <el-tag :type="data.enabled ? 'success' : 'info'">{{ data.enabled ? '已启用' : '已禁用' }}</el-tag></p>
      <p>缓存命中率: <strong>{{ data.hit_rate }}%</strong></p>
      <p>缓存TTL: <strong>{{ data.ttl }}秒</strong></p>
      <p>内存使用: <strong>{{ data.memory_usage }}</strong></p>
      <el-divider />
      <h4>已缓存接口</h4>
      <el-tag v-for="e in data.cached_endpoints" :key="e" style="margin:4px;">{{ e }}</el-tag>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'CacheManager', data() { return { data: {} } },
  created() { this.fetchData() },
  methods: {
    async fetchData() { try { const { data } = await request.get('/api/cache/config'); if (data.code === 200) this.data = data.data } catch (e) {} }
  }
}
</script>
