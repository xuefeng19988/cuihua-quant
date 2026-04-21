<template>
  <div class="note-editor-container">
    <!-- 顶部工具栏 -->
    <div class="editor-header">
      <div class="header-left">
        <el-button icon="el-icon-back" @click="$router.push('/notes')">返回</el-button>
        <span class="page-title">笔记编辑器</span>
      </div>
      <div class="header-actions">
        <el-button @click="saveDraft" :loading="saving">💾 保存草稿</el-button>
        <el-button type="success" @click="publishArticle" :loading="publishing">🚀 发布</el-button>
        <el-button @click="showPreview">👁️ 预览</el-button>
        <el-button @click="showHistory">📜 历史</el-button>
        <el-button @click="shareNote">🔗 分享</el-button>
      </div>
    </div>

    <div class="editor-body">
      <!-- 左侧：文章信息 -->
      <div class="editor-sidebar">
        <el-form label-width="80px" size="small">
          <el-form-item label="文章标题">
            <el-input v-model="form.title" placeholder="请输入文章标题" maxlength="100" show-word-limit />
          </el-form-item>
          <el-form-item label="副标题">
            <el-input v-model="form.subtitle" placeholder="摘要/副标题" maxlength="200" show-word-limit />
          </el-form-item>
          <el-form-item label="作者">
            <el-input v-model="form.author" placeholder="作者名称" />
          </el-form-item>
          <el-form-item label="封面图">
            <el-upload
              class="cover-uploader"
              action="/api/notes/upload"
              :show-file-list="false"
              :on-success="handleCoverSuccess"
              :headers="uploadHeaders"
            >
              <img v-if="form.cover_url" :src="form.cover_url" class="cover-image" />
              <i v-else class="el-icon-plus cover-uploader-icon"></i>
            </el-upload>
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="form.category" placeholder="选择分类" style="width:100%;" allow-create filterable>
              <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
            </el-select>
          </el-form-item>
          <el-form-item label="标签">
            <el-select v-model="form.tags" multiple filterable allow-create default-first-option style="width:100%;" placeholder="输入标签后回车">
              <el-option v-for="t in availableTags" :key="t" :label="t" :value="t" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-radio-group v-model="form.status">
              <el-radio label="draft">草稿</el-radio>
              <el-radio label="published">已发布</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="置顶">
            <el-switch v-model="form.is_top" :active-value="1" :inactive-value="0" />
          </el-form-item>
        </el-form>

        <!-- 统计信息 -->
        <div class="editor-stats" v-if="articleId">
          <div class="stat-item">
            <span class="stat-label">👁️ 浏览</span>
            <span class="stat-value">{{ article.views || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">❤️ 点赞</span>
            <span class="stat-value">{{ article.likes || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">💬 评论</span>
            <span class="stat-value">{{ article.comments || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">📅 创建</span>
            <span class="stat-value">{{ article.created_at ? new Date(article.created_at).toLocaleDateString() : '-' }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">🔄 更新</span>
            <span class="stat-value">{{ article.updated_at ? new Date(article.updated_at).toLocaleDateString() : '-' }}</span>
          </div>
        </div>

        <!-- 关联笔记 -->
        <div class="related-notes" v-if="relatedNotes.length > 0">
          <div class="section-title">🔗 关联笔记</div>
          <div v-for="note in relatedNotes" :key="note.id" class="related-item" @click="editArticle(note)">
            <div class="related-title">{{ note.title }}</div>
            <div class="related-time">{{ note.time }}</div>
          </div>
        </div>
      </div>

      <!-- 中间：编辑器 -->
      <div class="editor-main">
        <div class="editor-mode-switch">
          <el-radio-group v-model="editorMode" size="mini">
            <el-radio-button label="rich">富文本</el-radio-button>
            <el-radio-button label="markdown">Markdown</el-radio-button>
            <el-radio-button label="preview">预览</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 富文本编辑器 -->
        <div v-show="editorMode === 'rich'" class="editor-wrapper">
          <div id="rich-toolbar" style="border:1px solid #dcdfe6;border-radius:4px 4px 0 0;"></div>
          <div id="rich-content" style="border:1px solid #dcdfe6;border-top:none;min-height:600px;overflow-y:auto;border-radius:0 0 4px 4px;"></div>
        </div>

        <!-- Markdown 编辑器 -->
        <div v-show="editorMode === 'markdown'" class="md-editor-wrapper">
          <el-input
            type="textarea"
            v-model="form.content_md"
            :rows="25"
            placeholder="支持 Markdown 语法..."
            style="font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;font-size:14px;line-height:1.6;"
          />
        </div>

        <!-- 预览模式 -->
        <div v-show="editorMode === 'preview'" class="preview-wrapper">
          <div class="preview-content" v-html="sanitizeHTML(previewContent)"></div>
        </div>
      </div>

      <!-- 右侧：编辑器工具 -->
      <div class="editor-tools">
        <el-card class="tool-card">
          <div slot="header"><span>🎨 排版模板</span></div>
          <el-select v-model="selectedTemplate" placeholder="选择模板" style="width:100%;" @change="applyTemplate">
            <el-option label="默认模板" value="default" />
            <el-option label="研报模板" value="report" />
            <el-option label="新闻模板" value="news" />
            <el-option label="教程模板" value="tutorial" />
            <el-option label="会议纪要" value="meeting" />
            <el-option label="知识库" value="wiki" />
          </el-select>
        </el-card>

        <el-card class="tool-card">
          <div slot="header"><span>📊 字数统计</span></div>
          <div class="word-count">
            <div>总字数: <strong>{{ wordCount }}</strong></div>
            <div>中文字数: <strong>{{ chineseWordCount }}</strong></div>
            <div>段落数: <strong>{{ paragraphCount }}</strong></div>
            <div>阅读时间: <strong>{{ readTime }}</strong></div>
          </div>
        </el-card>

        <el-card class="tool-card">
          <div slot="header"><span>🏷️ 热门标签</span></div>
          <div class="hot-tags">
            <el-tag v-for="tag in hotTags" :key="tag.name" size="mini" style="margin:4px;cursor:pointer;" @click="addTag(tag.name)">{{ tag.name }} ({{ tag.count }})</el-tag>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 预览对话框 -->
    <el-dialog title="文章预览" :visible.sync="previewVisible" width="70%" top="5vh">
      <div class="preview-dialog-content" v-html="sanitizeHTML(previewContent)"></div>
    </el-dialog>

    <!-- 历史版本对话框 -->
    <el-dialog title="历史版本" :visible.sync="historyVisible" width="60%">
      <el-timeline>
        <el-timeline-item v-for="version in versions" :key="version.id" :timestamp="version.time" placement="top">
          <el-card>
            <h4>{{ version.title }}</h4>
            <p>{{ version.description }}</p>
            <el-button size="mini" @click="restoreVersion(version)">恢复此版本</el-button>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>

    <!-- 分享对话框 -->
    <el-dialog title="分享笔记" :visible.sync="shareVisible" width="500px">
      <el-form>
        <el-form-item label="分享链接">
          <el-input v-model="shareLink" readonly>
            <el-button slot="append" icon="el-icon-document-copy" @click="copyLink">复制</el-button>
          </el-input>
        </el-form-item>
        <el-form-item label="分享权限">
          <el-radio-group v-model="sharePermission">
            <el-radio label="public">公开</el-radio>
            <el-radio label="private">私密</el-radio>
            <el-radio label="password">密码保护</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="sharePermission === 'password'" label="访问密码">
          <el-input v-model="sharePassword" placeholder="设置访问密码" />
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="shareVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmShare">确认分享</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
import E from 'wangeditor'
import sanitizeMixin from '@/mixins/sanitize'

export default {
  mixins: [sanitizeMixin],
  name: 'NoteEditor',
  data() {
    return {
      articleId: null,
      form: {
        title: '',
        subtitle: '',
        author: '',
        cover_url: '',
        content: '',
        content_md: '',
        tags: [],
        category: '',
        status: 'draft',
        is_top: 0
      },
      editorMode: 'rich',
      editor: null,
      saving: false,
      publishing: false,
      previewVisible: false,
      previewContent: '',
      historyVisible: false,
      shareVisible: false,
      shareLink: '',
      sharePermission: 'public',
      sharePassword: '',
      categories: [],
      availableTags: [],
      selectedTemplate: 'default',
      relatedNotes: [],
      versions: [],
      hotTags: [
        { name: '量化', count: 125 },
        { name: '策略', count: 98 },
        { name: 'Python', count: 87 },
        { name: 'AI', count: 76 },
        { name: '机器学习', count: 65 },
        { name: 'A股', count: 54 },
        { name: '港股', count: 43 },
        { name: '技术分析', count: 38 }
      ],
      article: {}
    }
  },
  computed: {
    uploadHeaders() {
      return { Authorization: `Bearer ${localStorage.getItem('token')}` }
    },
    wordCount() {
      const html = this.editorMode === 'rich' ? (this.editor ? this.editor.txt.text() : '') : this.form.content_md
      return html ? html.length : 0
    },
    chineseWordCount() {
      const text = this.editorMode === 'rich' ? (this.editor ? this.editor.txt.text() : '') : this.form.content_md
      return text ? (text.match(/[\u4e00-\u9fa5]/g) || []).length : 0
    },
    paragraphCount() {
      const text = this.editorMode === 'rich' ? (this.editor ? this.editor.txt.text() : '') : this.form.content_md
      return text ? text.split(/\n\s*\n/).length : 0
    },
    readTime() {
      const minutes = Math.ceil(this.wordCount / 300)
      return minutes < 1 ? '<1分钟' : `${minutes}分钟`
    }
  },
  async created() {
    const id = this.$route.params.id
    if (id) {
      this.articleId = id
      await this.loadArticle(id)
      await this.loadRelatedNotes(id)
      await this.loadVersions(id)
    }
    await this.loadCategories()
    await this.loadTags()
  },
  mounted() {
    this.$nextTick(() => this.initEditor())
  },
  beforeDestroy() {
    if (this.editor) { this.editor.destroy(); this.editor = null }
  },
  methods: {
    initEditor() {
      if (this.editor) { this.editor.destroy(); this.editor = null }
      
      const editor = new E('#rich-toolbar', '#rich-content')
      editor.config.height = 600
      editor.config.customUploadImg = async (resultFiles, insertImgFn) => {
        for (const file of resultFiles) {
          const formData = new FormData()
          formData.append('file', file)
          try {
            const res = await request.post('/notes/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
            if (res.code === 200) insertImgFn(res.data.url)
          } catch (e) { this.$message.error('图片上传失败: ' + (e.message || '未知错误')) }
        }
      }
      editor.create()
      if (this.form.content) editor.txt.html(this.form.content)
      
      editor.config.onchange = (newHtml) => {
        this.form.content = newHtml
      }
      this.editor = editor
    },
    async loadArticle(id) {
      try {
        const { data } = await request.get(`/api/articles/${id}`)
        if (data.code === 200) {
          this.article = data.data
          this.form = {
            ...data.data,
            tags: Array.isArray(data.data.tags) ? data.data.tags : (data.data.tags ? data.data.tags.split(',') : [])
          }
          this.previewContent = this.form.content || '<p style="color:#999;">暂无内容</p>'
          if (this.editor && this.form.content) {
            this.editor.txt.html(this.form.content)
          }
        }
      } catch (e) { this.$message.error('加载文章失败') }
    },
    async loadRelatedNotes(id) {
      try {
        const { data } = await request.get(`/api/articles/${id}/related`)
        if (data.code === 200) {
          this.relatedNotes = data.data.notes || []
        }
      } catch (e) {}
    },
    async loadVersions(id) {
      try {
        const { data } = await request.get(`/api/articles/${id}/versions`)
        if (data.code === 200) {
          this.versions = data.data.versions || []
        }
      } catch (e) {}
    },
    async loadCategories() {
      try {
        const { data } = await request.get('/api/categories')
        if (data.code === 200) this.categories = data.data.categories || []
      } catch (e) {}
    },
    async loadTags() {
      try {
        const { data } = await request.get('/api/notes/tags')
        if (data.code === 200) this.availableTags = data.data.tags || []
      } catch (e) {}
    },
    handleCoverSuccess(res) {
      if (res.code === 200) {
        this.form.cover_url = res.data.url
        this.$message.success('封面图上传成功')
      }
    },
    async saveDraft() {
      this.saving = true
      try {
        const payload = { ...this.form, status: 'draft' }
        if (this.editorMode === 'rich' && this.editor) {
          payload.content = this.editor.txt.html()
        }
        
        let res
        if (this.articleId) {
          res = await request.put(`/api/articles/${this.articleId}`, payload)
        } else {
          res = await request.post('/api/articles', payload)
          this.articleId = res.data.data.id
        }
        this.$message.success('草稿已保存')
      } catch (e) { this.$message.error('保存失败') }
      finally { this.saving = false }
    },
    async publishArticle() {
      if (!this.form.title) return this.$message.warning('请输入文章标题')
      this.publishing = true
      try {
        const payload = { ...this.form, status: 'published' }
        if (this.editorMode === 'rich' && this.editor) {
          payload.content = this.editor.txt.html()
        }
        
        let res
        if (this.articleId) {
          res = await request.put(`/api/articles/${this.articleId}`, payload)
        } else {
          res = await request.post('/api/articles', payload)
          this.articleId = res.data.data.id
        }
        this.$message.success('文章已发布')
        this.$router.push('/notes')
      } catch (e) { this.$message.error('发布失败') }
      finally { this.publishing = false }
    },
    showPreview() {
      this.previewContent = this.form.content || '<p style="color:#999;">暂无内容</p>'
      this.previewVisible = true
    },
    showHistory() {
      this.historyVisible = true
    },
    shareNote() {
      this.shareLink = `${window.location.origin}/share/${this.articleId}`
      this.shareVisible = true
    },
    copyLink() {
      navigator.clipboard.writeText(this.shareLink)
      this.$message.success('链接已复制')
    },
    confirmShare() {
      this.$message.success('分享设置已保存')
      this.shareVisible = false
    },
    restoreVersion(version) {
      this.$confirm('确定恢复此版本？', '提示', { type: 'warning' }).then(async () => {
        try {
          await request.post(`/api/articles/${this.articleId}/restore`, { version_id: version.id })
          this.$message.success('版本已恢复')
          this.historyVisible = false
          this.loadArticle(this.articleId)
        } catch (e) { this.$message.error('恢复失败') }
      }).catch(() => {})
    },
    addTag(tag) {
      if (!this.form.tags.includes(tag)) {
        this.form.tags.push(tag)
      }
    },
    insertImage() {
      if (this.editor) this.editor.cmd.do('insertHTML', '<img src="图片链接" style="max-width:100%;"><p><br/></p>')
    },
    insertVideo() {
      if (this.editor) this.editor.cmd.do('insertHTML', '<video src="视频链接" controls style="max-width:100%;"></video><p><br/></p>')
    },
    insertCode() {
      if (this.editor) this.editor.cmd.do('insertHTML', '<pre><code>代码块</code></pre><p><br/></p>')
    },
    insertTable() {
      if (this.editor) this.editor.cmd.do('insertTable', '3行3列')
    },
    insertQuote() {
      if (this.editor) this.editor.cmd.do('insertHTML', '<blockquote>引用内容</blockquote><p><br/></p>')
    },
    insertDivider() {
      if (this.editor) this.editor.cmd.do('insertHTML', '<hr><p><br/></p>')
    },
    insertLink() {
      if (this.editor) this.editor.cmd.do('insertLink', 'https://')
    },
    insertNote() {
      if (this.editor) this.editor.cmd.do('insertHTML', '<a href="/note/笔记ID" class="note-link">📝 关联笔记</a>')
    },
    applyTemplate(template) {
      const templates = {
        default: '<h1>标题</h1><p>正文内容...</p>',
        report: '<h2>📊 核心观点</h2><p></p><h2>📈 数据分析</h2><p></p><h2>💡 投资建议</h2><p></p>',
        news: '<h2>📰 事件概述</h2><p></p><h2>🔍 深度分析</h2><p></p><h2>📊 市场影响</h2><p></p>',
        tutorial: '<h2>🎯 目标</h2><p></p><h2>📋 步骤</h2><ol><li></li></ol><h2>💡 注意事项</h2><p></p>',
        meeting: '<h2>📅 会议信息</h2><p></p><h2>📝 会议内容</h2><p></p><h2>✅ 待办事项</h2><ul><li></li></ul>',
        wiki: '<h1>知识库标题</h1><h2>概述</h2><p></p><h2>详细说明</h2><p></p><h2>参考资料</h2><ul><li></li></ul>'
      }
      if (this.editor && templates[template]) {
        this.editor.txt.html(templates[template])
      }
    },
    editArticle(article) {
      this.$router.push(`/note-editor/${article.id}`)
    }
  }
}
</script>

<style scoped>
.note-editor-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0f0f1a;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #1a1a2e;
  border-bottom: 1px solid #2a2a3e;
}

.header-left { display: flex; align-items: center; }
.page-title { font-size: 18px; font-weight: 600; margin-left: 16px; color: #d1d4dc; }
.header-actions { display: flex; gap: 8px; }

.editor-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.editor-sidebar {
  width: 280px;
  background: #1a1a2e;
  border-right: 1px solid #2a2a3e;
  padding: 16px;
  overflow-y: auto;
}

.editor-main {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #ffffff;
}

.editor-tools {
  width: 240px;
  background: #1a1a2e;
  border-left: 1px solid #2a2a3e;
  padding: 16px;
  overflow-y: auto;
}

.tool-card { margin-bottom: 16px; background: #2a2a3e; border: none; }
.tool-card ::v-deep .el-card__header { border-bottom: 1px solid #3a3a4e; color: #d1d4dc; }

.cover-uploader {
  border: 1px dashed #3a3a4e;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2a2a3e;
}

.cover-image { width: 100%; height: 100%; object-fit: cover; }
.cover-uploader-icon { font-size: 28px; color: #8c939d; }

.editor-stats {
  margin-top: 20px;
  padding: 16px;
  background: #2a2a3e;
  border-radius: 6px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #3a3a4e;
}

.stat-item:last-child { border-bottom: none; }
.stat-label { color: #909399; }
.stat-value { font-weight: 600; color: #d1d4dc; }

.related-notes {
  margin-top: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
  margin-bottom: 12px;
}

.related-item {
  padding: 8px 0;
  border-bottom: 1px solid #3a3a4e;
  cursor: pointer;
}

.related-item:hover {
  background: #3a3a4e;
}

.related-title {
  font-size: 13px;
  color: #d1d4dc;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.related-time {
  font-size: 11px;
  color: #606266;
  margin-top: 4px;
}

.editor-mode-switch { margin-bottom: 12px; text-align: center; }

.word-count {
  font-size: 13px;
  color: #909399;
  line-height: 2;
}

.hot-tags {
  display: flex;
  flex-wrap: wrap;
}

.preview-dialog-content {
  max-height: 70vh;
  overflow-y: auto;
  padding: 20px;
  line-height: 1.8;
}

.preview-dialog-content h1, .preview-dialog-content h2, .preview-dialog-content h3 { margin: 16px 0 8px; }
.preview-dialog-content p { margin: 8px 0; }
.preview-dialog-content img { max-width: 100%; }
</style>
