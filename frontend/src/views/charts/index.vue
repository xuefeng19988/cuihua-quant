<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>📉 图表分析</span>
      </div>
      <el-form :inline="true">
        <el-form-item label="股票"><el-select v-model="form.code" size="small" style="width:160px;"><el-option v-for="s in stocks" :key="s.code" :label="s.code + ' ' + s.name" :value="s.code" /></el-select></el-form-item>
        <el-form-item label="天数"><el-select v-model="form.days" size="small"><el-option :value="30" label="30天" /><el-option :value="60" label="60天" /><el-option :value="90" label="90天" /><el-option :value="180" label="180天" /></el-select></el-form-item>
        <el-form-item><el-button size="small" type="primary" @click="loadChart" :loading="loading">📊 生成</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card v-loading="loading">
      <div v-html="chartHtml" />
      <el-empty v-if="!chartHtml && !loading" description="选择股票后点击生成" />
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Charts',
  data() { return { form: { code: 'SH.600519', days: 60 }, stocks: [], chartHtml: '', loading: false } },
  created() { this.fetchStocks() },
  methods: {
    async fetchStocks() {
      try {
        const { data } = await request.get('/api/stocks')
        if (data.code === 200) this.stocks = data.data.list || []
      } catch (e) {}
    },
    async loadChart() {
      this.loading = true
      try {
        const { data } = await request.get('/api/charts', { params: this.form })
        if (data.code === 200) this.chartHtml = data.data.html || ''
      } catch (e) { this.$message.error('生成图表失败') }
      finally { this.loading = false }
    }
  }
}
</script>
