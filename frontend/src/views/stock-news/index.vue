<template>
  <div class="stock-news app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>📰 股票资讯聚合</span>
        <div style="float:right;">
          <el-input v-model="keyword" placeholder="搜索资讯..." size="mini" style="width:200px;margin-right:8px;" @keyup.enter.native="searchNews" />
          <el-button size="mini" type="primary" @click="refreshNews">🔄 刷新</el-button>
        </div>
      </div>
      
      <!-- 资讯分类 -->
      <el-tabs v-model="activeCategory" @tab-click="loadNews">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="公司公告" name="announcement" />
        <el-tab-pane label="行业新闻" name="industry" />
        <el-tab-pane label="研报" name="research" />
        <el-tab-pane label="市场动态" name="market" />
      </el-tabs>
    </el-card>

    <!-- 资讯列表 -->
    <el-card>
      <div v-for="news in filteredNews" :key="news.id" class="news-item">
        <div class="news-header">
          <h3 class="news-title" @click="viewNews(news)">{{ news.title }}</h3>
          <el-tag size="mini" :type="news.sentiment > 0 ? 'success' : news.sentiment < 0 ? 'danger' : 'info'">
            {{ news.sentiment > 0 ? '利好' : news.sentiment < 0 ? '利空' : '中性' }}
          </el-tag>
        </div>
        <p class="news-summary">{{ news.summary }}</p>
        <div class="news-footer">
          <span class="news-source">{{ news.source }}</span>
          <span class="news-date">{{ news.date }}</span>
          <span class="news-views">👁️ {{ news.views }}</span>
        </div>
      </div>
      
      <el-empty v-if="filteredNews.length === 0" description="暂无资讯" />
    </el-card>

    <!-- 资讯详情对话框 -->
    <el-dialog title="资讯详情" :visible.sync="newsDetailVisible" width="60%" top="5vh">
      <div v-if="selectedNews" class="news-detail">
        <h2>{{ selectedNews.title }}</h2>
        <div class="news-meta">
          <span>{{ selectedNews.source }}</span>
          <span>{{ selectedNews.date }}</span>
        </div>
        <div class="news-content" v-html="sanitizeHTML(selectedNews.content)"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import sanitizeMixin from '@/mixins/sanitize'
export default {
  mixins: [sanitizeMixin],
  name: 'StockNews',
  data() {
    return {
      keyword: '',
      activeCategory: 'all',
      news: [],
      newsDetailVisible: false,
      selectedNews: null
    }
  },
  computed: {
    filteredNews() {
      let news = this.news
      if (this.activeCategory !== 'all') {
        news = news.filter(n => n.category === this.activeCategory)
      }
      if (this.keyword) {
        news = news.filter(n => 
          n.title.toLowerCase().includes(this.keyword.toLowerCase()) ||
          n.summary.toLowerCase().includes(this.keyword.toLowerCase())
        )
      }
      return news
    }
  },
  created() { this.loadNews() },
  methods: {
    loadNews() {
      // 模拟资讯数据
      this.news = [
        {
          id: 1,
          title: '贵州茅台发布2026年Q1财报，业绩超预期',
          summary: '公司最新季度财报显示，营收和净利润均超过市场一致预期，毛利率同比提升2.3个百分点...',
          content: '<p>贵州茅台发布2026年第一季度财报，公司实现营收XXX亿元，同比增长XX%；净利润XXX亿元，同比增长XX%。毛利率达到XX%，同比提升2.3个百分点。</p><p>分析认为，公司业绩增长主要得益于产品结构优化和渠道改革...</p>',
          source: '财联社',
          date: '2026-04-18 14:30',
          category: 'announcement',
          sentiment: 0.8,
          views: 12580
        },
        {
          id: 2,
          title: '白酒行业分析：高端白酒需求持续增长',
          summary: '多家机构发布研报，一致看好高端白酒未来发展前景，维持行业推荐评级...',
          content: '<p>近期多家券商发布白酒行业研报，认为高端白酒需求持续增长，行业景气度 maintained...</p>',
          source: '证券时报',
          date: '2026-04-18 10:15',
          category: 'research',
          sentiment: 0.6,
          views: 8920
        },
        {
          id: 3,
          title: '新能源板块异动，多只股票涨停',
          summary: '受政策利好刺激，新能源板块今日表现强势，多只股票涨停...',
          content: '<p>今日新能源板块表现强势，受最新产业政策利好刺激，板块内多只股票涨停...</p>',
          source: '东方财富',
          date: '2026-04-18 09:30',
          category: 'market',
          sentiment: 0.7,
          views: 15620
        },
        {
          id: 4,
          title: '央行宣布降准0.25个百分点',
          summary: '为支持实体经济发展，央行决定下调金融机构存款准备金率0.25个百分点...',
          content: '<p>中国人民银行宣布，为支持实体经济发展，决定于2026年4月25日下调金融机构存款准备金率0.25个百分点...</p>',
          source: '新华社',
          date: '2026-04-17 18:00',
          category: 'market',
          sentiment: 0.5,
          views: 25800
        },
        {
          id: 5,
          title: '某科技公司获重大订单',
          summary: '公司今日公告，获得某大型国企重大订单，合同金额超过10亿元...',
          content: '<p>XX科技公司今日发布公告，公司与某大型国有企业签订重大合同，合同金额超过10亿元...</p>',
          source: '36氪',
          date: '2026-04-17 14:00',
          category: 'announcement',
          sentiment: 0.9,
          views: 9850
        }
      ]
    },
    
    searchNews() {
      // 搜索逻辑在 computed 中处理
    },
    
    refreshNews() {
      this.loadNews()
      this.$message.success('已刷新')
    },
    
    viewNews(news) {
      this.selectedNews = news
      this.newsDetailVisible = true
    }
  }
}
</script>

<style scoped>
.app-container {
  background: #0f0f1a;
  min-height: 100vh;
  padding: 16px;
}

.el-card {
  background: #1a1a2e !important;
  border: 1px solid #2a2a3e !important;
}

.el-card__header {
  border-bottom: 1px solid #2a2a3e !important;
}

.news-item {
  padding: 16px 0;
  border-bottom: 1px solid #2a2a3e;
}

.news-item:last-child {
  border-bottom: none;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.news-title {
  margin: 0;
  font-size: 16px;
  color: #d1d4dc;
  cursor: pointer;
}

.news-title:hover {
  color: #409EFF;
}

.news-summary {
  color: #909399;
  font-size: 13px;
  margin: 8px 0;
  line-height: 1.5;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  color: #606266;
  font-size: 12px;
}

.news-detail h2 {
  margin: 0 0 16px;
  color: #d1d4dc;
}

.news-meta {
  color: #909399;
  font-size: 13px;
  margin-bottom: 20px;
}

.news-meta span {
  margin-right: 16px;
}

.news-content {
  color: #d1d4dc;
  line-height: 1.8;
}
</style>
