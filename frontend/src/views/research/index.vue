<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📓 研究笔记本</span><el-button size="mini" style="float:right;" type="primary" @click="newNote">➕ 新建</el-button></div></el-card>
    <el-row :gutter="20">
      <el-col :span="8" v-for="note in notes" :key="note.title">
        <el-card shadow="hover" style="margin-bottom:16px;cursor:pointer;" @click="$message.info('打开: ' + note.title)">
          <div style="font-weight:600;margin-bottom:8px;">{{ note.title }}</div>
          <div style="color:#909399;font-size:12px;margin-bottom:8px;">{{ note.date }}</div>
          <el-tag v-for="t in note.tags" :key="t" size="mini" style="margin-right:4px;">{{ t }}</el-tag>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script>
import request from '@/utils/request'
export default { name: 'Research', data() { return { notes: [] } },
  created() { this.fetchData() },
  methods: {
    async fetchData() {
      try {
        const { data } = await request.get('/research')
        if (data.code === 200) this.notes = data.data.notes || []
      } catch (e) { this.$message.error('获取研究笔记失败') }
    },
    newNote() { this.$message.info('创建新研究笔记') }
  }
}
</script>
