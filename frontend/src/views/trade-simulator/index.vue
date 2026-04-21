<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>💼 模拟交易</span>
        <el-tag size="mini" style="float:right;">初始资金: ¥1,000,000</el-tag>
      </div>
    </el-card>

    <!-- 账户概览 -->
    <el-row :gutter="20" v-if="simData.balance >= 0">
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="color:#909399;font-size:13px;">账户余额</div>
          <div style="font-size:20px;font-weight:600;margin-top:8px;">¥{{ simData.balance.toLocaleString() }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="color:#909399;font-size:13px;">总资产</div>
          <div style="font-size:20px;font-weight:600;margin-top:8px;">¥{{ simData.total_value?.toLocaleString() || '-' }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="color:#909399;font-size:13px;">总盈亏</div>
          <div style="font-size:20px;font-weight:600;margin-top:8px;" :style="{color: simData.total_pnl > 0 ? '#67C23A' : '#F56C6C'}">
            {{ simData.total_pnl > 0 ? '+' : '' }}¥{{ simData.total_pnl?.toLocaleString() || '0' }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="color:#909399;font-size:13px;">收益率</div>
          <div style="font-size:20px;font-weight:600;margin-top:8px;" :style="{color: simData.return_pct > 0 ? '#67C23A' : '#F56C6C'}">
            {{ simData.return_pct > 0 ? '+' : '' }}{{ simData.return_pct || '0' }}%
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 交易操作 -->
    <el-card style="margin-top:20px;">
      <div slot="header"><span>🔄 交易操作</span></div>
      <el-form :inline="true" size="small">
        <el-form-item label="股票代码"><el-input v-model="tradeForm.code" placeholder="SH.600519" style="width:130px;" /></el-form-item>
        <el-form-item label="价格"><el-input-number v-model="tradeForm.price" :min="0" :step="0.01" style="width:100px;" /></el-form-item>
        <el-form-item label="数量"><el-input-number v-model="tradeForm.qty" :min="100" :step="100" style="width:100px;" /></el-form-item>
        <el-form-item>
          <el-button type="success" @click="executeTrade('buy')">买入</el-button>
          <el-button type="danger" @click="executeTrade('sell')">卖出</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 持仓列表 -->
    <el-card style="margin-top:20px;">
      <div slot="header"><span>📊 持仓列表</span></div>
      <el-table :data="simData.positions || []" style="width:100%">
        <el-table-column prop="code" label="代码" width="110" />
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column prop="qty" label="数量" width="80" />
        <el-table-column prop="avg_cost" label="成本价" width="90" />
        <el-table-column prop="current_price" label="现价" width="90" />
        <el-table-column label="盈亏" width="100">
          <template slot-scope="{ row }">
            <span :style="{color: (row.current_price - row.avg_cost) > 0 ? '#67C23A' : '#F56C6C'}">
              {{ ((row.current_price - row.avg_cost) * row.qty).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 交易历史 -->
    <el-card style="margin-top:20px;">
      <div slot="header"><span>📜 交易历史</span></div>
      <el-table :data="simData.history || []" style="width:100%">
        <el-table-column label="时间" width="160">
          <template slot-scope="{ row }">{{ new Date(row.time).toLocaleString('zh-CN') }}</template>
        </el-table-column>
        <el-table-column prop="action" label="操作" width="80">
          <template slot-scope="{ row }"><el-tag size="mini" :type="row.action === '买入' ? 'success' : 'danger'">{{ row.action }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="code" label="代码" width="110" />
        <el-table-column prop="price" label="价格" width="90" />
        <el-table-column prop="qty" label="数量" width="80" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'TradeSimulator',
  data() {
    return {
      simData: { balance: -1, total_value: 0, total_pnl: 0, return_pct: 0, positions: [], history: [] },
      tradeForm: { code: '', price: 0, qty: 100 }
    }
  },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try {
        const { data } = await request.get('/trade-simulator')
        if (data.code === 200) this.simData = data.data
      } catch (e) { this.$message.error('获取模拟交易数据失败') }
    },
    async executeTrade(action) {
      if (!this.tradeForm.code || !this.tradeForm.price) {
        return this.$message.warning('请填写完整交易信息')
      }
      try {
        const { data } = await request.post('/trade-simulator', {
          action,
          code: this.tradeForm.code,
          price: this.tradeForm.price,
          qty: this.tradeForm.qty
        })
        if (data.code === 200) {
          this.$message.success(data.message)
          this.fetchData()
        } else {
          this.$message.error(data.message)
        }
      } catch (e) { this.$message.error('交易失败') }
    }
  }
}
</script>
