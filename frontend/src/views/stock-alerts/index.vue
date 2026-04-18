<template>
  <div class="stock-alerts app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>🚨 行情异动提醒</span>
        <el-button size="mini" type="primary" style="float:right;" @click="refreshAlerts">🔄 刷新</el-button>
      </div>
      
      <!-- 异动类型筛选 -->
      <el-form :inline="true" size="small">
        <el-form-item label="异动类型">
          <el-select v-model="alertType" placeholder="全部" clearable @change="filterAlerts">
            <el-option label="涨停" value="limit_up" />
            <el-option label="跌停" value="limit_down" />
            <el-option label="大幅上涨" value="surge" />
            <el-option label="大幅下跌" value="plunge" />
            <el-option label="放量" value="volume_surge" />
            <el-option label="换手率高" value="high_turnover" />
          </el-select>
        </el-form-item>
        <el-form-item label="市场">
          <el-select v-model="market" placeholder="全部" clearable @change="filterAlerts">
            <el-option label="A股" value="a" />
            <el-option label="港股" value="hk" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 异动列表 -->
    <el-card>
      <el-table :data="filteredAlerts" style="width:100%" stripe>
        <el-table-column prop="time" label="时间" width="120" />
        <el-table-column prop="code" label="代码" width="110" />
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column prop="price" label="最新价" width="90" />
        <el-table-column prop="change" label="涨跌幅" width="90">
          <template slot-scope="{ row }">
            <span :style="{color: row.change > 0 ? '#26a69a' : '#ef5350', fontWeight: 600}">
              {{ row.change > 0 ? '+' : '' }}{{ row.change.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="alertType" label="异动类型" width="100">
          <template slot-scope="{ row }">
            <el-tag size="mini" :type="getAlertTypeColor(row.alertType)">
              {{ getAlertTypeName(row.alertType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="异动说明" />
        <el-table-column label="操作" width="100">
          <template slot-scope="{ row }">
            <el-button size="mini" @click="goToDetail(row.code)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 异动统计 -->
    <el-row :gutter="20" style="margin-top:20px;">
      <el-col :span="6" v-for="stat in alertStats" :key="stat.type">
        <el-card shadow="hover" style="text-align:center;">
          <div style="color:#909399;font-size:12px;">{{ stat.name }}</div>
          <div style="font-size:24px;font-weight:600;margin:8px 0;" :style="{color: stat.color}">
            {{ stat.count }}
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'StockAlerts',
  data() {
    return {
      alertType: '',
      market: '',
      alerts: [],
      alertStats: [
        { type: 'limit_up', name: '涨停', count: 0, color: '#F56C6C' },
        { type: 'limit_down', name: '跌停', count: 0, color: '#26a69a' },
        { type: 'surge', name: '大幅上涨', count: 0, color: '#E6A23C' },
        { type: 'volume_surge', name: '放量', count: 0, color: '#409EFF' }
      ]
    }
  },
  computed: {
    filteredAlerts() {
      let alerts = this.alerts
      if (this.alertType) {
        alerts = alerts.filter(a => a.alertType === this.alertType)
      }
      if (this.market) {
        alerts = alerts.filter(a => {
          if (this.market === 'a') return a.code.startsWith('SH.') || a.code.startsWith('SZ.')
          if (this.market === 'hk') return a.code.startsWith('HK.')
          return true
        })
      }
      return alerts
    }
  },
  created() { this.loadAlerts() },
  methods: {
    loadAlerts() {
      // 模拟异动数据
      this.alerts = [
        { time: '14:30', code: 'SH.600519', name: '贵州茅台', price: 1750.00, change: 10.01, alertType: 'limit_up', description: '涨停' },
        { time: '14:25', code: 'SZ.002594', name: '比亚迪', price: 280.50, change: -9.98, alertType: 'limit_down', description: '跌停' },
        { time: '14:20', code: 'SH.601318', name: '中国平安', price: 52.30, change: 8.55, alertType: 'surge', description: '大幅上涨' },
        { time: '14:15', code: 'SZ.300750', name: '宁德时代', price: 220.80, change: 7.25, alertType: 'surge', description: '大幅上涨' },
        { time: '14:10', code: 'HK.00700', name: '腾讯控股', price: 330.20, change: -5.80, alertType: 'plunge', description: '大幅下跌' },
        { time: '14:05', code: 'SH.600036', name: '招商银行', price: 38.50, change: 6.20, alertType: 'volume_surge', description: '放量上涨' },
        { time: '14:00', code: 'SZ.000858', name: '五粮液', price: 185.60, change: 9.95, alertType: 'limit_up', description: '涨停' }
      ]
      
      // 更新统计
      this.alertStats.forEach(stat => {
        stat.count = this.alerts.filter(a => a.alertType === stat.type).length
      })
    },
    
    filterAlerts() {
      // 筛选逻辑在 computed 中处理
    },
    
    refreshAlerts() {
      this.loadAlerts()
      this.$message.success('已刷新')
    },
    
    getAlertTypeName(type) {
      const names = {
        limit_up: '涨停',
        limit_down: '跌停',
        surge: '大幅上涨',
        plunge: '大幅下跌',
        volume_surge: '放量',
        high_turnover: '高换手'
      }
      return names[type] || type
    },
    
    getAlertTypeColor(type) {
      const colors = {
        limit_up: 'danger',
        limit_down: 'success',
        surge: 'warning',
        plunge: 'danger',
        volume_surge: 'primary',
        high_turnover: 'info'
      }
      return colors[type] || 'info'
    },
    
    goToDetail(code) {
      this.$router.push(`/stock-detail/${code}`)
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
