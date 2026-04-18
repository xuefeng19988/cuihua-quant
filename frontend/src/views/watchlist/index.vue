<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>👁️ 自选股</span>
        <el-tag size="mini" style="float:right;">{{ watchlist.length }} 只</el-tag>
      </div>
      <el-form :inline="true">
        <el-form-item label="添加"><el-input v-model="newCode" size="small" placeholder="股票代码" style="width:130px;" /></el-form-item>
        <el-form-item><el-button size="small" type="primary" @click="addStock">➕ 添加</el-button></el-form-item>
        <el-form-item><el-button size="small" @click="refresh">🔄 刷新</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="watchlist" style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="代码" width="110" />
        <el-table-column prop="name" label="名称" width="80" />
        <el-table-column prop="price" label="最新价" width="80" />
        <el-table-column prop="change" label="涨跌幅" width="80">
          <template slot-scope="{ row }"><span :style="{ color: row.change > 0 ? '#67C23A' : '#F56C6C', fontWeight: 600 }">{{ row.change > 0 ? '+' : '' }}{{ row.change }}%</span></template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template slot-scope="{ row }"><el-button size="mini" type="danger" @click="removeStock(row.code)">🗑️</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Watchlist',
  data() { return { watchlist: [], newCode: '', loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/watchlist')
        if (data.code === 200) this.watchlist = data.data || []
      } catch (e) { this.$message.error('获取自选股失败') }
      finally { this.loading = false }
    },
    async addStock() {
      if (!this.newCode) return this.$message.warning('请输入股票代码')
      try {
        await request.post('/api/watchlist', { code: this.newCode })
        this.$message.success('添加成功')
        this.newCode = ''
        this.fetchData()
      } catch (e) { this.$message.error('添加失败') }
    },
    async removeStock(code) {
      try {
        await request.delete('/api/watchlist', { params: { code } })
        this.$message.success('已删除')
        this.fetchData()
      } catch (e) { this.$message.error('删除失败') }
    },
    refresh() { this.fetchData() }
  }
}
</script>
