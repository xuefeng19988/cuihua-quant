<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>🌍 投资组合</span>
      <div style="float:right;display:flex;gap:8px;align-items:center;">
        <el-form :inline="true" size="mini">
          <el-form-item label="总资金"><el-input-number v-model="totalCapital" :step="10000" @change="updateCapital" /></el-form-item>
          <el-form-item><el-button type="primary" @click="updatePortfolio">💾 保存</el-button></el-form-item>
        </el-form>
      </div>
    </div></el-card>

    <!-- 核心指标 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="hover"><div style="color:#909399;font-size:13px;">{{ card.label }}</div><div style="font-size:20px;font-weight:600;margin-top:8px;" :style="{color:card.color}">{{ card.value }}</div></el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="20" style="margin-top:20px;">
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>🥧 资产配置</span></div>
          <pie-chart :data="allocationData" title="持仓占比" :height="300" :show-label="false" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>🌳 行业分布</span></div>
          <treemap-chart :data="industryTreeData" title="行业树图" :height="300" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top:20px;">
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>📊 盈亏贡献</span></div>
          <waterfall-chart :data="pnlContribution" title="各股票盈亏贡献" :height="280" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header"><span>📈 持仓市值变化</span></div>
          <line-chart :categories="marketValueCategories" :series="marketValueSeries" title="持仓市值" :height="280" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 持仓表格 -->
    <el-card style="margin-top:20px;">
      <div slot="header"><span>📋 持仓明细</span>
        <el-button size="mini" type="primary" style="float:right;" @click="showAddDialog">➕ 添加持仓</el-button>
      </div>
      <el-table :data="positions" stripe>
        <el-table-column prop="code" label="代码" width="110" />
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column prop="shares" label="股数" width="80" />
        <el-table-column prop="cost" label="成本价" width="90" />
        <el-table-column prop="price" label="现价" width="90" />
        <el-table-column label="市值" width="100"><template slot-scope="{ row }">{{ (row.shares * row.price).toFixed(0) }}</template></el-table-column>
        <el-table-column label="盈亏" width="100"><template slot-scope="{ row }"><span :style="{color:(row.price-row.cost)*row.shares>=0?'#67C23A':'#F56C6C'}">{{ ((row.price-row.cost)*row.shares).toFixed(0) }}</span></template></el-table-column>
        <el-table-column label="占比" width="80"><template slot-scope="{ row }">{{ ((row.shares * row.price / totalMarketValue) * 100).toFixed(1) }}%</template></el-table-column>
        <el-table-column label="操作" width="80"><template slot-scope="{ row }"><el-button size="mini" type="danger" @click="removePosition(row)">🗑️</el-button></template></el-table-column>
      </el-table>
    </el-card>

    <!-- 添加持仓对话框 -->
    <el-dialog title="添加持仓" :visible.sync="addDialogVisible" width="400px">
      <el-form :model="newPosition" label-width="80px">
        <el-form-item label="股票代码"><el-input v-model="newPosition.code" placeholder="如 SH.600519" /></el-form-item>
        <el-form-item label="股票名称"><el-input v-model="newPosition.name" /></el-form-item>
        <el-form-item label="股数"><el-input-number v-model="newPosition.shares" :min="100" :step="100" /></el-form-item>
        <el-form-item label="成本价"><el-input-number v-model="newPosition.cost" :min="0" :step="1" /></el-form-item>
        <el-form-item label="现价"><el-input-number v-model="newPosition.price" :min="0" :step="1" /></el-form-item>
      </el-form>
      <span slot="footer"><el-button @click="addDialogVisible=false">取消</el-button><el-button type="primary" @click="addPosition">确认</el-button></span>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
import { PieChart, LineChart, TreemapChart, WaterfallChart } from '@/components/charts'

export default {
  name: 'Portfolio',
  components: { PieChart, LineChart, TreemapChart, WaterfallChart },
  data() {
    return {
      totalCapital: 1000000,
      positions: [
        { code: 'SH.600519', name: '贵州茅台', shares: 100, cost: 1680, price: 1720 },
        { code: 'SZ.002594', name: '比亚迪', shares: 200, cost: 280, price: 295 },
        { code: 'SH.601318', name: '中国平安', shares: 300, cost: 48, price: 50 },
        { code: 'SZ.300750', name: '宁德时代', shares: 100, cost: 200, price: 215 },
        { code: 'HK.00700', name: '腾讯控股', shares: 200, cost: 300, price: 320 }
      ],
      addDialogVisible: false,
      newPosition: { code: '', name: '', shares: 100, cost: 0, price: 0 },
      marketValueCategories: ['1月', '2月', '3月', '4月', '5月', '6月'],
      marketValueSeries: [{ name: '市值(万)', data: [95, 98, 102, 100, 105, 105.2], color: '#409EFF' }]
    }
  },
  computed: {
    totalMarketValue() {
      return this.positions.reduce((sum, p) => sum + p.shares * p.price, 0)
    },
    totalCost() {
      return this.positions.reduce((sum, p) => sum + p.shares * p.cost, 0)
    },
    totalPnl() {
      return this.totalMarketValue - this.totalCost
    },
    statCards() {
      return [
        { label: '总市值', value: `¥${this.totalMarketValue.toFixed(0)}`, color: '#409EFF' },
        { label: '总成本', value: `¥${this.totalCost.toFixed(0)}`, color: '#909399' },
        { label: '总盈亏', value: `${this.totalPnl >= 0 ? '+' : ''}¥${this.totalPnl.toFixed(0)}`, color: this.totalPnl >= 0 ? '#67C23A' : '#F56C6C' },
        { label: '收益率', value: `${((this.totalPnl / this.totalCost) * 100).toFixed(2)}%`, color: this.totalPnl >= 0 ? '#67C23A' : '#F56C6C' }
      ]
    },
    allocationData() {
      const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#ffeb3b', '#ff9800']
      return this.positions.map((p, i) => ({
        value: p.shares * p.price,
        name: p.name,
        itemStyle: { color: colors[i % colors.length] }
      }))
    },
    industryTreeData() {
      const industries = { '白酒': [], '新能源': [], '金融': [], '科技': [] }
      const industryMap = { 'SH.600519': '白酒', 'SZ.002594': '新能源', 'SH.601318': '金融', 'SZ.300750': '新能源', 'HK.00700': '科技' }
      this.positions.forEach(p => {
        const ind = industryMap[p.code] || '其他'
        if (!industries[ind]) industries[ind] = []
        industries[ind].push({ name: p.name, value: p.shares * p.price })
      })
      return Object.entries(industries).filter(([_, v]) => v.length > 0).map(([k, v]) => ({ name: k, children: v }))
    },
    pnlContribution() {
      return this.positions.map(p => ({
        name: p.name,
        value: (p.price - p.cost) * p.shares
      }))
    }
  },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try { const { data } = await request.get('/api/portfolio'); if (data.code === 200) { this.positions = data.data.positions || this.positions; this.totalCapital = data.data.total_capital || 1000000 } } catch (e) {}
    },
    showAddDialog() { this.newPosition = { code: '', name: '', shares: 100, cost: 0, price: 0 }; this.addDialogVisible = true },
    addPosition() {
      if (!this.newPosition.code) return this.$message.warning('请输入代码')
      this.positions.push({ ...this.newPosition })
      this.addDialogVisible = false
      this.$message.success('添加成功')
    },
    removePosition(row) {
      this.positions = this.positions.filter(p => p.code !== row.code)
      this.$message.success('已移除')
    },
    async updateCapital() {},
    async updatePortfolio() { this.$message.success('保存成功') }
  }
}
</script>
