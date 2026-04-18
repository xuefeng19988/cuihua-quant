<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>⭐ 自选股</span>
        <div style="float:right;display:flex;gap:8px;align-items:center;">
          <el-radio-group v-model="viewMode" size="mini">
            <el-radio-button label="table">表格</el-radio-button>
            <el-radio-button label="card">卡片</el-radio-button>
          </el-radio-group>
          <el-button size="mini" type="primary" @click="showAddDialog">➕ 添加</el-button>
          <el-button size="mini" @click="refresh" :loading="loading">🔄 刷新</el-button>
        </div>
      </div>
      <el-form :inline="true" size="small">
        <el-form-item label="分组"><el-select v-model="filterGroup" placeholder="全部分组" clearable style="width:140px;" @change="filterWatchlist"><el-option v-for="g in groups" :key="g" :label="g" :value="g" /></el-select></el-form-item>
        <el-form-item label="排序"><el-select v-model="sortBy" style="width:120px;" @change="sortWatchlist"><el-option label="涨跌幅" value="change" /><el-option label="代码" value="code" /><el-option label="名称" value="name" /></el-select></el-form-item>
        <el-form-item><el-button size="small" @click="exportWatchlist">📤 导出</el-button></el-form-item>
      </el-form>
    </el-card>

    <!-- 组合概览 -->
    <el-row :gutter="16" style="margin-bottom:20px;">
      <el-col :span="6"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;font-size:12px;">自选总数</div><div style="font-size:24px;font-weight:600;">{{ watchlist.length }}</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;font-size:12px;">上涨</div><div style="font-size:24px;font-weight:600;color:#26a69a;">{{ upCount }}</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;font-size:12px;">下跌</div><div style="font-size:24px;font-weight:600;color:#ef5350;">{{ downCount }}</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;font-size:12px;">平均涨跌幅</div><div style="font-size:24px;font-weight:600;" :style="{color: avgChange >= 0 ? '#26a69a' : '#ef5350'}">{{ avgChange >= 0 ? '+' : '' }}{{ avgChange }}%</div></el-card></el-col>
    </el-row>

    <!-- 表格视图 -->
    <el-card v-if="viewMode === 'table'">
      <el-table :data="filteredWatchlist" style="width:100%" v-loading="loading" stripe @row-click="goToDetail">
        <el-table-column prop="code" label="代码" width="110" />
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column prop="price" label="最新价" width="90" />
        <el-table-column prop="change" label="涨跌幅" width="90">
          <template slot-scope="{ row }"><span :style="{ color: row.change > 0 ? '#26a69a' : row.change < 0 ? '#ef5350' : '#909399', fontWeight: 600 }">{{ row.change > 0 ? '+' : '' }}{{ row.change }}%</span></template>
        </el-table-column>
        <el-table-column label="涨跌额" width="90"><template slot-scope="{ row }"><span :style="{color: row.changeAmount >= 0 ? '#26a69a' : '#ef5350'}">{{ row.changeAmount >= 0 ? '+' : '' }}{{ row.changeAmount?.toFixed(2) || '-' }}</span></template></el-table-column>
        <el-table-column prop="volume" label="成交量" width="100"><template slot-scope="{ row }">{{ (row.volume/10000).toFixed(0) }}万</template></el-table-column>
        <el-table-column prop="group" label="分组" width="80"><template slot-scope="{ row }"><el-tag size="mini" :type="row.group === '核心' ? 'danger' : 'info'">{{ row.group || '默认' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template slot-scope="{ row }">
            <el-button size="mini" @click.stop="goToDetail(row)">详情</el-button>
            <el-button size="mini" type="danger" @click.stop="removeStock(row)">🗑️</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 卡片视图 -->
    <el-row :gutter="16" v-else>
      <el-col :span="6" v-for="stock in filteredWatchlist" :key="stock.code" style="margin-bottom:16px;">
        <el-card shadow="hover" class="stock-card" @click.native="goToDetail(stock)">
          <div class="card-header">
            <div><h4 class="stock-name">{{ stock.name }}</h4><span class="stock-code">{{ stock.code }}</span></div>
            <el-tag size="mini" :type="stock.group === '核心' ? 'danger' : stock.group === '港股' ? 'warning' : 'info'">{{ stock.group || '默认' }}</el-tag>
          </div>
          <div class="card-price" :class="stock.change >= 0 ? 'up' : 'down'">
            <div class="price-value">{{ stock.price || '-' }}</div>
            <div class="price-change">{{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%</div>
          </div>
          <div class="card-footer">
            <span>量: {{ (stock.volume/10000).toFixed(0) }}万</span>
            <el-button size="mini" type="danger" icon="el-icon-delete" circle @click.stop="removeStock(stock)"></el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加对话框 -->
    <el-dialog title="添加自选股" :visible.sync="addDialogVisible" width="400px">
      <el-form :model="newStock" label-width="80px">
        <el-form-item label="股票代码"><el-input v-model="newStock.code" placeholder="如 SH.600519" /></el-form-item>
        <el-form-item label="股票名称"><el-input v-model="newStock.name" placeholder="如 贵州茅台" /></el-form-item>
        <el-form-item label="分组"><el-select v-model="newStock.group" style="width:100%;"><el-option label="核心" value="核心" /><el-option label="观察" value="观察" /><el-option label="港股" value="港股" /></el-select></el-form-item>
      </el-form>
      <span slot="footer"><el-button @click="addDialogVisible = false">取消</el-button><el-button type="primary" @click="addStock" :loading="adding">确认</el-button></span>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Watchlist',
  data() {
    return {
      watchlist: [],
      filterGroup: '',
      sortBy: 'change',
      viewMode: 'card',
      loading: false,
      adding: false,
      addDialogVisible: false,
      newStock: { code: '', name: '', group: '观察' },
      groups: ['核心', '观察', '港股']
    }
  },
  computed: {
    filteredWatchlist() {
      let list = this.watchlist
      if (this.filterGroup) list = list.filter(s => s.group === this.filterGroup)
      if (this.sortBy === 'change') list = [...list].sort((a, b) => b.change - a.change)
      else if (this.sortBy === 'code') list = [...list].sort((a, b) => a.code.localeCompare(b.code))
      else if (this.sortBy === 'name') list = [...list].sort((a, b) => a.name.localeCompare(b.name))
      return list
    },
    upCount() { return this.watchlist.filter(s => s.change > 0).length },
    downCount() { return this.watchlist.filter(s => s.change < 0).length },
    avgChange() { return this.watchlist.length > 0 ? (this.watchlist.reduce((sum, s) => sum + s.change, 0) / this.watchlist.length).toFixed(2) : 0 }
  },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/watchlist')
        if (data.code === 200) this.watchlist = data.data.stocks || this.watchlist
      } catch (e) { this.$message.error('刷新失败') }
      finally { this.loading = false }
    },
    filterWatchlist() {},
    sortWatchlist() {},
    showAddDialog() { this.newStock = { code: '', name: '', group: '观察' }; this.addDialogVisible = true },
    async addStock() {
      if (!this.newStock.code) return this.$message.warning('请输入代码')
      try {
        await request.post('/api/watchlist', this.newStock)
        this.$message.success('添加成功')
        this.watchlist.push({ ...this.newStock, price: 0, change: 0, volume: 0 })
        this.addDialogVisible = false
      } catch (e) { this.$message.error('添加失败') }
    },
    async removeStock(stock) {
      try {
        await request.delete('/api/watchlist', { params: { code: stock.code } })
        this.watchlist = this.watchlist.filter(s => s.code !== stock.code)
        this.$message.success('已移除')
      } catch (e) { this.$message.error('移除失败') }
    },
    goToDetail(stock) { this.$router.push(`/stock-detail/${stock.code}`) },
    async exportWatchlist() {
      const csv = 'code,name,price,change,group\n' + this.watchlist.map(s => `${s.code},${s.name},${s.price},${s.change},${s.group || ''}`).join('\n')
      const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `watchlist_${new Date().toISOString().slice(0,10)}.csv`
      link.click()
      this.$message.success(`已导出 ${this.watchlist.length} 只自选股`)
    },
    async refresh() { this.fetchData() }
  }
}
</script>

<style scoped>
.app-container { background: #0f0f1a; min-height: 100vh; padding: 16px; }
.el-card { background: #1a1a2e !important; border: 1px solid #2a2a3e !important; }
.el-card__header { border-bottom: 1px solid #2a2a3e !important; }

.stock-card { cursor: pointer; transition: transform 0.2s; }
.stock-card:hover { transform: translateY(-4px); }

.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.stock-name { margin: 0; font-size: 16px; color: #d1d4dc; }
.stock-code { color: #909399; font-size: 12px; }

.card-price { text-align: center; padding: 16px 0; border-top: 1px solid #2a2a3e; border-bottom: 1px solid #2a2a3e; }
.price-value { font-size: 24px; font-weight: 700; }
.price-change { font-size: 14px; margin-top: 4px; }
.card-price.up .price-value { color: #26a69a; }
.card-price.down .price-value { color: #ef5350; }
.card-price.up .price-change { color: #26a69a; }
.card-price.down .price-change { color: #ef5350; }

.card-footer { display: flex; justify-content: space-between; padding: 8px 0; color: #909399; font-size: 12px; }
</style>
