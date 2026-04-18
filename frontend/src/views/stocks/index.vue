<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>💼 股票池</span>
        <div style="float:right;">
          <el-tag size="mini">{{ filtered.length }} 只</el-tag>
          <el-button size="mini" type="primary" @click="showAddDialog" style="margin-left:8px;">➕ 添加</el-button>
        </div>
      </div>
      <el-form :inline="true">
        <el-form-item label="分组">
          <el-select v-model="filterGroup" size="small" placeholder="全部分组" clearable @change="filterStocks" style="width:150px;">
            <el-option v-for="(g, id) in groups" :key="id" :label="g.name" :value="id" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="keyword" size="small" placeholder="代码/名称" clearable @input="filterStocks" style="width:200px;" />
        </el-form-item>
        <el-form-item><el-button size="small" @click="refresh">🔄 刷新</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="filtered" style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="代码" width="120" />
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column prop="price" label="最新价" width="90" />
        <el-table-column prop="change" label="涨跌幅" width="90">
          <template slot-scope="{ row }"><span :style="{ color: row.change > 0 ? '#67C23A' : '#F56C6C', fontWeight: 600 }">{{ row.change > 0 ? '+' : '' }}{{ row.change }}%</span></template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="100" />
        <el-table-column label="分组" width="120">
          <template slot-scope="{ row }">
            <el-tag v-for="g in row.groups" :key="g" size="mini" style="margin:2px;">{{ g }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template slot-scope="{ row }">
            <el-button size="mini" type="danger" @click="deleteStock(row.code)">🗑️</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:16px;text-align:center;"
        layout="prev, pager, next" :total="total" :page-size="10"
        :current-page.sync="page" @current-change="fetchData" />
    </el-card>

    <!-- 添加股票对话框 -->
    <el-dialog title="添加股票" :visible.sync="addDialogVisible" width="400px">
      <el-form :model="newStock" label-width="80px">
        <el-form-item label="股票代码"><el-input v-model="newStock.code" placeholder="如 SH.600519" /></el-form-item>
        <el-form-item label="股票名称"><el-input v-model="newStock.name" placeholder="如 贵州茅台" /></el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addStock" :loading="adding">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Stocks',
  data() {
    return {
      stocks: [],
      filtered: [],
      groups: {},
      filterGroup: '',
      keyword: '',
      total: 0,
      page: 1,
      loading: false,
      addDialogVisible: false,
      adding: false,
      newStock: { code: '', name: '' }
    }
  },
  created() { this.fetchData(); this.fetchGroups() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/stocks', { params: { page: this.page } })
        if (data.code === 200) {
          this.stocks = (data.data.list || []).map(s => ({ ...s, groups: ['watchlist'] }))
          this.total = data.data.total || 0
          this.filterStocks()
        }
      } catch (e) { this.$message.error('获取股票数据失败') }
      finally { this.loading = false }
    },
    async fetchGroups() {
      try {
        const { data } = await request.get('/api/stock-groups')
        if (data.code === 200) {
          this.groups = data.data.groups || {}
        }
      } catch (e) {}
    },
    filterStocks() {
      let list = this.stocks
      // 分组筛选
      if (this.filterGroup && this.groups[this.filterGroup]) {
        const groupCodes = this.groups[this.filterGroup].stocks || []
        list = list.filter(s => groupCodes.includes(s.code))
      }
      // 关键词搜索
      const kw = this.keyword.toLowerCase()
      if (kw) {
        list = list.filter(s => s.code.toLowerCase().includes(kw) || (s.name || '').includes(kw))
      }
      this.filtered = list
    },
    showAddDialog() { this.newStock = { code: '', name: '' }; this.addDialogVisible = true },
    async addStock() {
      if (!this.newStock.code) return this.$message.warning('请输入股票代码')
      this.adding = true
      try {
        await request.post('/api/stocks', this.newStock)
        this.$message.success('添加成功')
        this.addDialogVisible = false
        this.fetchData()
      } catch (e) { this.$message.error('添加失败') }
      finally { this.adding = false }
    },
    async deleteStock(code) {
      try {
        await request.delete(`/api/stocks/${code}`)
        this.$message.success('已删除')
        this.fetchData()
      } catch (e) { this.$message.error('删除失败') }
    },
    async refresh() { this.fetchData() }
  }
}
</script>
