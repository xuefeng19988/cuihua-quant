<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <el-form :inline="true">
        <el-form-item label="日期"><el-date-picker v-model="date" type="date" value-format="yyyy-MM-dd" /></el-form-item>
        <el-form-item label="关键词"><el-input v-model="keyword" placeholder="搜索标题..." /></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchArticles">🔍 查询</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card>
      <div slot="header"><span>📰 文章列表</span></div>
      <el-empty description="暂无文章数据" />
    </el-card>
  </div>
</template>
<script>
export default {
  name: 'Articles',
  data() { return { date: '', keyword: '' } },
  methods: { fetchArticles() { this.$message.info('文章查询功能开发中') } }
}
</script>
