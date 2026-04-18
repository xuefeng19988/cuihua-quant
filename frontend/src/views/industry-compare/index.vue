<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📊 行业对比分析</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div></el-card>
    <el-row :gutter="20">
      <el-col :span="12" v-for="ind in industries" :key="ind.industry">
        <el-card shadow="hover">
          <div slot="header"><span>{{ ind.industry }} <el-tag size="mini" :type="ind.avg_change>0?'success':'danger'">{{ ind.avg_change>0?'+':'' }}{{ ind.avg_change }}%</el-tag></span></div>
          <el-table :data="ind.stocks" size="mini">
            <el-table-column prop="code" label="代码" width="110" /><el-table-column prop="name" label="名称" />
            <el-table-column prop="change" label="涨跌幅" width="80"><template slot-scope="{ row }"><span :style="{color:row.change>0?'#67C23A':'#F56C6C'}">{{ row.change>0?'+':'' }}{{ row.change }}%</span></template></el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'IndustryCompare', data() { return { industries: [], loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try { const { data } = await request.get('/api/industry-compare'); if (data.code === 200) this.industries = data.data.industries }
      catch (e) { this.$message.error('获取数据失败') }
      finally { this.loading = false }
    }
  }
}
</script>
