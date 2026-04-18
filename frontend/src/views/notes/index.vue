<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>📝 笔记管理</span>
        <div style="float:right;">
          <el-button size="mini" type="primary" @click="openEditor()">➕ 新建笔记</el-button>
        </div>
      </div>
      <el-form :inline="true" size="small">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="搜索标题/内容..." clearable style="width:200px;" @keyup.enter.native="fetchNotes" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="query.tag" placeholder="全部标签" clearable style="width:150px;" @change="fetchNotes">
            <el-option v-for="t in tags" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchNotes">🔍 查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 笔记列表 -->
    <el-card>
      <el-table :data="notes" style="width:100%" v-loading="loading" stripe>
        <el-table-column type="expand">
          <template slot-scope="{ row }">
            <div style="padding:16px;" v-html="row.content"></div>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="source" label="来源" width="120" />
        <el-table-column prop="date" label="日期" width="160" />
        <el-table-column label="标签" width="150">
          <template slot-scope="{ row }">
            <el-tag v-for="t in row.tags" :key="t" size="mini" style="margin:2px;">{{ t }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template slot-scope="{ row }">
            <el-button size="mini" type="primary" @click="openEditor(row)">✏️ 编辑</el-button>
            <el-button size="mini" type="danger" @click="deleteNote(row)">🗑️</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination style="margin-top:16px;text-align:center;"
        layout="prev, pager, next, total" :total="total" :page-size="10"
        :current-page.sync="page" @current-change="fetchNotes" />
    </el-card>

    <!-- 笔记编辑器对话框 -->
    <el-dialog :title="editingNote ? '编辑笔记' : '新建笔记'" :visible.sync="editorVisible" width="80%" top="5vh">
      <el-form :model="noteForm" label-width="80px">
        <el-form-item label="标题"><el-input v-model="noteForm.title" placeholder="请输入标题" /></el-form-item>
        <el-form-item label="来源"><el-input v-model="noteForm.source" placeholder="如：财联社、36氪" /></el-form-item>
        <el-form-item label="标签">
          <el-select v-model="noteForm.tags" multiple filterable allow-create default-first-option style="width:100%;" placeholder="输入标签后回车添加">
            <el-option v-for="t in tags" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <div id="editor-toolbar" style="border:1px solid #ccc;"></div>
          <div id="editor-content" style="border:1px solid #ccc;border-top:none;height:400px;overflow-y:auto;"></div>
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="editorVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNote" :loading="saving">💾 保存</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
import E from 'wangeditor'

export default {
  name: 'Notes',
  data() {
    return {
      notes: [],
      total: 0,
      page: 1,
      tags: [],
      query: { keyword: '', tag: '' },
      loading: false,
      editorVisible: false,
      editingNote: null,
      noteForm: { title: '', source: '', tags: [], content: '' },
      editor: null,
      saving: false
    }
  },
  created() { this.fetchNotes(); this.fetchTags() },
  methods: {
    async fetchNotes() {
      this.loading = true
      try {
        const { data } = await request.get('/api/notes', { params: { page: this.page, per_page: 10, ...this.query } })
        if (data.code === 200) { this.notes = data.data.notes; this.total = data.data.total }
      } catch (e) { this.$message.error('获取笔记失败') }
      finally { this.loading = false }
    },
    async fetchTags() {
      try {
        const { data } = await request.get('/api/notes/tags')
        if (data.code === 200) this.tags = data.data.tags || []
      } catch (e) {}
    },
    openEditor(note = null) {
      this.editingNote = note
      this.noteForm = note ? { ...note } : { title: '', source: '', tags: [], content: '' }
      this.editorVisible = true
      this.$nextTick(() => this.initEditor())
    },
    initEditor() {
      if (this.editor) { this.editor.destroy(); this.editor = null }

      const editor = new E('#editor-toolbar', '#editor-content')
      editor.config.uploadImgServer = '/api/notes/upload'
      editor.config.uploadFileName = 'file'
      editor.config.uploadImgHooks = {
        customInsert: (insertImgFn, result) => {
          if (result.code === 200) insertImgFn(result.data.url)
        }
      }
      editor.config.uploadImgMaxSize = 10 * 1024 * 1024 // 10MB
      editor.config.uploadImgAccept = ['jpg', 'jpeg', 'png', 'gif', 'webp']
      // 粘贴图片
      editor.config.pasteFilterStyle = false
      editor.config.pasteIgnoreImg = false
      editor.config.customPaste = (editor, event) => {
        // 允许粘贴图片
        return true
      }

      editor.config.customUploadImg = async (resultFiles, insertImgFn) => {
        for (const file of resultFiles) {
          const formData = new FormData()
          formData.append('file', file)
          try {
            const res = await request.post('/api/notes/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
            if (res.data.code === 200) insertImgFn(res.data.data.url)
          } catch (e) { this.$message.error('图片上传失败') }
        }
      }

      editor.create()
      if (this.noteForm.content) editor.txt.html(this.noteForm.content)
      this.editor = editor
    },
    async saveNote() {
      if (!this.noteForm.title) return this.$message.warning('请输入标题')
      this.saving = true
      try {
        const content = this.editor ? this.editor.txt.html() : ''
        const payload = { ...this.noteForm, content }

        if (this.editingNote) {
          await request.put(`/api/notes/${this.editingNote.id}`, payload)
          this.$message.success('笔记更新成功')
        } else {
          await request.post('/api/notes', payload)
          this.$message.success('笔记创建成功')
        }
        this.editorVisible = false
        this.fetchNotes()
      } catch (e) { this.$message.error('保存失败') }
      finally { this.saving = false }
    },
    async deleteNote(row) {
      try {
        await this.$confirm('确定删除该笔记？', '提示', { type: 'warning' })
        await request.delete(`/api/notes/${row.id}`)
        this.$message.success('删除成功')
        this.fetchNotes()
      } catch (e) {}
    },
    resetQuery() {
      this.query = { keyword: '', tag: '' }
      this.page = 1
      this.fetchNotes()
    }
  }
}
</script>
