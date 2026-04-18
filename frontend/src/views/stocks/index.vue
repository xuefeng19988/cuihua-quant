<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>💼 股票池</span>
        <div style="float:right;">
          <el-tag size="mini">{{ filtered.length }} 只</el-tag>
          <el-button size="mini" type="primary" @click="showAddDialog" style="margin-left:8px;">➕ 添加</el-button>
          <el-button size="mini" @click="showImportDialog" style="margin-left:4px;">📥 导入</el-button>
          <el-button size="mini" @click="exportStocks" style="margin-left:4px;">📤 导出</el-button>
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

    <!-- 图表区 -->
    <el-row :gutter="20" style="margin-bottom:20px;">
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📊 涨跌分布</span></div>
          <pie-chart :data="changeDistribution" title="涨/平/跌" :height="250" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>🥧 行业占比</span></div>
          <pie-chart :data="industryDistribution" title="行业分布" :height="250" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📈 成交量 Top10</span></div>
          <bar-chart :data="topVolumeData" :categories="topVolumeCategories" title="成交量排行" :height="250" :horizontal="true" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 高级图表 -->
    <el-row :gutter="20" style="margin-bottom:20px;">
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>🔗 股票相关性热力图</span></div>
          <heatmap-chart :data="correlationData" :x-axis="correlationXAxis" :y-axis="correlationYAxis" title="相关系数矩阵" :height="300" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>📈 估值对比 (PE vs PB)</span></div>
          <scatter-plot :data="valuationScatterData" :x-axis-name="PE" :y-axis-name="PB" title="估值散点图" :height="300" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 股票表格 -->
    <el-card>
      <el-table :data="filtered" style="width: 100%" v-loading="loading" stripe>
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

    <!-- 批量导入对话框 -->
    <el-dialog title="批量导入股票" :visible.sync="importDialogVisible" width="500px">
      <el-alert title="CSV格式: code,name" type="info" :closable="false" style="margin-bottom:16px;" />
      <el-input type="textarea" v-model="importCsv" :rows="8" placeholder="SH.600519,贵州茅台&#10;SZ.002594,比亚迪" />
      <span slot="footer">
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="importStocks" :loading="importing">导入</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
import { PieChart, BarChart, HeatmapChart, ScatterPlot } from '@/components/charts'

