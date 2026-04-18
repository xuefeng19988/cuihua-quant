<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>💾 备份管理</span>
        <div style="float:right;">
          <el-button size="mini" type="primary" @click="createBackup" :loading="creating">📦 创建备份</el-button>
          <el-upload :show-file-list="false" :http-request="uploadBackup" accept=".zip" style="display:inline-block;margin-left:8px;">
            <el-button size="mini" type="success">📤 上传备份</el-button>
          </el-upload>
        </div>
      </div>
    </el-card>

    <!-- 备份说明 -->
    <el-alert title="备份包含：股票配置、笔记数据、系统配置等" type="info" :closable="false" style="margin-bottom:16px;" />

    <!-- 备份列表 -->
    <el-card>
      <div slot="header"><span>📋 备份列表</span></div>
      <el-table :data="backups" style="width:100%" v-loading="loading" stripe>
        <el-table-column prop="name" label="备份名称" min-width="200" />
        <el-table-column prop="size_mb" label="大小" width="100">
          <template slot-scope="{ row }">{{ row.size_mb }} MB</template>
        </el-table-column>
        <el-table-column label="包含内容" min-width="200">
          <template slot-scope="{ row }">
            <el-tag v-for="t in (row.tables || [])" :key="t" size="mini" type="success" style="margin:2px;">📋 {{ t }}</el-tag>
            <el-tag v-for="f in (row.files || [])" :key="f" size="mini" type="warning" style="margin:2px;">⚙️ {{ f }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template slot-scope="{ row }">{{ new Date(row.created_at).toLocaleString('zh-CN') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template slot-scope="{ row }">
            <el-button size="mini" @click="downloadBackup(row)">📥 下载</el-button>
            <el-button size="mini" type="warning" @click="restoreBackup(row)" :disabled="row.uploaded">🔄 恢复</el-button>
            <el-button size="mini" type="danger" @click="deleteBackup(row)">🗑️</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination style="margin-top:16px;text-align:center;"
        layout="prev, pager, next, total" :total="total" :page-size="10"
        :current-page.sync="page" @current-change="fetchBackups" />
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'BackupManager',
  data() { return { backups: [], total: 0, page: 1, loading: false, creating: false } },
  created() { this.fetchBackups() },
  methods: {
    async fetchBackups() {
      this.loading = true
      try {
        const { data } = await request.get('/api/backup/list', { params: { page: this.page, per_page: 10 } })
        if (data.code === 200) { this.backups = data.data.backups; this.total = data.data.total }
      } catch (e) { this.$message.error('获取备份列表失败') }
      finally { this.loading = false }
    },
    async createBackup() {
      this.creating = true
      try {
        const { data } = await request.post('/api/backup/create')
        if (data.code === 200) { this.$message.success(`备份创建成功 (${data.data.size_mb}MB)`); this.fetchBackups() }
      } catch (e) { this.$message.error('备份失败') }
      finally { this.creating = false }
    },
    async uploadBackup({ file }) {
      const formData = new FormData()
      formData.append('file', file)
      try {
        await request.post('/api/backup/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
        this.$message.success('备份上传成功')
        this.fetchBackups()
      } catch (e) { this.$message.error('上传失败') }
    },
    downloadBackup(row) {
      window.open(`/api/backup/download/${row.filename}?token=${localStorage.getItem('token')}`)
    },
    async restoreBackup(row) {
      try {
        await this.$confirm(`确定要恢复备份 "${row.name}" 吗？当前数据将被覆盖！`, '警告', { type: 'warning' })
        const { data } = await request.post(`/api/backup/restore/${row.filename}`)
        if (data.code === 200) { this.$message.success('备份恢复成功'); this.$router.push('/notes') }
      } catch (e) { if (e !== 'cancel') this.$message.error('恢复失败') }
    },
    async deleteBackup(row) {
      try {
        await this.$confirm(`确定删除备份 "${row.name}" 吗？`, '提示', { type: 'warning' })
        await request.delete(`/api/backup/delete/${row.filename}`)
        this.$message.success('备份删除成功')
        this.fetchBackups()
      } catch (e) {}
    }
  }
}
</script>
