<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📈 期权策略分析</span><el-select v-model="underlying" size="mini" style="float:right;width:150px;" @change="fetchData"><el-option label="50ETF" value="510050.SH" /></el-select></div></el-card>
    <el-row :gutter="20">
      <el-col :span="12"><el-card><div slot="header"><span>📊 看涨期权 (Calls)</span></div><el-table :data="options.calls"><el-table-column prop="strike" label="行权价" /><el-table-column prop="bid" label="买入价" /><el-table-column prop="ask" label="卖出价" /><el-table-column prop="volume" label="成交量" /><el-table-column prop="oi" label="持仓量" /></el-table></el-card></el-col>
      <el-col :span="12"><el-card><div slot="header"><span>📊 看跌期权 (Puts)</span></div><el-table :data="options.puts"><el-table-column prop="strike" label="行权价" /><el-table-column prop="bid" label="买入价" /><el-table-column prop="ask" label="卖出价" /><el-table-column prop="volume" label="成交量" /><el-table-column prop="oi" label="持仓量" /></el-table></el-card></el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'OptionStrategy', data() { return { underlying: '510050.SH', options: { calls: [], puts: [] } } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try { const { data } = await request.get('/option-chain', { params: { underlying: this.underlying } }); if (data.code === 200) this.options = data.data }
      catch (e) { this.$message.error('获取期权链失败') }
    }
  }
}
</script>
