<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>💼 股票池</span>
        <el-tag size="mini" style="float:right;">{{ stocks.length }} 只</el-tag>
      </div>
      <el-form :inline="true">
        <el-form-item label="搜索"><el-input v-model="keyword" size="small" placeholder="代码/名称" clearable @input="filterStocks" /></el-form-item>
        <el-form-item><el-button size="small" type="primary" @click="refresh">🔄 刷新</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="filtered" style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="代码" width="110" />
        <el-table-column prop="name" label="名称" width="80" />
        <el-table-column prop="price" label="最新价" width="80" />
        <el-table-column prop="change" label="涨跌幅" width="80">
          <template slot-scope="{ row }"><span :style="{ color: row.change > 0 ? '#67C23A' : '#F56C6C', fontWeight: 600 }">{{ row.change > 0 ? '+' : '' }}{{ row.change }}%</span></template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="100" />
        <el-table-column prop="group" label="分组" width="80" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Stocks',
  data() { return { stocks: [], filtered: [], keyword: '', loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/stocks')
        if (data.code === 200) {
          this.stocks = data.data.list || []
          this.filterStocks()
        }
      } catch (e) { this.$message.error('获取股票数据失败') }
      finally { this.loading = false }
    },
    filterStocks() {
      const kw = this.keyword.toLowerCase()
      this.filtered = kw ? this.stocks.filter(s => s.code.toLowerCase().includes(kw) || (s.name || '').includes(kw)) : this.stocks
    },
    async refresh() { this.fetchData() }
  }
}
</script>