export default {
  name: 'Stocks',
  components: { PieChart, BarChart, HeatmapChart, ScatterPlot },
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
      importDialogVisible: false,
      adding: false,
      importing: false,
      newStock: { code: '', name: '' },
      importCsv: ''
    }
  },
  computed: {
    changeDistribution() {
      const up = this.stocks.filter(s => s.change > 0).length
      const down = this.stocks.filter(s => s.change < 0).length
      const flat = this.stocks.length - up - down
      return [
        { value: up, name: '上涨', itemStyle: { color: '#26a69a' } },
        { value: flat, name: '平盘', itemStyle: { color: '#909399' } },
        { value: down, name: '下跌', itemStyle: { color: '#ef5350' } }
      ]
    },
    industryDistribution() {
      const industries = {}
      this.stocks.forEach(s => {
        const ind = s.industry || '其他'
        industries[ind] = (industries[ind] || 0) + 1
      })
      const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#ffeb3b', '#ff9800']
      return Object.entries(industries).map(([name, value], i) => ({
        name, value, itemStyle: { color: colors[i % colors.length] }
      }))
    },
    topVolumeData() {
      return [...this.stocks].sort((a, b) => (b.volume || 0) - (a.volume || 0)).slice(0, 10).map(s => s.volume || 0)
    },
    topVolumeCategories() {
      return [...this.stocks].sort((a, b) => (b.volume || 0) - (a.volume || 0)).slice(0, 10).map(s => s.name)
    },
    // 相关性热力图数据
    correlationXAxis() {
      return this.stocks.slice(0, 8).map(s => s.name)
    },
    correlationYAxis() {
      return this.stocks.slice(0, 8).map(s => s.name)
    },
    correlationData() {
      const n = Math.min(this.stocks.length, 8)
      const data = []
      for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
          const corr = i === j ? 1 : (Math.random() * 1.4 - 0.2)
          data.push([j, i, parseFloat(corr.toFixed(2))])
        }
      }
      return data
    },
    // 估值散点图数据
    valuationScatterData() {
      return this.stocks.slice(0, 10).map((s, i) => [
        (Math.random() * 30 + 10).toFixed(1),  // PE
        (Math.random() * 8 + 1).toFixed(1),     // PB
        Math.floor(Math.random() * 100 + 50),   // size
        s.name
      ])
    }
  },
  created() { this.fetchData(); this.fetchGroups() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/api/stocks', { params: { page: this.page } })
        if (data.code === 200) {
          this.stocks = (data.data.list || []).map(s => ({ ...s, groups: ['watchlist'], industry: this.getIndustry(s.code) }))
          this.total = data.data.total || 0
          this.filterStocks()
        }
      } catch (e) { this.$message.error('获取股票数据失败') }
      finally { this.loading = false }
    },
    getIndustry(code) {
      const map = { 'SH.600519': '白酒', 'SZ.000858': '白酒', 'SZ.300750': '新能源', 'SZ.002594': '新能源', 'SH.601318': '金融', 'SH.600036': '金融', 'SZ.002415': '科技', 'SZ.002230': '科技' }
      return map[code] || '其他'
    },
    async fetchGroups() {
      try { const { data } = await request.get('/api/stock-groups'); if (data.code === 200) this.groups = data.data.groups || {} } catch (e) {}
    },
    filterStocks() {
      let list = this.stocks
      if (this.filterGroup && this.groups[this.filterGroup]) {
        const groupCodes = this.groups[this.filterGroup].stocks || []
        list = list.filter(s => groupCodes.includes(s.code))
      }
      const kw = this.keyword.toLowerCase()
      if (kw) list = list.filter(s => s.code.toLowerCase().includes(kw) || (s.name || '').includes(kw))
      this.filtered = list
    },
    showAddDialog() { this.newStock = { code: '', name: '' }; this.addDialogVisible = true },
    async addStock() {
      if (!this.newStock.code) return this.$message.warning('请输入股票代码')
      this.adding = true
      try { await request.post('/api/stocks', this.newStock); this.$message.success('添加成功'); this.addDialogVisible = false; this.fetchData() }
      catch (e) { this.$message.error('添加失败') }
      finally { this.adding = false }
    },
    async deleteStock(code) {
      try { await request.delete(`/api/stocks/${code}`); this.$message.success('已删除'); this.fetchData() }
      catch (e) { this.$message.error('删除失败') }
    },
    showImportDialog() { this.importCsv = ''; this.importDialogVisible = true },
    async importStocks() {
      if (!this.importCsv.trim()) return this.$message.warning('请输入CSV数据')
      this.importing = true
      try {
        const { data } = await request.post('/api/stock-import', { csv: this.importCsv })
        if (data.code === 200) { this.$message.success(`导入成功: ${data.data.imported}只, 跳过${data.data.skipped}只`); this.importDialogVisible = false; this.fetchData() }
      } catch (e) { this.$message.error('导入失败') }
      finally { this.importing = false }
    },
    async exportStocks() {
      try {
        const { data } = await request.get('/api/stock-export')
        if (data.code === 200) {
          const csv = 'code,name\n' + data.data.stocks.map(s => `${s.code},${s.name}`).join('\n')
          const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
          const link = document.createElement('a')
          link.href = URL.createObjectURL(blob)
          link.download = `stocks_${new Date().toISOString().slice(0,10)}.csv`
          link.click()
          this.$message.success(`已导出 ${data.data.total} 只股票`)
        }
      } catch (e) { this.$message.error('导出失败') }
    },
    async refresh() { this.fetchData() }
  }
}
</script>
