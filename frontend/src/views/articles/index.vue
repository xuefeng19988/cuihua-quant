<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>📰 文章信息</span>
        <el-button size="mini" style="float:right;" icon="el-icon-refresh" @click="fetchArticles">刷新</el-button>
      </div>
      <el-form :inline="true">
        <el-form-item label="日期"><el-date-picker v-model="query.date" type="date" value-format="yyyy-MM-dd" /></el-form-item>
        <el-form-item label="关键词"><el-input v-model="query.keyword" placeholder="搜索标题..." /></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchArticles">🔍 查询</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <div slot="header">
        <span>文章列表 ({{ total }} 篇)</span>
        <el-tag size="mini" style="float:right;">{{ query.date || '全部日期' }}</el-tag>
      </div>
      <el-empty v-if="articles.length === 0" description="暂无文章数据" />
      <el-table v-else :data="articles" style="width: 100%">
        <el-table-column prop="date" label="日期" width="100" />
        <el-table-column prop="platform" label="来源" width="100" />
        <el-table-column prop="title" label="标题" />
        <el-table-column label="相关股票" width="120">
          <template slot-scope="{ row }">
            <el-tag v-for="stock in row.stocks" :key="stock" size="mini" style="margin: 2px;">{{ stock }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top: 16px; text-align: center;"
        layout="prev, pager, next" :total="total" :page-size="20" :current-page.sync="page" @current-change="fetchArticles" />
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Articles',
  data() {
    return {
      query: { date: '', keyword: '' },
      articles: [],
      total: 0,
      page: 1
    }
  },
  created() { this.fetchArticles() },
  methods: {
    fetchArticles() {
      // 模拟数据
      this.articles = []
      this.total = 0
    }
  }
}
</script>
