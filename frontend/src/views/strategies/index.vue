<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>🎯 策略管理</span>
        <el-tag size="mini" style="float:right;">{{ strategies.length }} 个策略</el-tag>
      </div>
      <el-form :inline="true">
        <el-form-item label="状态筛选">
          <el-select v-model="filterStatus" size="small" @change="filterData">
            <el-option label="全部" value="" />
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型筛选">
          <el-select v-model="filterType" size="small" @change="filterData">
            <el-option label="全部" value="" />
            <el-option label="多因子" value="multi_factor" />
            <el-option label="动量" value="momentum" />
            <el-option label="均值回归" value="mean_reversion" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="filteredStrategies" style="width: 100%">
        <el-table-column prop="name" label="策略名称" width="140" />
        <el-table-column prop="type" label="类型" width="100">
          <template slot-scope="{ row }"><el-tag size="mini" type="info">{{ row.type }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template slot-scope="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="mini">{{ row.status === 'active' ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="return_pct" label="收益率" width="90">
          <template slot-scope="{ row }">
            <span :style="{ color: row.return_pct > 0 ? '#67C23A' : '#F56C6C', fontWeight: 600 }">{{ row.return_pct > 0 ? '+' : '' }}{{ row.return_pct }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="sharpe" label="夏普比率" width="90" />
        <el-table-column prop="max_dd" label="最大回撤" width="90">
          <template slot-scope="{ row }"><span style="color:#F56C6C;">{{ row.max_dd }}%</span></template>
        </el-table-column>
        <el-table-column prop="win_rate" label="胜率" width="80" />
        <el-table-column prop="signals" label="信号数" width="80" />
        <el-table-column prop="last_signal" label="最后信号" width="110" />
        <el-table-column label="操作" width="120">
          <template slot-scope="{ row }">
            <el-button size="mini" type="primary" @click="toggleStrategy(row)">{{ row.status === 'active' ? '停用' : '启用' }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'Strategies',
  data() {
    return { strategies: [], filteredStrategies: [], filterStatus: '', filterType: '' }
  },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try {
        const { data } = await request.get('/api/strategies')
        if (data.code === 200) {
          this.strategies = data.data.strategies || []
          this.filterData()
        }
      } catch (e) {
        this.$message.error('获取策略数据失败')
      }
    },
    filterData() {
      this.filteredStrategies = this.strategies.filter(s => {
        if (this.filterStatus && s.status !== this.filterStatus) return false
        if (this.filterType && s.type !== this.filterType) return false
        return true
      })
    },
    toggleStrategy(row) {
      const newStatus = row.status === 'active' ? 'inactive' : 'active'
      this.$confirm(`确定${newStatus === 'active' ? '启用' : '停用'}策略 "${row.name}"?`, '提示', {
        confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
      }).then(async () => {
        try {
          await request.post(`/api/strategies/${row.id}/toggle`, { status: newStatus })
          this.$message.success('操作成功')
          this.fetchData()
        } catch (e) {
          this.$message.error('操作失败')
        }
      }).catch(() => {})
    }
  }
}
</script>
