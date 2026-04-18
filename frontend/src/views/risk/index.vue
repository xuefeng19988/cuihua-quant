<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="m in cards" :key="m.label">
        <el-card shadow="hover">
          <div style="color:#909399;font-size:13px;">{{ m.label }}</div>
          <div :style="{ fontSize: '20px', fontWeight: 600, marginTop: '8px', color: m.color || '#303133' }">{{ m.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <div slot="header"><span>🛡️ 风险指标详情</span></div>
          <el-table :data="indicators" style="width: 100%">
            <el-table-column prop="name" label="指标" />
            <el-table-column prop="value" label="当前值" width="120" />
            <el-table-column prop="threshold" label="阈值" width="100" />
            <el-table-column label="状态" width="100">
              <template slot-scope="{ row }">
                <el-tag :type="row.status === 'normal' ? 'success' : row.status === 'warning' ? 'warning' : 'danger'" size="small">
                  {{ row.statusText }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📈 持仓集中度</span></div>
          <el-table :data="concentration" style="width: 100%">
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="80" />
            <el-table-column prop="weight" label="权重" width="80">
              <template slot-scope="{ row }">{{ row.weight }}%</template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template slot-scope="{ row }">
                <el-tag :type="row.weight > 20 ? 'danger' : row.weight > 15 ? 'warning' : 'success'" size="mini">
                  {{ row.weight > 20 ? '超限' : row.weight > 15 ? '预警' : '正常' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'Risk',
  data() {
    return {
      cards: [
        { label: 'VaR (95%)', value: '--', color: '#303133' },
        { label: 'CVaR (95%)', value: '--', color: '#303133' },
        { label: '最大回撤', value: '--', color: '#303133' },
        { label: '年化波动率', value: '--', color: '#303133' }
      ],
      indicators: [],
      concentration: []
    }
  },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try {
        const { data } = await request.get('/api/risk')
        if (data.code === 200) {
          const r = data.data
          // Update cards
          this.cards = [
            { label: 'VaR (95%)', value: r.var_95 || '--', color: r.var_status === 'warning' ? '#E6A23C' : '#303133' },
            { label: 'CVaR (95%)', value: r.cvar_95 || '--', color: r.cvar_status === 'warning' ? '#E6A23C' : '#303133' },
            { label: '最大回撤', value: r.max_drawdown || '--', color: r.drawdown_status === 'warning' ? '#E6A23C' : '#303133' },
            { label: '年化波动率', value: r.volatility || '--', color: r.vol_status === 'warning' ? '#E6A23C' : '#303133' }
          ]
          this.indicators = r.indicators || []
          this.concentration = r.concentration || []
        }
      } catch (e) {
        this.$message.error('获取风险数据失败: ' + e.message)
      }
    }
  }
}
</script>
