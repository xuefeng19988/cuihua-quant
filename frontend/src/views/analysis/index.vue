<template>
  <div class="app-container">
    <!-- Search & Generate -->
    <el-card style="margin-bottom: 20px;">
      <el-form :inline="true">
        <el-form-item label="股票池">
          <el-select v-model="pool" style="width: 150px;">
            <el-option label="核心观察池" value="watchlist" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" icon="el-icon-search" @click="fetchData" :loading="loading">生成信号</el-button></el-form-item>
      </el-form>
    </el-card>

    <!-- Signals Table -->
    <el-card>
      <div slot="header"><span>🎯 交易信号 (Top 20)</span></div>
      <el-table :data="signals" style="width: 100%" v-loading="loading">
        <el-table-column label="排名" width="70">
          <template slot-scope="{ row }"><el-tag :type="row.rank <= 5 ? 'success' : 'warning'" size="small">#{{ row.rank }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="code" label="代码" width="100"><template slot-scope="{ row }"><el-tag size="small">{{ row.code }}</el-tag></template></el-table-column>
        <el-table-column prop="name" label="名称" width="80" />
        <el-table-column prop="close" label="收盘价" width="80" />
        <el-table-column label="综合得分" width="100">
          <template slot-scope="{ row }"><span :style="{ color: row.combined_score > 0 ? '#67C23A' : '#F56C6C', fontWeight: 600 }">{{ row.combined_score >= 0 ? '+' : '' }}{{ row.combined_score }}</span></template>
        </el-table-column>
        <el-table-column prop="tech_score" label="技术分" width="80" />
        <el-table-column prop="sentiment_score" label="情绪分" width="80" />
      </el-table>
      <el-empty v-if="signals.length === 0" description="点击"生成信号"开始分析" />
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Analysis',
  data() { return { signals: [], pool: 'watchlist', loading: false } },
  created() { this.fetchData() },
  methods: {
    fetchData() {
      this.loading = true
      fetch(`/api/signals?pool=${this.pool}`)
        .then(res => res.json())
        .then(data => {
          this.loading = false
          if (data.code === 200) this.signals = data.data.list || []
        })
        .catch(() => { this.loading = false })
    }
  }
}
</script>
