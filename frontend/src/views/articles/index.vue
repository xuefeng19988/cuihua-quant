<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>📰 文章信息</span><el-tag size="mini" style="float:right;">{{ articles.length }} 篇</el-tag></div>
    </el-card>
    <el-row :gutter="20">
      <el-col :span="8" v-for="article in articles" :key="article.title">
        <el-card shadow="hover" style="margin-bottom:16px;cursor:pointer;" @click="viewArticle(article)">
          <div style="font-weight:600;margin-bottom:8px;">{{ article.title }}</div>
          <div style="color:#909399;font-size:12px;margin-bottom:8px;">{{ article.date }}</div>
          <el-tag v-for="t in article.tags" :key="t" size="mini" style="margin-right:4px;">{{ t }}</el-tag>
          <div style="margin-top:8px;font-size:13px;color:#606266;">{{ article.summary }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'Articles',
  data() {
    return {
      articles: [
        { title: 'AI大模型如何重塑量化交易', date: '2026-04-15', tags: ['AI', '量化'], summary: '探索AI大语言模型在量化选股、信号生成中的应用前景' },
        { title: '新能源赛道投资逻辑解析', date: '2026-04-12', tags: ['新能源', '赛道'], summary: '从政策、技术、市场三维度分析新能源投资机会' },
        { title: 'A股结构性行情下的配置策略', date: '2026-04-08', tags: ['策略', 'A股'], summary: '在市场分化中寻找确定性收益的配置方法' },
        { title: '半导体行业周期判断', date: '2026-04-05', tags: ['半导体', '周期'], summary: '全球半导体产业链分析与周期位置判断' },
        { title: '消费复苏的投资主线', date: '2026-04-01', tags: ['消费', '复苏'], summary: '后疫情时代消费板块的投资机会与风险' },
        { title: '港股科技股估值修复空间', date: '2026-03-28', tags: ['港股', '科技'], summary: '港股科技板块当前估值水平与修复路径分析' }
      ]
    }
  },
  methods: {
    viewArticle(article) { this.$message.info('查看: ' + article.title) }
  }
}
</script>
