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

    <!-- 卡片视图 -->
    <el-row :gutter="20" v-if="viewMode === 'card'">
      <el-col :span="8" v-for="article in articles" :key="article.id" style="margin-bottom:20px;">
        <el-card shadow="hover" :body-style="{ padding: '0' }" class="article-card">
          <!-- 封面图 -->
          <div class="article-cover" @click="editArticle(article)" :style="{ backgroundImage: article.cover_url ? `url(${article.cover_url})` : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }">
            <div class="cover-overlay">
              <el-tag v-if="article.is_top" size="mini" type="danger" style="margin-bottom:4px;">📌 置顶</el-tag>
              <el-tag :type="article.status === 'published' ? 'success' : 'info'" size="mini">
                {{ article.status === 'published' ? '已发布' : '草稿' }}
              </el-tag>
            </div>
          </div>
          
          <!-- 内容 -->
          <div style="padding:16px;">
            <h3 @click="editArticle(article)" style="margin:0 0 8px;font-size:16px;cursor:pointer;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
              {{ article.title }}
            </h3>
            <p v-if="article.subtitle" style="color:#909399;font-size:12px;margin:0 0 8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
              {{ article.subtitle }}
            </p>
            
            <!-- 标签 -->
            <div style="margin-bottom:8px;">
              <el-tag v-for="t in article.tags" :key="t" size="mini" style="margin:2px;">{{ t }}</el-tag>
            </div>
            
            <!-- 底部信息 -->
            <div style="display:flex;justify-content:space-between;align-items:center;color:#909399;font-size:12px;">
              <div>
                <span>👁️ {{ article.views }}</span>
                <span style="margin-left:8px;">❤️ {{ article.likes }}</span>
              </div>
              <div style="display:flex;gap:4px;">
                <el-button size="mini" icon="el-icon-edit" @click="editArticle(article)" circle></el-button>
                <el-button size="mini" icon="el-icon-delete" type="danger" @click="deleteArticle(article)" circle></el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 列表视图 -->
    <el-card v-else>
      <el-table :data="articles" style="width:100%" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="封面" width="80">
          <template slot-scope="{ row }">
            <div v-if="row.cover_url" style="width:60px;height:40px;background-size:cover;background-position:center;border-radius:4px;" :style="{ backgroundImage: `url(${row.cover_url})` }"></div>
            <div v-else style="width:60px;height:40px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:4px;"></div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column label="标签" width="150"><template slot-scope="{ row }"><el-tag v-for="t in row.tags" :key="t" size="mini" style="margin:2px;">{{ t }}</el-tag></template></el-table-column>
        <el-table-column label="状态" width="80"><template slot-scope="{ row }"><el-tag :type="row.status === 'published' ? 'success' : 'info'" size="mini">{{ row.status === 'published' ? '已发布' : '草稿' }}</el-tag></template></el-table-column>
        <el-table-column prop="views" label="浏览" width="70" />
        <el-table-column prop="likes" label="点赞" width="70" />
        <el-table-column prop="updated_at" label="更新时间" width="160"><template slot-scope="{ row }">{{ new Date(row.updated_at).toLocaleString('zh-CN') }}</template></el-table-column>
        <el-table-column label="操作" width="200" fixed="right"><template slot-scope="{ row }"><el-button size="mini" @click="editArticle(row)">✏️</el-button><el-button size="mini" type="warning" @click="aiAnalyze(row)">🤖 AI</el-button><el-button size="mini" type="success" @click="togglePublish(row)" v-if="row.status === 'draft'">🚀</el-button><el-button size="mini" type="danger" @click="deleteArticle(row)">🗑️</el-button></template></el-table-column>
      </el-table>
    </el-card>

    <!-- 分页 -->
    <el-pagination v-if="total > 10" style="margin-top:16px;text-align:center;" layout="prev, pager, next, total" :total="total" :page-size="10" :current-page.sync="page" @current-change="fetchArticles" />

    <el-empty v-if="articles.length === 0 && !loading" description="暂无笔记">
      <el-button type="primary" @click="createArticle">创建第一篇笔记</el-button>
    </el-empty>
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
      loading: false, viewMode: 'card',
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
        const { data } = await request.get('/articles', { params: { page: this.page, per_page: 10, ...this.query } })
        if (data.code === 200) { this.articles = data.data.articles; this.total = data.data.total; this.stats = data.data.stats || this.stats }
      } catch (e) { this.$message.error('获取笔记失败') }
      finally { this.loading = false }
    },
    aiAnalyze(note) {
      this.$router.push({ path: '/ai-center/note', query: { id: note.id, title: note.title } })
    },
    async fetchTags() {
      try { const { data } = await request.get('/notes/tags'); if (data.code === 200) this.tags = data.data.tags || [] } catch (e) {}
    },
    createArticle() { this.$router.push('/note-editor') },
    editArticle(article) { this.$router.push(`/note-editor/${article.id}`) },
    async togglePublish(article) {
      try { await request.put(`/articles/${article.id}`, { status: 'published' }); this.$message.success('已发布'); this.fetchArticles() }
      catch (e) { this.$message.error('发布失败') }
    },
    async deleteArticle(article) {
      try { await this.$confirm(`确定删除"${article.title}"？`, '提示', { type: 'warning' }); await request.delete(`/articles/${article.id}`); this.$message.success('删除成功'); this.fetchArticles() } catch (e) {}
    },
    resetQuery() { this.query = { status: '', category: '', tag: '', keyword: '' }; this.page = 1; this.fetchArticles() }
  }
}
</script>

<style scoped>
.app-container { background: #0f0f1a; min-height: 100vh; padding: 16px; }
.el-card { background: #1a1a2e !important; border: 1px solid #2a2a3e !important; }
.el-card__header { border-bottom: 1px solid #2a2a3e !important; }

/* 卡片视图 */
.article-card { cursor: pointer; transition: transform 0.2s; }
.article-card:hover { transform: translateY(-4px); }

.article-cover {
  height: 140px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.cover-overlay {
  position: absolute;
  top: 0; left: 0; right: 0;
  padding: 12px;
  background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, transparent 100%);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
</style>
