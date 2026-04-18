<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>🔍 数据质量检查</span>
        <el-button size="mini" type="primary" @click="checkQuality" :loading="loading" style="float:right;">🔄 开始检查</el-button>
      </div>
    </el-card>

    <!-- 质量概览 -->
    <el-row :gutter="20" v-if="qualityScore >= 0">
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="color:#909399;font-size:13px;">质量评分</div>
          <div style="font-size:28px;font-weight:600;margin-top:8px;" :style="{color: qualityScore >= 80 ? '#67C23A' : qualityScore >= 60 ? '#E6A23C' : '#F56C6C'}">
            {{ qualityScore }}分
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="color:#909399;font-size:13px;">检查股票数</div>
          <div style="font-size:28px;font-weight:600;margin-top:8px;">{{ stocksChecked }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="color:#909399;font-size:13px;">数据记录数</div>
          <div style="font-size:28px;font-weight:600;margin-top:8px;">{{ totalRecords.toLocaleString() }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="color:#909399;font-size:13px;">问题总数</div>
          <div style="font-size:28px;font-weight:600;margin-top:8px;" :style="{color: totalIssues > 0 ? '#F56C6C' : '#67C23A'}">{{ totalIssues }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 问题严重性分布 -->
    <el-card v-if="severityCount.high + severityCount.medium + severityCount.low > 0" style="margin-top:20px;">
      <div slot="header"><span>⚠️ 问题分布</span></div>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-tag size="medium" type="danger" style="width:100%;text-align:center;padding:12px;">
            🔴 严重: {{ severityCount.high }}
          </el-tag>
        </el-col>
        <el-col :span="8">
          <el-tag size="medium" type="warning" style="width:100%;text-align:center;padding:12px;">
            🟡 中等: {{ severityCount.medium }}
          </el-tag>
        </el-col>
        <el-col :span="8">
          <el-tag size="medium" type="info" style="width:100%;text-align:center;padding:12px;">
            🔵 轻微: {{ severityCount.low }}
          </el-tag>
        </el-col>
      </el-row>
    </el-card>

    <!-- 问题列表 -->
    <el-card v-if="issues.length > 0" style="margin-top:20px;">
      <div slot="header"><span>📋 问题详情</span></div>
      <el-table :data="issues" style="width:100%">
        <el-table-column prop="code" label="股票代码" width="120" />
        <el-table-column prop="issue" label="问题描述" />
        <el-table-column prop="severity" label="严重程度" width="100">
          <template slot-scope="{ row }">
            <el-tag size="mini" :type="row.severity === 'high' ? 'danger' : row.severity === 'medium' ? 'warning' : 'info'">
              {{ row.severity === 'high' ? '严重' : row.severity === 'medium' ? '中等' : '轻微' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-empty v-if="issues.length === 0 && qualityScore >= 0 && totalIssues === 0" description="✅ 数据质量良好，未发现明显问题" />
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'DataQuality',
  data() {
    return {
      qualityScore: -1,
      stocksChecked: 0,
      totalRecords: 0,
      totalIssues: 0,
      severityCount: { high: 0, medium: 0, low: 0 },
      issues: [],
      loading: false
    }
  },
  created() { this.checkQuality() },
  methods: {
    async checkQuality() {
      this.loading = true
      try {
        const { data } = await request.get('/api/data-quality')
        if (data.code === 200) {
          const d = data.data
          this.qualityScore = d.quality_score
          this.stocksChecked = d.stocks_checked
          this.totalRecords = d.total_records
          this.totalIssues = d.total_issues
          this.severityCount = d.severity_count || { high: 0, medium: 0, low: 0 }
          this.issues = d.issues || []
        }
      } catch (e) { this.$message.error('数据质量检查失败') }
      finally { this.loading = false }
    }
  }
}
</script>
