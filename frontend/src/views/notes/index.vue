<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>📝 笔记管理</span>
        <div style="float:right;">
          <el-radio-group v-model="viewMode" size="mini" style="margin-right:12px;">
            <el-radio-button label="card">卡片</el-radio-button>
            <el-radio-button label="list">列表</el-radio-button>
          </el-radio-group>
          <el-button type="primary" @click="createArticle">➕ 新建笔记</el-button>
        </div>
      </div>
      <el-form :inline="true" size="small">
        <el-form-item label="状态"><el-select v-model="query.status" placeholder="全部" clearable style="width:100px;" @change="fetchArticles"><el-option label="草稿" value="draft" /><el-option label="已发布" value="published" /></el-select></el-form-item>
        <el-form-item label="分类"><el-select v-model="query.category" placeholder="全部分类" clearable style="width:140px;" @change="fetchArticles"><el-option v-for="c in stats.categories" :key="c" :label="c" :value="c" /></el-select></el-form-item>
        <el-form-item label="标签"><el-select v-model="query.tag" placeholder="全部标签" clearable style="width:140px;" @change="fetchArticles"><el-option v-for="t in tags" :key="t" :label="t" :value="t" /></el-select></el-form-item>
        <el-form-item label="关键词"><el-input v-model="query.keyword" placeholder="搜索标题..." clearable style="width:200px;" @keyup.enter.native="fetchArticles" /></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchArticles">🔍 查询</el-button><el-button @click="resetQuery">重置</el-button></el-form-item>
      </el-form>
    </el-card>

    <!-- 图表区 -->
    <el-row :gutter="20" style="margin-bottom:20px;">
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>🥧 笔记分类占比</span></div>
          <pie-chart :data="categoryData" title="分类分布" :height="250" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📈 发布趋势</span></div>
          <line-chart :categories="publishCategories" :series="publishSeries" title="月度发布量" :height="250" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>☁️ 热门标签</span></div>
          <word-cloud :words="tagWords" title="标签云" :height="250" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 笔记列表 -->
    <el-card>
      <el-table :data="articles" style="width:100%" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column label="标签" width="150"><template slot-scope="{ row }"><el-tag v-for="t in row.tags" :key="t" size="mini" style="margin:2px;">{{ t }}</el-tag></template></el-table-column>
        <el-table-column label="状态" width="80"><template slot-scope="{ row }"><el-tag :type="row.status === 'published' ? 'success' : 'info'" size="mini">{{ row.status === 'published' ? '已发布' : '草稿' }}</el-tag></template></el-table-column>
        <el-table-column prop="views" label="浏览" width="70" />
        <el-table-column prop="likes" label="点赞" width="70" />
        <el-table-column prop="updated_at" label="更新时间" width="160"><template slot-scope="{ row }">{{ new Date(row.updated_at).toLocaleString('zh-CN') }}</template></el-table-column>
        <el-table-column label="操作" width="150" fixed="right"><template slot-scope="{ row }"><el-button size="mini" @click="editArticle(row)">✏️</el-button><el-button size="mini" type="success" @click="togglePublish(row)" v-if="row.status === 'draft'">🚀</el-button><el-button size="mini" type="danger" @click="deleteArticle(row)">🗑️</el-button></template></el-table-column>
      </el-table>
      <el-pagination style="margin-top:16px;text-align:center;" layout="prev, pager, next, total" :total="total" :page-size="10" :current-page.sync="page" @current-change="fetchArticles" />
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
import { PieChart, LineChart, WordCloud } from '@/components/charts'

export default {
  name: 'Notes',
  components: { PieChart, LineChart, WordCloud },
  data() {
    return {
      articles: [], total: 0, page: 1, tags: [],
      query: { status: '', category: '', tag: '', keyword: '' },
      loading: false, viewMode: 'list',
      stats: { total: 0, draft: 0, published: 0, total_views: 0, categories: [] },
      publishCategories: ['1月', '2月', '3月', '4月', '5月', '6月'],
      publishSeries: [{ name: '发布量', data: [5, 8, 12, 15, 10, 18], color: '#409EFF' }],
      tagWords: [
        { name: '量化', value: 50 }, { name: '策略', value: 45 }, { name: 'Python', value: 40 },
        { name: 'AI', value: 38 }, { name: '机器学习', value: 35 }, { name: 'A股', value: 30 },
        { name: '港股', value: 28 }, { name: '技术分析', value: 25 }, { name: '基本面', value: 22 },
        { name: '风控', value: 20 }, { name: '回测', value: 18 }, { name: '情绪', value: 15 }
      ]
    }
  },
  computed: {
    categoryData() {
      const cats = {}
      this.articles.forEach(a => {
        const c = a.category || '未分类'
        cats[c] = (cats[c] || 0) + 1
      })
      const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
      return Object.entries(cats).map(([name, value], i) => ({ name, value, itemStyle: { color: colors[i % colors.length] } }))
    }
  },
  created() { this.fetchArticles(); this.fetchTags() },
  methods: {
    async fetchArticles() {
      this.loading = true
      try {
        const { data } = await request.get('/api/articles', { params: { page: this.page, per_page: 10, ...this.query } })
        if (data.code === 200) { this.articles = data.data.articles; this.total = data.data.total; this.stats = data.data.stats || this.stats }
      } catch (e) { this.$message.error('获取笔记失败') }
      finally { this.loading = false }
    },
    async fetchTags() {
      try { const { data } = await request.get('/api/notes/tags'); if (data.code === 200) this.tags = data.data.tags || [] } catch (e) {}
    },
    createArticle() { this.$router.push('/note-editor') },
    editArticle(article) { this.$router.push(`/note-editor/${article.id}`) },
    async togglePublish(article) {
      try { await request.put(`/api/articles/${article.id}`, { status: 'published' }); this.$message.success('已发布'); this.fetchArticles() }
      catch (e) { this.$message.error('发布失败') }
    },
    async deleteArticle(article) {
      try { await this.$confirm(`确定删除"${article.title}"？`, '提示', { type: 'warning' }); await request.delete(`/api/articles/${article.id}`); this.$message.success('删除成功'); this.fetchArticles() } catch (e) {}
    },
    resetQuery() { this.query = { status: '', category: '', tag: '', keyword: '' }; this.page = 1; this.fetchArticles() }
  }
}
</script>
