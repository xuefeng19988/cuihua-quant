<template>
  <div class="stock-pool-enhanced">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>💼 股票池</span>
        <div style="float:right;display:flex;gap:8px;align-items:center;">
          <el-radio-group v-model="viewMode" size="mini">
            <el-radio-button label="table">表格</el-radio-button>
            <el-radio-button label="card">卡片</el-radio-button>
          </el-radio-group>
          <el-button size="mini" type="primary" @click="showAddDialog">➕ 添加</el-button>
          <el-button size="mini" @click="batchImport">📥 导入</el-button>
          <el-button size="mini" @click="batchExport">📤 导出</el-button>
        </div>
      </div>
      
      <!-- 筛选栏 -->
      <el-form :inline="true" size="small">
        <el-form-item label="板块">
          <el-select v-model="filterSector" placeholder="全部板块" clearable style="width:140px;" @change="filterStocks">
            <el-option label="全部" value="" />
            <el-option label="白酒" value="白酒" />
            <el-option label="新能源" value="新能源" />
            <el-option label="金融" value="金融" />
            <el-option label="科技" value="科技" />
            <el-option label="医药" value="医药" />
            <el-option label="消费" value="消费" />
          </el-select>
        </el-form-item>
        <el-form-item label="市场">
          <el-select v-model="filterMarket" placeholder="全部市场" clearable style="width:120px;" @change="filterStocks">
            <el-option label="全部" value="" />
            <el-option label="A股" value="A" />
            <el-option label="港股" value="HK" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-select v-model="sortBy" style="width:120px;" @change="sortStocks">
            <el-option label="涨跌幅" value="change" />
            <el-option label="代码" value="code" />
            <el-option label="名称" value="name" />
            <el-option label="成交量" value="volume" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="searchKeyword" placeholder="代码/名称" clearable style="width:160px;" @input="filterStocks" />
        </el-form-item>
        <el-form-item><el-button @click="refresh">🔄 刷新</el-button></el-form-item>
      </el-form>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom:20px;">
      <el-col :span="6">
        <el-card shadow="hover" style="text-align:center;">
          <div style="color:#909399;font-size:12px;">股票总数</div>
          <div style="font-size:24px;font-weight:600;color:#409EFF;">{{ filteredStocks.length }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" style="text-align:center;">
          <div style="color:#909399;font-size:12px;">上涨</div>
          <div style="font-size:24px;font-weight:600;color:#26a69a;">{{ upCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" style="text-align:center;">
          <div style="color:#909399;font-size:12px;">下跌</div>
          <div style="font-size:24px;font-weight:600;color:#ef5350;">{{ downCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" style="text-align:center;">
          <div style="color:#909399;font-size:12px;">平均涨跌幅</div>
          <div style="font-size:24px;font-weight:600;" :style="{color: avgChange >= 0 ? '#26a69a' : '#ef5350'}">{{ avgChange >= 0 ? '+' : '' }}{{ avgChange }}%</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16" style="margin-bottom:20px;">
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📊 涨跌分布</span></div>
          <pie-chart :data="changeDistribution" title="涨/平/跌" :height="250" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>🥧 行业占比</span></div>
          <pie-chart :data="sectorDistribution" title="行业分布" :height="250" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📈 成交量 Top10</span></div>
          <bar-chart :data="topVolumeData" :categories="topVolumeCategories" title="成交量排行" :height="250" :horizontal="true" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 表格视图 -->
    <el-card v-if="viewMode === 'table'">
      <el-table :data="pagedStocks" style="width:100%" v-loading="loading" stripe @row-click="goToDetail">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="code" label="代码" width="110" />
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column prop="price" label="最新价" width="90" />
        <el-table-column prop="change" label="涨跌幅" width="90">
          <template slot-scope="{ row }">
            <span :style="{ color: row.change > 0 ? '#26a69a' : row.change < 0 ? '#ef5350' : '#909399', fontWeight: 600 }">{{ row.change > 0 ? '+' : '' }}{{ row.change }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="100"><template slot-scope="{ row }">{{ (row.volume/10000).toFixed(0) }}万</template></el-table-column>
        <el-table-column prop="sector" label="板块" width="80" />
        <el-table-column label="操作" width="180" fixed="right">
          <template slot-scope="{ row }">
            <el-button size="mini" @click.stop="goToDetail(row)">详情</el-button>
            <el-button size="mini" type="warning" @click.stop="aiAnalyze(row)">🤖 AI</el-button>
            <el-button size="mini" type="danger" @click.stop="removeStock(row)">🗑️</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:16px;text-align:center;" layout="prev, pager, next" :total="filteredStocks.length" :page-size="pageSize" :current-page.sync="currentPage" />
    </el-card>

    <!-- 卡片视图 -->
    <el-row :gutter="16" v-else>
      <el-col :span="6" v-for="stock in pagedStocks" :key="stock.code" style="margin-bottom:16px;">
        <el-card shadow="hover" class="stock-card" @click.native="goToDetail(stock)">
          <div class="card-header">
            <div>
              <h4 class="stock-name">{{ stock.name }}</h4>
              <span class="stock-code">{{ stock.code }}</span>
            </div>
            <el-tag size="mini" :type="stock.sector === '白酒' ? 'danger' : stock.sector === '新能源' ? 'success' : 'info'">{{ stock.sector }}</el-tag>
          </div>
          <div class="card-price" :class="stock.change >= 0 ? 'up' : 'down'">
            <div class="price-value">{{ stock.price }}</div>
            <div class="price-change">{{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%</div>
          </div>
          <div class="card-footer">
            <span>量: {{ (stock.volume/10000).toFixed(0) }}万</span>
            <el-button size="mini" type="danger" icon="el-icon-delete" circle @click.stop="removeStock(stock)"></el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加股票对话框 -->
    <el-dialog title="添加股票" :visible.sync="addDialogVisible" width="400px">
      <el-form :model="newStock" label-width="80px">
        <el-form-item label="股票代码"><el-input v-model="newStock.code" placeholder="如 SH.600519" /></el-form-item>
        <el-form-item label="股票名称"><el-input v-model="newStock.name" placeholder="如 贵州茅台" /></el-form-item>
        <el-form-item label="所属板块">
          <el-select v-model="newStock.sector" style="width:100%;">
            <el-option label="白酒" value="白酒" />
            <el-option label="新能源" value="新能源" />
            <el-option label="金融" value="金融" />
            <el-option label="科技" value="科技" />
            <el-option label="医药" value="医药" />
            <el-option label="消费" value="消费" />
          </el-select>
        </el-form-item>
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
import { PieChart, BarChart } from '@/components/charts'

export default {
  name: 'StockPoolEnhanced',
  components: { PieChart, BarChart },
  data() {
    return {
      stocks: [],
      filteredStocks: [],
      pagedStocks: [],
      viewMode: 'table',
      filterSector: '',
      filterMarket: '',
      sortBy: 'change',
      searchKeyword: '',
      loading: false,
      adding: false,
      currentPage: 1,
      pageSize: 10,
      addDialogVisible: false,
      newStock: { code: '', name: '', sector: '' }
    }
  },
  computed: {
    upCount() { return this.filteredStocks.filter(s => s.change > 0).length },
    downCount() { return this.filteredStocks.filter(s => s.change < 0).length },
    avgChange() {
      if (this.filteredStocks.length === 0) return 0
      return (this.filteredStocks.reduce((sum, s) => sum + s.change, 0) / this.filteredStocks.length).toFixed(2)
    },
    changeDistribution() {
      return [
        { value: this.upCount, name: '上涨', itemStyle: { color: '#26a69a' } },
        { value: this.filteredStocks.length - this.upCount - this.downCount, name: '平盘', itemStyle: { color: '#909399' } },
        { value: this.downCount, name: '下跌', itemStyle: { color: '#ef5350' } }
      ]
    },
    sectorDistribution() {
      const sectors = {}
      this.filteredStocks.forEach(s => {
        const sec = s.sector || '其他'
        sectors[sec] = (sectors[sec] || 0) + 1
      })
      const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
      return Object.entries(sectors).map(([name, value], i) => ({
        name, value, itemStyle: { color: colors[i % colors.length] }
      }))
    },
    topVolumeData() {
      return [...this.filteredStocks].sort((a, b) => b.volume - a.volume).slice(0, 10).map(s => s.volume)
    },
    topVolumeCategories() {
      return [...this.filteredStocks].sort((a, b) => b.volume - a.volume).slice(0, 10).map(s => s.name)
    }
  },
  created() { this.fetchStocks() },
  watch: {
    currentPage() { this.updatePagedStocks() },
    filteredStocks() { this.updatePagedStocks() }
  },
  methods: {
    async fetchStocks() {
      this.loading = true
      try {
        const { data } = await request.get('/stocks')
        if (data.code === 200) {
          this.stocks = (data.data.list || []).map(s => ({
            ...s,
            sector: this.getSector(s.code),
            market: s.code.startsWith('HK.') ? 'HK' : 'A'
          }))
          this.filterStocks()
        }
      } catch (e) { this.$message.error('获取股票数据失败') }
      finally { this.loading = false }
    },
    getSector(code) {
      const map = {
        'SH.600519': '白酒', 'SZ.000858': '白酒', 'SZ.000568': '白酒',
        'SZ.300750': '新能源', 'SZ.002594': '新能源', 'SH.601012': '新能源',
        'SH.601318': '金融', 'SH.600036': '金融', 'SZ.300059': '金融',
        'SZ.002415': '科技', 'SZ.002230': '科技', 'SH.688981': '科技',
        'SH.600276': '医药', 'SZ.300760': '医药',
        'SZ.000333': '消费', 'SZ.000651': '消费'
      }
      return map[code] || '其他'
    },
    filterStocks() {
      let stocks = this.stocks
      if (this.filterSector) stocks = stocks.filter(s => s.sector === this.filterSector)
      if (this.filterMarket) stocks = stocks.filter(s => s.market === this.filterMarket)
      if (this.searchKeyword) {
        const kw = this.searchKeyword.toLowerCase()
        stocks = stocks.filter(s => s.code.toLowerCase().includes(kw) || (s.name || '').includes(kw))
      }
      this.filteredStocks = stocks
      this.sortStocks()
    },
    sortStocks() {
      const sorted = [...this.filteredStocks]
      if (this.sortBy === 'change') sorted.sort((a, b) => b.change - a.change)
      else if (this.sortBy === 'code') sorted.sort((a, b) => a.code.localeCompare(b.code))
      else if (this.sortBy === 'name') sorted.sort((a, b) => a.name.localeCompare(b.name))
      else if (this.sortBy === 'volume') sorted.sort((a, b) => b.volume - a.volume)
      this.filteredStocks = sorted
    },
    updatePagedStocks() {
      const start = (this.currentPage - 1) * this.pageSize
      this.pagedStocks = this.filteredStocks.slice(start, start + this.pageSize)
    },
    showAddDialog() { this.newStock = { code: '', name: '', sector: '' }; this.addDialogVisible = true },
    async addStock() {
      if (!this.newStock.code) return this.$message.warning('请输入股票代码')
      this.adding = true
      try {
        await request.post('/stocks', this.newStock)
        this.$message.success('添加成功')
        this.addDialogVisible = false
        this.fetchStocks()
      } catch (e) { this.$message.error('添加失败') }
      finally { this.adding = false }
    },
    async removeStock(stock) {
      try {
        await request.delete(`/stocks/${stock.code}`)
        this.$message.success('已删除')
        this.fetchStocks()
      } catch (e) { this.$message.error('删除失败') }
    },
    goToDetail(stock) { this.$router.push(`/stock-detail/${stock.code}`) },
    aiAnalyze(stock) {
      this.$router.push({ path: '/ai-center/stock', query: { code: stock.code, name: stock.name } })
    },
    refresh() { this.fetchStocks(); this.$message.success('已刷新') },
    batchImport() { this.$message.info('导入功能开发中') },
    batchExport() {
      const csv = 'code,name,price,change,sector\n' + this.filteredStocks.map(s => `${s.code},${s.name},${s.price},${s.change},${s.sector}`).join('\n')
      const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `stocks_${new Date().toISOString().slice(0,10)}.csv`
      link.click()
      this.$message.success(`已导出 ${this.filteredStocks.length} 只股票`)
    }
  }
}
</script>

<style scoped>
.stock-pool-enhanced { background: #0f0f1a; min-height: 100vh; padding: 16px; }
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

.card-footer { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; color: #909399; font-size: 12px; }
</style>
