<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>🔍 高级股票筛选器</span>
        <el-button size="mini" style="float:right;" type="primary" @click="screen" :loading="loading">🔍 筛选</el-button>
      </div>
      <el-form :inline="true" size="small">
        <!-- 基础条件 -->
        <el-form-item label="市场">
          <el-select v-model="form.market" style="width:100px;">
            <el-option label="全部" value="" />
            <el-option label="A股" value="A" />
            <el-option label="港股" value="HK" />
          </el-select>
        </el-form-item>
        <el-form-item label="涨跌幅">
          <el-input-number v-model="form.min_change" :min="-10" :max="10" :step="1" style="width:90px;" />
          <span style="margin:0 4px;">~</span>
          <el-input-number v-model="form.max_change" :min="-10" :max="10" :step="1" style="width:90px;" />
        </el-form-item>
        <el-form-item label="成交量">
          <el-input-number v-model="form.min_volume" :step="10000" :min="0" style="width:110px;" />
          <span style="margin:0 4px;">~</span>
          <el-input-number v-model="form.max_volume" :step="10000" :min="0" style="width:110px;" placeholder="不限" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="form.min_price" :min="0" :step="1" style="width:80px;" />
          <span style="margin:0 4px;">~</span>
          <el-input-number v-model="form.max_price" :min="0" :step="1" style="width:80px;" placeholder="不限" />
        </el-form-item>
        <el-form-item label="排序">
          <el-select v-model="form.sort_by" style="width:90px;">
            <el-option label="涨跌幅" value="change" />
            <el-option label="成交量" value="volume" />
            <el-option label="价格" value="price" />
          </el-select>
        </el-form-item>
        <el-form-item label="顺序">
          <el-select v-model="form.sort_order" style="width:80px;">
            <el-option label="降序" value="desc" />
            <el-option label="升序" value="asc" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <div slot="header">
        <span>筛选结果 ({{ total }} 只)</span>
        <el-tag size="mini" style="float:right;">实时</el-tag>
      </div>
      <el-table :data="results" style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="代码" width="110">
          <template slot-scope="{ row }"><el-tag size="small">{{ row.code }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="name" label="名称" width="80" />
        <el-table-column prop="market" label="市场" width="60">
          <template slot-scope="{ row }"><el-tag size="mini" :type="row.market==='A'?'':'info'">{{ row.market }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="price" label="最新价" width="80" />
        <el-table-column prop="change" label="涨跌幅" width="80">
          <template slot-scope="{ row }">
            <span :style="{ color: row.change > 0 ? '#67C23A' : row.change < 0 ? '#F56C6C' : '#909399', fontWeight: 600 }">
              {{ row.change > 0 ? '+' : '' }}{{ row.change }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="100" />
        <el-table-column label="操作" width="100">
          <template slot-scope="{ row }">
            <el-button size="mini" @click="$router.push('/charts?code=' + row.code)">📉 图表</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="results.length === 0 && !loading" description="设置条件后点击筛选" />
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Screener',
  data() {
    return {
      form: {
        market: '',
        min_change: -3,
        max_change: 3,
        min_volume: 0,
        max_volume: null,
        min_price: 0,
        max_price: null,
        sort_by: 'change',
        sort_order: 'desc'
      },
      results: [],
      total: 0,
      loading: false
    }
  },
  methods: {
    async screen() {
      this.loading = true
      try {
        const payload = { ...this.form }
        if (!payload.max_volume) delete payload.max_volume
        if (!payload.max_price) delete payload.max_price
        const { data } = await request.post('/api/screener', payload)
        if (data.code === 200) {
          this.results = data.data.list || []
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
