<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>🔍 股票筛选器</span>
        <el-button size="mini" style="float:right;" type="primary" @click="screen" :loading="loading">🔍 筛选</el-button>
      </div>
      <el-form :inline="true">
        <el-form-item label="涨跌幅范围">
          <el-input-number v-model="form.minChange" :min="-10" :max="10" :step="1" style="width: 100px;" />
          <span style="margin: 0 8px;">~</span>
          <el-input-number v-model="form.maxChange" :min="-10" :max="10" :step="1" style="width: 100px;" />
        </el-form-item>
        <el-form-item label="最小成交量"><el-input-number v-model="form.minVolume" :step="10000" :min="0" style="width: 150px;" /></el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <div slot="header">
        <span>筛选结果 ({{ total }} 只)</span>
        <el-tag size="mini" style="float:right;">实时</el-tag>
      </div>
      <el-table :data="results" style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="代码" width="110"><template slot-scope="{ row }"><el-tag size="small">{{ row.code }}</el-tag></template></el-table-column>
        <el-table-column prop="name" label="名称" width="80" />
        <el-table-column prop="price" label="最新价" width="80" />
        <el-table-column prop="change" label="涨跌幅" width="80">
          <template slot-scope="{ row }"><span :style="{ color: row.change > 0 ? '#67C23A' : row.change < 0 ? '#F56C6C' : '#909399', fontWeight: 600 }">{{ row.change > 0 ? '+' : '' }}{{ row.change }}%</span></template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="100" />
        <el-table-column label="操作" width="100">
          <template slot-scope="{ row }">
            <el-button size="mini" @click="$router.push('/charts?code=' + row.code)">📉 图表</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="results.length === 0" description="点击"筛选"开始选股" />
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Screener',
  data() {
    return { form: { minChange: -3, maxChange: 3, minVolume: 0 }, results: [], total: 0, loading: false }
  },
  methods: {
    async screen() {
      this.loading = true
      try {
        const { data } = await request.post('/api/screener', this.form)
        if (data.code === 200) {
          this.results = data.data.results || []
          this.total = data.data.total || 0
        }
      } catch (e) {
        this.$message.error('筛选失败: ' + e.message)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
