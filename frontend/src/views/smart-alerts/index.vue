<template>
  <div class="smart-alerts app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>🔔 智能提醒系统</span>
        <el-button size="mini" type="primary" style="float:right;" @click="showAddAlert">➕ 新建提醒</el-button>
      </div>
      
      <!-- 提醒统计 -->
      <el-row :gutter="20">
        <el-col :span="6" v-for="stat in alertStats" :key="stat.type">
          <el-card shadow="hover" style="text-align:center;">
            <div style="color:#909399;font-size:12px;">{{ stat.name }}</div>
            <div style="font-size:24px;font-weight:600;margin:8px 0;" :style="{color: stat.color}">
              {{ stat.count }}
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 提醒列表 -->
    <el-card>
      <el-table :data="alerts" style="width:100%" stripe>
        <el-table-column prop="name" label="提醒名称" width="150" />
        <el-table-column prop="code" label="股票代码" width="110" />
        <el-table-column prop="condition" label="触发条件" width="180">
          <template slot-scope="{ row }">
            <el-tag size="mini" :type="getConditionType(row.condition)">
              {{ row.condition }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="触发值" width="100" />
        <el-table-column prop="status" label="状态" width="80">
          <template slot-scope="{ row }">
            <el-switch v-model="row.enabled" @change="toggleAlert(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="triggered" label="已触发" width="80" />
        <el-table-column prop="lastTrigger" label="最后触发" width="150" />
        <el-table-column label="操作" width="150">
          <template slot-scope="{ row }">
            <el-button size="mini" @click="editAlert(row)">编辑</el-button>
            <el-button size="mini" type="danger" @click="deleteAlert(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑提醒对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="500px">
      <el-form :model="alertForm" label-width="100px">
        <el-form-item label="提醒名称">
          <el-input v-model="alertForm.name" placeholder="如：突破20日均线" />
        </el-form-item>
        <el-form-item label="股票代码">
          <el-select v-model="alertForm.code" filterable placeholder="选择股票" style="width:100%;">
            <el-option v-for="s in stocks" :key="s.code" :label="s.code + ' ' + s.name" :value="s.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="触发条件">
          <el-select v-model="alertForm.condition" style="width:100%;">
            <el-option label="价格突破" value="price_break" />
            <el-option label="涨跌幅" value="change_pct" />
            <el-option label="成交量突破" value="volume_break" />
            <el-option label="RSI超买" value="rsi_overbought" />
            <el-option label="RSI超卖" value="rsi_oversold" />
            <el-option label="MACD金叉" value="macd_golden" />
            <el-option label="MACD死叉" value="macd_death" />
            <el-option label="突破均线" value="ma_break" />
          </el-select>
        </el-form-item>
        <el-form-item label="触发值">
          <el-input-number v-model="alertForm.value" :precision="2" :step="0.01" style="width:100%;" />
        </el-form-item>
        <el-form-item label="通知方式">
          <el-checkbox-group v-model="alertForm.notifyMethods">
            <el-checkbox label="system">系统通知</el-checkbox>
            <el-checkbox label="email">邮件</el-checkbox>
            <el-checkbox label="wechat">微信</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAlert">保存</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'SmartAlerts',
  data() {
    return {
      alerts: [],
      stocks: [],
      dialogVisible: false,
      editingAlert: null,
      alertForm: {
        name: '',
        code: '',
        condition: 'price_break',
        value: 0,
        notifyMethods: ['system'],
        enabled: true
      },
      alertStats: [
        { type: 'total', name: '总提醒', count: 0, color: '#409EFF' },
        { type: 'enabled', name: '已启用', count: 0, color: '#67C23A' },
        { type: 'triggered', name: '已触发', count: 0, color: '#E6A23C' },
        { type: 'disabled', name: '已禁用', count: 0, color: '#909399' }
      ]
    }
  },
  computed: {
    dialogTitle() {
      return this.editingAlert ? '编辑提醒' : '新建提醒'
    }
  },
  created() {
    this.loadAlerts()
    this.loadStocks()
  },
  methods: {
    async loadAlerts() {
      // 模拟提醒数据
      this.alerts = [
        {
          id: 1,
          name: '突破20日均线',
          code: 'SH.600519',
          condition: 'ma_break',
          value: 1720.00,
          enabled: true,
          triggered: 3,
          lastTrigger: '2026-04-18 14:30',
          notifyMethods: ['system']
        },
        {
          id: 2,
          name: 'RSI超卖',
          code: 'SZ.002594',
          condition: 'rsi_oversold',
          value: 30,
          enabled: true,
          triggered: 1,
          lastTrigger: '2026-04-17 10:15',
          notifyMethods: ['system', 'email']
        },
        {
          id: 3,
          name: '放量突破',
          code: 'SH.601318',
          condition: 'volume_break',
          value: 5000000,
          enabled: false,
          triggered: 0,
          lastTrigger: '-',
          notifyMethods: ['system']
        }
      ]
      
      // 更新统计
      this.alertStats[0].count = this.alerts.length
      this.alertStats[1].count = this.alerts.filter(a => a.enabled).length
      this.alertStats[2].count = this.alerts.reduce((sum, a) => sum + a.triggered, 0)
      this.alertStats[3].count = this.alerts.filter(a => !a.enabled).length
    },
    
    async loadStocks() {
      try {
        const { data } = await request.get('/stocks')
        if (data.code === 200) {
          this.stocks = data.data.list || []
        }
      } catch (e) {}
    },
    
    showAddAlert() {
      this.editingAlert = null
      this.alertForm = {
        name: '',
        code: '',
        condition: 'price_break',
        value: 0,
        notifyMethods: ['system'],
        enabled: true
      }
      this.dialogVisible = true
    },
    
    editAlert(alert) {
      this.editingAlert = alert
      this.alertForm = { ...alert }
      this.dialogVisible = true
    },
    
    async saveAlert() {
      if (!this.alertForm.name || !this.alertForm.code) {
        return this.$message.warning('请填写完整信息')
      }
      
      if (this.editingAlert) {
        // 更新提醒
        const index = this.alerts.findIndex(a => a.id === this.editingAlert.id)
        if (index !== -1) {
          this.alerts[index] = { ...this.alerts[index], ...this.alertForm }
        }
        this.$message.success('提醒已更新')
      } else {
        // 新建提醒
        const newAlert = {
          id: this.alerts.length + 1,
          ...this.alertForm,
          triggered: 0,
          lastTrigger: '-'
        }
        this.alerts.push(newAlert)
        this.$message.success('提醒已创建')
      }
      
      this.dialogVisible = false
      this.loadAlerts()
    },
    
    async deleteAlert(alert) {
      try {
        await this.$confirm(`确定删除提醒"${alert.name}"？`, '提示', { type: 'warning' })
        this.alerts = this.alerts.filter(a => a.id !== alert.id)
        this.$message.success('已删除')
        this.loadAlerts()
      } catch (e) {}
    },
    
    async toggleAlert(alert) {
      this.$message.success(`提醒已${alert.enabled ? '启用' : '禁用'}`)
      this.loadAlerts()
    },
    
    getConditionType(condition) {
      const types = {
        price_break: 'primary',
        change_pct: 'warning',
        volume_break: 'success',
        rsi_overbought: 'danger',
        rsi_oversold: 'success',
        macd_golden: 'success',
        macd_death: 'danger',
        ma_break: 'primary'
      }
      return types[condition] || 'info'
    }
  }
}
</script>

<style scoped>
.app-container {
  background: #0f0f1a;
  min-height: 100vh;
  padding: 16px;
}

.el-card {
  background: #1a1a2e !important;
  border: 1px solid #2a2a3e !important;
}

.el-card__header {
  border-bottom: 1px solid #2a2a3e !important;
}
</style>
