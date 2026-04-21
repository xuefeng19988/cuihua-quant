<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>📈 信号分析</span><el-button size="mini" style="float:right;" type="primary" @click="refresh" :loading="loading">🔄 刷新信号</el-button></div>
    </el-card>
    <el-table :data="signals" style="width: 100%" v-loading="loading">
      <el-table-column prop="rank" label="排名" width="60" />
      <el-table-column prop="code" label="代码" width="110" />
      <el-table-column prop="name" label="名称" width="80" />
      <el-table-column prop="signal" label="信号" width="80"><template slot-scope="{ row }"><el-tag :type="row.signal === 'buy' ? 'success' : 'warning'" size="mini">{{ row.signal === 'buy' ? '买入' : '持有' }}</el-tag></template></el-table-column>
      <el-table-column prop="score" label="得分" width="70" />
      <el-table-column prop="price" label="价格" width="80" />
      <el-table-column prop="reason" label="原因" />
    </el-table>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Analysis',
  data() { return { signals: [], loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await request.get('/signals')
        if (data.code === 200) this.signals = data.data.signals || []
      } catch (e) { this.$message.error('获取信号失败') }
      finally { this.loading = false }
    },
    refresh() { this.fetchData() }
  }
}
</script>
