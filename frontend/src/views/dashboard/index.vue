<template>
  <div class="dashboard-container">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="item in stats" :key="item.label">
        <el-card shadow="hover">
          <div style="display: flex; align-items: center;">
            <div style="font-size: 36px; margin-right: 16px;">{{ item.icon }}</div>
            <div>
              <div style="color: #909399; font-size: 13px;">{{ item.label }}</div>
              <div style="font-size: 24px; font-weight: 600; color: #303133;">{{ item.value }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="12">
        <el-card>
          <div slot="header"><span style="color: #67C23A;">📈 涨幅 Top 5</span></div>
          <el-table :data="gainers" size="small">
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="price" label="价格" width="80" />
            <el-table-column prop="change" label="涨跌" width="80">
              <template slot-scope="{ row }"><span style="color: #67C23A; font-weight: 600;">+{{ row.change }}%</span></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header"><span style="color: #F56C6C;">📉 跌幅 Top 5</span></div>
          <el-table :data="losers" size="small">
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="price" label="价格" width="80" />
            <el-table-column prop="change" label="涨跌" width="80">
              <template slot-scope="{ row }"><span style="color: #F56C6C; font-weight: 600;">{{ row.change }}%</span></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <div slot="header"><span>🚀 快速导航</span></div>
      <el-row :gutter="16">
        <el-col :span="4" v-for="item in quickLinks" :key="item.name">
          <div style="text-align: center; padding: 16px 0; cursor: pointer;" @click="$router.push(item.path)">
            <div style="font-size: 32px;">{{ item.icon }}</div>
            <div style="margin-top: 8px; color: #606266;">{{ item.name }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Dashboard',
  data() {
    return {
      stats: [
        { icon: '✅', label: '系统状态', value: '加载中...' },
        { icon: '📊', label: '总收益', value: '--' },
        { icon: '💰', label: '仓位', value: '--' },
        { icon: '💎', label: '总资产', value: '--' }
      ],
      gainers: [],
      losers: [],
      quickLinks: [
        { name: '股票池', icon: '💼', path: '/stocks' },
        { name: '信号分析', icon: '📈', path: '/analysis' },
        { name: '回测中心', icon: '🔬', path: '/backtest' },
        { name: '图表分析', icon: '📉', path: '/charts' },
        { name: '投资组合', icon: '🌍', path: '/portfolio' },
        { name: '热力图', icon: '🔥', path: '/heatmap' }
      ]
    }
  },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try {
        const { data } = await request.get('/dashboard')
        if (data.code === 200) {
          const d = data.data
          // 系统状态
          this.stats[0].value = '运行中'
          // 持仓信息
          if (d.portfolio_summary) {
            const ps = d.portfolio_summary
            this.stats[1].value = `收益 ¥${(ps.total_pnl / 10000).toFixed(1)}万`
            this.stats[2].value = `${ps.position_ratio}%`
            this.stats[3].value = `¥${(ps.total_value / 10000).toFixed(1)}万`
          }
          // 涨跌榜
          this.gainers = (d.top_gainers || []).map(g => ({ code: g.code, name: g.name, price: '-', change: g.change.toFixed(2) }))
          this.losers = (d.top_losers || []).map(l => ({ code: l.code, name: l.name, price: '-', change: l.change.toFixed(2) }))
        }
      } catch (e) {
        this.stats[0].value = '连接失败'
      }
    }
  }
}
</script>
