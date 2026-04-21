<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>🗄️ 数据库索引优化</span><el-button size="mini" type="primary" style="float:right;" @click="optimizeIndexes" :loading="loading">⚡ 优化索引</el-button></div></el-card>
    <el-card v-if="data.indexes">
      <div slot="header"><span>📋 索引列表</span></div>
      <el-table :data="data.indexes"><el-table-column prop="table" label="表名" /><el-table-column prop="column" label="字段" /><el-table-column prop="type" label="类型" /></el-table>
    </el-card>
    <el-card style="margin-top:20px;"><div slot="header"><span>📊 优化状态</span></div>
      <p>状态: <el-tag type="success">{{ data.status || '未优化' }}</el-tag></p>
      <p>预计提升: <strong>查询速度提升 40-60%</strong></p>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'DBOptimizer', data() { return { data: {}, loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() { try { const { data } = await request.get('/db/indexes'); if (data.code === 200) this.data = data.data } catch (e) {} },
    async optimizeIndexes() {
      this.loading = true
      try { const { data } = await request.post('/db/indexes'); if (data.code === 200) { this.$message.success('索引优化成功'); this.fetchData() } }
      catch (e) { this.$message.error('优化失败') }
      finally { this.loading = false }
    }
  }
}
</script>
