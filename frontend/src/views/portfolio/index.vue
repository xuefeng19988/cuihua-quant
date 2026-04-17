<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="item in summary" :key="item.label">
        <el-card shadow="hover">
          <div style="color: #909399; font-size: 13px;">{{ item.label }}</div>
          <div style="font-size: 24px; font-weight: 600; margin-top: 8px;" :style="{ color: item.color }">{{ item.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>💰 设置总资金</span></div>
      <el-form :inline="true" @submit.native.prevent>
        <el-form-item label="总资金 (元)"><el-input-number v-model="capital" :step="10000" /></el-form-item>
        <el-form-item><el-button type="primary" @click="saveCapital">💾 保存</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>➕ 添加持仓</span></div>
      <el-form :inline="true" @submit.native.prevent>
        <el-form-item label="股票"><el-select v-model="addForm.code" filterable placeholder="选择" style="width: 180px;">
          <el-option v-for="s in stockOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select></el-form-item>
        <el-form-item label="买入价"><el-input-number v-model="addForm.buy_price" :precision="2" :step="0.01" /></el-form-item>
        <el-form-item label="数量"><el-input-number v-model="addForm.quantity" :step="100" /></el-form-item>
        <el-form-item label="目标价"><el-input-number v-model="addForm.target_price" :precision="2" :step="0.01" /></el-form-item>
        <el-form-item><el-button type="success" @click="addPosition">➕ 添加</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <div slot="header"><span>📋 持仓明细</span></div>
      <el-table :data="positions" style="width: 100%">
        <el-table-column prop="code" label="代码" width="110"><template slot-scope="{ row }"><el-tag size="small">{{ row.code }}</el-tag></template></el-table-column>
        <el-table-column prop="name" label="名称" width="80" />
        <el-table-column prop="buy_price" label="买入价" width="80" />
        <el-table-column prop="quantity" label="数量" width="70" />
        <el-table-column prop="current_price" label="现价" width="80" />
        <el-table-column label="盈亏" width="120">
          <template slot-scope="{ row }">
            <span :style="{ color: row.pnl >= 0 ? '#67C23A' : '#F56C6C', fontWeight: 600 }">¥{{ row.pnl >= 0 ? '+' : '' }}{{ row.pnl }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="目标" width="80" />
        <el-table-column label="操作" width="80">
          <template slot-scope="{ row, $index }"><el-button size="mini" type="danger" @click="delPosition($index)">🗑️</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Portfolio',
  data() {
    return {
      capital: 1000000, summary: [], positions: [], stockOptions: [],
      addForm: { code: '', buy_price: 0, quantity: 0, target_price: 0 }
    }
  },
  created() { this.fetchData() },
  methods: {
    fetchData() {
      fetch('/api/portfolio')
        .then(res => res.json())
        .then(data => {
          if (data.code === 200) {
            const d = data.data
            this.capital = d.total_capital || 1000000
            this.positions = d.positions || []
            this.summary = [
              { label: '总资金', value: `¥${(d.total_capital||0).toLocaleString()}`, color: '#303133' },
              { label: '持仓市值', value: `¥${(d.total_market||0).toLocaleString()}`, color: '#303133' },
              { label: '可用现金', value: `¥${(d.cash||0).toLocaleString()}`, color: '#67C23A' },
              { label: '总盈亏', value: `¥${d.total_pnl >= 0 ? '+' : ''}${(d.total_pnl||0).toLocaleString()}`, color: d.total_pnl >= 0 ? '#67C23A' : '#F56C6C' }
            ]
            this.stockOptions = d.stock_options || []
          }
        })
    },
    saveCapital() {
      fetch('/api/portfolio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'set_capital', total_capital: this.capital })
      }).then(() => { this.$message.success('已保存'); this.fetchData() })
    },
    addPosition() {
      fetch('/api/portfolio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'add_position', ...this.addForm })
      }).then(() => {
        this.$message.success('已添加')
        this.addForm = { code: '', buy_price: 0, quantity: 0, target_price: 0 }
        this.fetchData()
      })
    },
    delPosition(idx) {
      fetch('/api/portfolio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'del_position', idx })
      }).then(() => { this.$message.success('已删除'); this.fetchData() })
    }
  }
}
</script>
