<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>🔍 高级股票筛选器</span>
        <el-button size="mini" type="primary" style="float:right;" @click="screen" :loading="loading">🔍 筛选</el-button>
      </div>
      
      <!-- 基础筛选 -->
      <el-form :inline="true" size="small">
        <el-form-item label="市场">
          <el-select v-model="form.market" style="width:100px;">
            <el-option label="全部" value="" />
            <el-option label="A股" value="A" />
            <el-option label="港股" value="HK" />
          </el-select>
        </el-form-item>
        <el-form-item label="板块">
          <el-select v-model="form.sector" placeholder="全部" clearable style="width:120px;">
            <el-option label="白酒" value="白酒" />
            <el-option label="新能源" value="新能源" />
            <el-option label="金融" value="金融" />
            <el-option label="科技" value="科技" />
            <el-option label="医药" value="医药" />
            <el-option label="消费" value="消费" />
          </el-select>
        </el-form-item>
        <el-form-item label="涨跌幅">
          <el-input-number v-model="form.minChange" :min="-10" :max="10" :step="1" style="width:80px;" />
          <span style="margin:0 4px;">~</span>
          <el-input-number v-model="form.maxChange" :min="-10" :max="10" :step="1" style="width:80px;" />
        </el-form-item>
        <el-form-item label="成交量(万)">
          <el-input-number v-model="form.minVolume" :min="0" :step="10" style="width:100px;" />
          <span style="margin:0 4px;">~</span>
          <el-input-number v-model="form.maxVolume" :min="0" :step="10" style="width:100px;" placeholder="不限" />
        </el-form-item>
        <el-form-item><el-button type="primary" @click="screen">筛选</el-button><el-button @click="resetForm">重置</el-button></el-form-item>
      </el-form>

      <!-- 高级筛选 -->
      <el-collapse v-model="activeCollapse">
        <el-collapse-item title="📊 高级筛选条件" name="advanced">
          <el-form :inline="true" size="small">
            <el-form-item label="PE范围">
              <el-input-number v-model="form.minPE" :min="0" :step="5" style="width:80px;" />
              <span style="margin:0 4px;">~</span>
              <el-input-number v-model="form.maxPE" :min="0" :step="5" style="width:80px;" />
            </el-form-item>
            <el-form-item label="PB范围">
              <el-input-number v-model="form.minPB" :min="0" :step="0.5" style="width:80px;" />
              <span style="margin:0 4px;">~</span>
              <el-input-number v-model="form.maxPB" :min="0" :step="0.5" style="width:80px;" />
            </el-form-item>
            <el-form-item label="ROE范围">
              <el-input-number v-model="form.minROE" :min="0" :step="5" style="width:80px;" />
              <span style="margin:0 4px;">~</span>
              <el-input-number v-model="form.maxROE" :min="0" :step="5" style="width:80px;" />
            </el-form-item>
            <el-form-item label="排序">
              <el-select v-model="form.sortBy" style="width:100px;">
                <el-option label="涨跌幅" value="change" />
                <el-option label="成交量" value="volume" />
                <el-option label="PE" value="pe" />
                <el-option label="ROE" value="roe" />
              </el-select>
            </el-form-item>
            <el-form-item label="顺序">
              <el-select v-model="form.sortOrder" style="width:80px;">
                <el-option label="降序" value="desc" />
                <el-option label="升序" value="asc" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <!-- 筛选结果统计 -->
    <el-row :gutter="16" style="margin-bottom:20px;">
      <el-col :span="6"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;font-size:12px;">筛选结果</div><div style="font-size:24px;font-weight:600;">{{ results.length }}</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;font-size:12px;">平均涨跌幅</div><div style="font-size:24px;font-weight:600;" :style="{color: avgChange >= 0 ? '#26a69a' : '#ef5350'}">{{ avgChange >= 0 ? '+' : '' }}{{ avgChange }}%</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;font-size:12px;">平均PE</div><div style="font-size:24px;font-weight:600;">{{ avgPE }}</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover" style="text-align:center;"><div style="color:#909399;font-size:12px;">平均ROE</div><div style="font-size:24px;font-weight:600;">{{ avgROE }}%</div></el-card></el-col>
    </el-row>

    <!-- 结果表格 -->
    <el-card>
      <el-table :data="pagedResults" style="width:100%" v-loading="loading" stripe @row-click="goToDetail">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="code" label="代码" width="110" />
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column prop="price" label="最新价" width="90" />
        <el-table-column prop="change" label="涨跌幅" width="90">
          <template slot-scope="{ row }"><span :style="{ color: row.change > 0 ? '#26a69a' : row.change < 0 ? '#ef5350' : '#909399', fontWeight: 600 }">{{ row.change > 0 ? '+' : '' }}{{ row.change }}%</span></template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="100"><template slot-scope="{ row }">{{ (row.volume/10000).toFixed(0) }}万</template></el-table-column>
        <el-table-column prop="pe" label="PE" width="70" />
        <el-table-column prop="pb" label="PB" width="70" />
        <el-table-column prop="roe" label="ROE" width="70"><template slot-scope="{ row }">{{ row.roe }}%</template></el-table-column>
        <el-table-column prop="sector" label="板块" width="80" />
        <el-table-column label="操作" width="100" fixed="right">
          <template slot-scope="{ row }">
            <el-button size="mini" @click.stop="goToDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:16px;text-align:center;" layout="prev, pager, next" :total="results.length" :page-size="pageSize" :current-page.sync="currentPage" />
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
        market: '', sector: '',
        minChange: -10, maxChange: 10,
        minVolume: 0, maxVolume: null,
        minPE: 0, maxPE: null,
        minPB: 0, maxPB: null,
        minROE: 0, maxROE: null,
        sortBy: 'change', sortOrder: 'desc'
      },
      results: [],
      loading: false,
      currentPage: 1,
      pageSize: 10,
      activeCollapse: []
    }
  },
  computed: {
    pagedResults() {
      const start = (this.currentPage - 1) * this.pageSize
      return this.results.slice(start, start + this.pageSize)
    },
    avgChange() {
      if (this.results.length === 0) return 0
      return (this.results.reduce((sum, r) => sum + r.change, 0) / this.results.length).toFixed(2)
    },
    avgPE() {
      const withPE = this.results.filter(r => r.pe > 0)
      if (withPE.length === 0) return '-'
      return (withPE.reduce((sum, r) => sum + r.pe, 0) / withPE.length).toFixed(1)
    },
    avgROE() {
      const withROE = this.results.filter(r => r.roe > 0)
      if (withROE.length === 0) return '-'
      return (withROE.reduce((sum, r) => sum + r.roe, 0) / withROE.length).toFixed(1)
    }
  },
  methods: {
    async screen() {
      this.loading = true
      this.currentPage = 1
      try {
        const { data } = await request.post('/screener', this.form)
        if (data.code === 200) {
          this.results = data.data.list || []
          if (this.form.sortBy) {
            this.results.sort((a, b) => {
              const va = a[this.form.sortBy] || 0
              const vb = b[this.form.sortBy] || 0
              return this.form.sortOrder === 'desc' ? vb - va : va - vb
            })
          }
        }
      } catch (e) { this.$message.error('筛选失败') }
      finally { this.loading = false }
    },
    resetForm() {
      this.form = {
        market: '', sector: '',
        minChange: -10, maxChange: 10,
        minVolume: 0, maxVolume: null,
        minPE: 0, maxPE: null,
        minPB: 0, maxPB: null,
        minROE: 0, maxROE: null,
        sortBy: 'change', sortOrder: 'desc'
      }
    },
    goToDetail(row) { this.$router.push(`/stock-detail/${row.code}`) }
  }
}
</script>

<style scoped>
.app-container { background: #0f0f1a; min-height: 100vh; padding: 16px; }
.el-card { background: #1a1a2e !important; border: 1px solid #2a2a3e !important; }
.el-card__header { border-bottom: 1px solid #2a2a3e !important; }
</style>
