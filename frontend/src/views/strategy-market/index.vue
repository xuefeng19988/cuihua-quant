<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📈 量化策略市场</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div></el-card>
    <el-row :gutter="20">
      <el-col :span="12" v-for="s in strategies" :key="s.name">
        <el-card shadow="hover">
          <div slot="header"><span>{{ s.name }} <el-tag size="mini" type="success">{{ s.author }}</el-tag></span></div>
          <el-row :gutter="10">
            <el-col :span="6"><div style="text-align:center;"><div style="color:#909399;font-size:12px;">年化收益</div><div style="font-size:18px;font-weight:600;color:#67C23A;">{{ s.annual_return }}%</div></div></el-col>
            <el-col :span="6"><div style="text-align:center;"><div style="color:#909399;font-size:12px;">最大回撤</div><div style="font-size:18px;font-weight:600;color:#F56C6C;">{{ s.max_drawdown }}%</div></div></el-col>
            <el-col :span="6"><div style="text-align:center;"><div style="color:#909399;font-size:12px;">夏普比率</div><div style="font-size:18px;font-weight:600;">{{ s.sharpe }}</div></div></el-col>
            <el-col :span="6"><div style="text-align:center;"><div style="color:#909399;font-size:12px;">订阅数</div><div style="font-size:18px;font-weight:600;">{{ s.subscribers }}</div></div></el-col>
          </el-row>
          <el-button type="primary" size="mini" style="margin-top:12px;width:100%;">订阅策略</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'StrategyMarket', data() { return { strategies: [], loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try { const { data } = await request.get('/api/strategy-market'); if (data.code === 200) this.strategies = data.data.strategies }
      catch (e) { this.$message.error('获取数据失败') }
      finally { this.loading = false }
    }
  }
}
</script>
