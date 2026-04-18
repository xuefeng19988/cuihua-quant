<template>
  <div class="app-container">
    <!-- 顶部统计面板 -->
    <el-row :gutter="20" style="margin-bottom:20px;">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover" style="text-align:center;">
          <div style="color:#909399;font-size:12px;">{{ stat.label }}</div>
          <div style="font-size:24px;font-weight:600;margin:8px 0;" :style="{color:stat.color}">{{ stat.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索过滤区 -->
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>📰 文章信息</span>
        <div style="float:right;">
          <el-radio-group v-model="viewMode" size="mini" @change="fetchArticles">
            <el-radio-button label="table">表格</el-radio-button>
            <el-radio-button label="card">卡片</el-radio-button>
          </el-radio-group>
          <el-button size="mini" icon="el-icon-refresh" @click="fetchArticles" style="margin-left:8px;">刷新</el-button>
        </div>
      </div>
      <el-form :inline="true" size="small">
        <el-form-item label="日期">
          <el-select v-model="query.date" placeholder="选择日期" clearable style="width:150px;">
            <el-option v-for="d in availableDates" :key="d" :label="d" :value="d" />
          </el-select>
        </el-form-item>
        <el-form-item label="平台">
          <el-select v-model="query.platform" placeholder="全部平台" clearable style="width:140px;">
            <el-option v-for="p in platforms" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="搜索标题/内容..." clearable style="width:200px;" @keyup.enter.native="fetchArticles" />
        </el-form-item>
        <el-form-item label="相关度">
          <el-select v-model="query.relevance" placeholder="全部" clearable style="width:100px;">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="仅股票相关">
          <el-switch v-model="query.stock_only" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchArticles">🔍 查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 平台分布 -->
    <el-card v-if="platformDist.length > 0" style="margin-bottom:20px;">
      <div slot="header"><span>📊 平台分布</span></div>
      <el-row :gutter="10">
        <el-col :span="4" v-for="p in platformDist" :key="p.name">
          <div style="text-align:center;padding:10px;background:#f5f7fa;border-radius:6px;">
            <div style="font-size:12px;color:#606266;">{{ p.name }}</div>
            <div style="font-size:18px;font-weight:600;margin-top:4px;">{{ p.count }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 表格视图 -->
    <el-card v-if="viewMode === 'table'">
      <el-table :data="articles" style="width:100%" v-loading="loading" stripe>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="date" label="日期" width="105" />
        <el-table-column prop="platform" label="来源" width="110">
          <template slot-scope="{ row }"><el-tag size="mini" :type="platformType(row.platform)">{{ row.platform }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="300" show-overflow-tooltip>
          <template slot-scope="{ row }">
            <a v-if="row.url" :href="row.url" target="_blank" style="color:#409EFF;text-decoration:none;">{{ row.title }}</a>
            <span v-else>{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="相关股票" width="160">
          <template slot-scope="{ row }">
            <span v-if="!row.stocks.length" style="color:#c0c4cc;">-</span>
            <el-tag v-for="s in row.stocks" :key="s" size="mini" type="success" style="margin:2px;cursor:pointer;" @click="goToStock(s)">{{ s }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="相关度" width="80">
          <template slot-scope="{ row }">
            <el-tag v-if="row.relevance==='high'" size="mini" type="danger">高</el-tag>
            <el-tag v-else-if="row.relevance==='medium'" size="mini" type="warning">中</el-tag>
            <el-tag v-else size="mini">低</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 卡片视图 -->
    <el-row :gutter="20" v-if="viewMode === 'card'">
      <el-col :span="8" v-for="article in articles" :key="article.id" style="margin-bottom:16px;">
        <el-card shadow="hover" :body-style="{ padding: '16px' }">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <el-tag size="mini" :type="platformType(article.platform)">{{ article.platform }}</el-tag>
            <el-tag v-if="article.relevance==='high'" size="mini" type="danger">高相关</el-tag>
            <el-tag v-else-if="article.relevance==='medium'" size="mini" type="warning">中相关</el-tag>
          </div>
          <h4 style="margin:8px 0;font-size:14px;line-height:1.4;">
            <a v-if="article.url" :href="article.url" target="_blank" style="color:#303133;text-decoration:none;">{{ article.title }}</a>
            <span v-else>{{ article.title }}</span>
          </h4>
          <div style="color:#909399;font-size:12px;margin-bottom:8px;">{{ article.date }}</div>
          <div v-if="article.stocks.length > 0" style="margin-top:8px;">
            <el-tag v-for="s in article.stocks" :key="s" size="mini" type="success" style="margin:2px;">{{ s }}</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分页 -->
    <el-pagination v-if="total > 0" style="margin-top:16px;text-align:center;"
      layout="prev, pager, next, total" :total="total" :page-size="20"
      :current-page.sync="page" @current-change="fetchArticles" />

    <el-empty v-if="!loading && articles.length === 0" description="暂无文章数据" />
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Articles',
  data() {
    return {
      query: { date: '', keyword: '', platform: '', relevance: '', stock_only: false },
      articles: [],
      total: 0,
      page: 1,
      totalPages: 1,
      availableDates: [],
      platforms: ['微博', '头条', '百度', 'B站', '知乎', '抖音', '华尔街见闻', '澎湃', '36氪', '财联社', '凤凰新闻'],
      platformDist: [],
      loading: false,
      viewMode: 'table',
      stats: [
        { label: '文章总数', value: 0, color: '#409EFF' },
        { label: '股票相关', value: 0, color: '#67C23A' },
        { label: '今日新增', value: 0, color: '#E6A23C' },
        { label: '覆盖平台', value: 0, color: '#F56C6C' }
      ]
    }
  },
  created() { this.fetchArticles() },
  methods: {
    async fetchArticles() {
      this.loading = true
      try {
        const params = { page: this.page, per_page: 20, stock_only: this.query.stock_only ? 'true' : 'false' }
        if (this.query.date) params.date = this.query.date
        if (this.query.keyword) params.keyword = this.query.keyword
        if (this.query.platform) params.platform = this.query.platform
        if (this.query.relevance) params.relevance = this.query.relevance

        const res = await request.get('/articles', { params })
        if (res.code === 200) {
          this.articles = res.data || []
          this.total = res.total || 0
          this.totalPages = res.total_pages || 1
          this.availableDates = res.available_dates || []

          // 更新统计
          this.stats[0].value = res.total || 0
          this.stats[1].value = res.stock_related || 0
          this.stats[2].value = res.today_count || 0
          this.stats[3].value = res.platform_count || 0
          this.platformDist = res.platform_distribution || []
        }
      } catch (e) {
        console.error('获取文章失败:', e)
        this.$message.error('获取文章数据失败')
      } finally {
        this.loading = false
      }
    },
    resetQuery() {
      this.query = { date: '', keyword: '', platform: '', relevance: '', stock_only: false }
      this.page = 1
      this.fetchArticles()
    },
    platformType(platform) {
      const map = { '微博': '', '头条': 'success', '百度': 'warning', 'B站': 'danger', '知乎': 'info', '华尔街见闻': 'danger', '财联社': 'danger', '36氪': 'success' }
      return map[platform] || ''
    },
    goToStock(code) {
      this.$router.push(`/stock-detail?code=${code}`)
    }
  }
}
</script>
