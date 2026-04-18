<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>📰 文章信息</span>
        <el-button size="mini" style="float:right;" icon="el-icon-refresh" @click="fetchArticles">刷新</el-button>
      </div>
      <el-form :inline="true">
        <el-form-item label="日期">
          <el-date-picker v-model="query.date" type="date" value-format="yyyy-MM-dd" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="搜索标题..." clearable @keyup.enter.native="fetchArticles" />
        </el-form-item>
        <el-form-item label="仅股票相关">
          <el-switch v-model="query.stock_only" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchArticles">🔍 查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 统计信息 -->
      <div v-if="total > 0" style="margin-top: 10px; color: #909399; font-size: 13px;">
        共 {{ total }} 篇文章 | 第 {{ page }}/{{ totalPages }} 页
        <span v-if="query.date"> | 日期: {{ query.date }}</span>
        <span v-if="query.keyword"> | 关键词: "{{ query.keyword }}"</span>
        <span v-if="query.stock_only"> | 仅股票相关</span>
      </div>
    </el-card>

    <el-card>
      <el-empty v-if="!loading && articles.length === 0" description="暂无文章数据，请选择日期或点击查询" />
      <el-table v-else :data="articles" style="width: 100%" v-loading="loading">
        <el-table-column prop="date" label="日期" width="100" />
        <el-table-column prop="platform" label="来源" width="110">
          <template slot-scope="{ row }">
            <el-tag size="mini" type="info">{{ row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="300">
          <template slot-scope="{ row }">
            <a v-if="row.url" :href="row.url" target="_blank" style="color: #409EFF; text-decoration: none;">
              {{ row.title }}
            </a>
            <span v-else>{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="相关股票" width="160">
          <template slot-scope="{ row }">
            <span v-if="row.stocks.length === 0" style="color: #c0c4cc;">-</span>
            <template v-else>
              <el-tag v-for="stock in row.stocks" :key="stock" size="mini" type="success" style="margin: 2px;">
                {{ stock }}
              </el-tag>
            </template>
          </template>
        </el-table-column>
        <el-table-column label="相关度" width="90">
          <template slot-scope="{ row }">
            <el-tag v-if="row.relevance === 'high'" size="mini" type="danger">高</el-tag>
            <el-tag v-else-if="row.relevance === 'medium'" size="mini" type="warning">中</el-tag>
            <el-tag v-else size="mini">低</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="total > 0"
        style="margin-top: 16px; text-align: center;"
        layout="prev, pager, next, total"
        :total="total"
        :page-size="perPage"
        :current-page.sync="page"
        @current-change="fetchArticles"
      />
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'Articles',
  data() {
    return {
      query: { date: '', keyword: '', stock_only: false },
      articles: [],
      total: 0,
      page: 1,
      perPage: 20,
      totalPages: 0,
      loading: false
    }
  },
  created() { this.fetchArticles() },
  methods: {
    async fetchArticles() {
      this.loading = true
      try {
        const params = {
          page: this.page,
          per_page: this.perPage,
          stock_only: this.query.stock_only ? 'true' : 'false'
        }
        if (this.query.date) params.date = this.query.date
        if (this.query.keyword) params.keyword = this.query.keyword

        const res = await request({ url: '/articles', method: 'get', params })
        if (res.code === 200) {
          this.articles = res.data || []
          this.total = res.total || 0
          this.totalPages = res.total_pages || 1
        }
      } catch (e) {
        console.error('获取文章失败:', e)
        this.$message.error('获取文章数据失败')
      } finally {
        this.loading = false
      }
    },
    resetQuery() {
      this.query = { date: '', keyword: '', stock_only: false }
      this.page = 1
      this.fetchArticles()
    }
  }
}
</script>
