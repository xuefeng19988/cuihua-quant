<template>
  <div class="app-container">
    <!-- Add Stock -->
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>➕ 新增股票</span></div>
      <el-form :inline="true" @submit.native.prevent>
        <el-form-item label="代码"><el-input v-model="addForm.code" placeholder="如 HK.09988" style="width: 150px;" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="addForm.name" placeholder="如 阿里巴巴" style="width: 150px;" /></el-form-item>
        <el-form-item><el-button type="success" icon="el-icon-plus" @click="handleAdd">添加</el-button></el-form-item>
      </el-form>
    </el-card>

    <!-- Stock Table -->
    <el-card>
      <div slot="header">
        <span>📋 股票列表 ({{ total }})</span>
        <el-button size="mini" style="float: right;" icon="el-icon-refresh" @click="fetchData">刷新</el-button>
      </div>
      <el-table :data="stocks" style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="代码" width="110">
          <template slot-scope="{ row }"><el-tag size="small">{{ row.code }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column prop="price" label="最新价" width="90" />
        <el-table-column prop="change" label="涨跌幅" width="90">
          <template slot-scope="{ row }">
            <span :style="{ color: row.change > 0 ? '#67C23A' : row.change < 0 ? '#F56C6C' : '#909399', fontWeight: 600 }">
              {{ row.change > 0 ? '+' : '' }}{{ row.change }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template slot-scope="{ row }">
            <el-button size="mini" @click="$router.push('/trade/charts')">📉</el-button>
            <el-button size="mini" type="danger" @click="handleDelete(row.code)">🗑️</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top: 16px; text-align: center;"
        layout="prev, pager, next" :total="total" :page-size="10" :current-page.sync="page" @current-change="fetchData" />
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Stocks',
  data() {
    return { stocks: [], loading: false, total: 0, page: 1, addForm: { code: '', name: '' } }
  },
  created() { this.fetchData() },
  methods: {
    fetchData() {
      this.loading = true
      fetch(`/api/stocks?page=${this.page}`)
        .then(res => res.json())
        .then(data => {
          this.loading = false
          if (data.code === 200) {
            this.stocks = data.data.list || []
            this.total = data.data.total || 0
          }
        })
        .catch(() => { this.loading = false })
    },
    handleAdd() {
      if (!this.addForm.code) return this.$message.warning('请输入代码')
      fetch('/api/stocks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.addForm)
      })
      .then(res => res.json())
      .then(data => {
        if (data.code === 200) {
          this.$message.success('添加成功')
          this.addForm = { code: '', name: '' }
          this.fetchData()
        } else {
          this.$message.error(data.message || '添加失败')
        }
      })
    },
    handleDelete(code) {
      this.$confirm(`确定删除 ${code}?`, '提示', { type: 'warning' })
        .then(() => {
          fetch(`/api/stocks/${code}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
              if (data.code === 200) {
                this.$message.success('删除成功')
                this.fetchData()
              }
            })
        })
        .catch(() => {})
    }
  }
}
</script>
