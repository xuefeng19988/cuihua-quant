<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>🌍 美股/港股数据</span><el-button size="mini" style="float:right;" @click="fetchData" :loading="loading">🔄 刷新</el-button></div></el-card>
    <el-row :gutter="20">
      <el-col :span="12"><el-card><div slot="header"><span>🇭🇰 港股</span></div>
        <el-table :data="data.hk_stocks"><el-table-column prop="code" label="代码" /><el-table-column prop="name" label="名称" /><el-table-column prop="price" label="价格" /><el-table-column prop="change" label="涨跌幅"><template slot-scope="{ row }"><span :style="{color:row.change>0?'#67C23A':'#F56C6C'}">{{ row.change>0?'+':'' }}{{ row.change }}%</span></template></el-table-column></el-table>
      </el-card></el-col>
      <el-col :span="12"><el-card><div slot="header"><span>🇺🇸 美股</span></div>
        <el-table :data="data.us_stocks"><el-table-column prop="code" label="代码" /><el-table-column prop="name" label="名称" /><el-table-column prop="price" label="价格" /><el-table-column prop="change" label="涨跌幅"><template slot-scope="{ row }"><span :style="{color:row.change>0?'#67C23A':'#F56C6C'}">{{ row.change>0?'+':'' }}{{ row.change }}%</span></template></el-table-column></el-table>
      </el-card></el-col>
    </el-row>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'UsHkData', data() { return { data: { hk_stocks: [], us_stocks: [] }, loading: false } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try { const { data } = await request.get('/api/us-hk-data'); if (data.code === 200) this.data = data.data }
      catch (e) { this.$message.error('获取数据失败') }
      finally { this.loading = false }
    }
  }
}
</script>
