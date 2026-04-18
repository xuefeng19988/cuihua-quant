<template>
  <div class="note-editor-container">
    <!-- 顶部工具栏 -->
    <div class="editor-header">
      <div class="header-left">
        <el-button icon="el-icon-back" @click="$router.push('/notes')">返回</el-button>
        <span class="page-title">公众号笔记编辑器</span>
      </div>
      <div class="header-actions">
        <el-button @click="saveDraft" :loading="saving">💾 保存草稿</el-button>
        <el-button type="success" @click="publishArticle" :loading="publishing">🚀 发布</el-button>
        <el-button @click="showPreview">👁️ 预览</el-button>
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
            <span class="stat-label">📅 创建</span>
            <span class="stat-value">{{ article.created_at ? new Date(article.created_at).toLocaleDateString() : '-' }}</span>
          </div>
        </div>
      </div>

      <!-- 中间：编辑器 -->
      <div class="editor-main">
        <div class="editor-mode-switch">
          <el-radio-group v-model="editorMode" size="mini">
            <el-radio-button label="rich">富文本</el-radio-button>
            <el-radio-button label="markdown">Markdown</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 富文本编辑器 -->
        <div v-show="editorMode === 'rich'" class="editor-wrapper">
          <div id="rich-toolbar" style="border:1px solid #dcdfe6;"></div>
          <div id="rich-content" style="border:1px solid #dcdfe6;border-top:none;min-height:600px;overflow-y:auto;"></div>
        </div>

        <!-- Markdown 编辑器 -->
        <div v-show="editorMode === 'markdown'" class="md-editor-wrapper">
          <el-input
            type="textarea"
            v-model="form.content_md"
            :rows="25"
            placeholder="支持 Markdown 语法..."
            style="font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;"
          />
        </div>
      </div>

      <!-- 右侧：快捷操作 -->
      <div class="editor-tools">
        <el-card class="tool-card">
          <div slot="header"><span>📋 快捷操作</span></div>
          <el-button-group style="width:100%;display:flex;flex-wrap:wrap;">
            <el-button size="mini" @click="insertImage">🖼️ 图片</el-button>
            <el-button size="mini" @click="insertVideo">🎬 视频</el-button>
            <el-button size="mini" @click="insertCode">💻 代码</el-button>
            <el-button size="mini" @click="insertTable">📊 表格</el-button>
            <el-button size="mini" @click="insertQuote">💬 引用</el-button>
            <el-button size="mini" @click="insertDivider">➖ 分割线</el-button>
          </el-button-group>
        </el-card>

        <el-card class="tool-card">
          <div slot="header"><span>🎨 排版模板</span></div>
          <el-select v-model="selectedTemplate" placeholder="选择模板" style="width:100%;" @change="applyTemplate">
            <el-option label="默认模板" value="default" />
            <el-option label="研报模板" value="report" />
            <el-option label="新闻模板" value="news" />
            <el-option label="教程模板" value="tutorial" />
          </el-select>
        </el-card>

        <el-card class="tool-card">
          <div slot="header"><span>📊 字数统计</span></div>
          <div class="word-count">
            <div>总字数: <strong>{{ wordCount }}</strong></div>
            <div>中文字数: <strong>{{ chineseWordCount }}</strong></div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 预览对话框 -->
    <el-dialog title="文章预览" :visible.sync="previewVisible" width="60%" top="5vh">
      <div class="preview-content" v-html="previewContent"></div>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
import E from 'wangeditor'

export default {
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
      categories: [],
      availableTags: [],
      selectedTemplate: 'default'
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
    }
  },
  async created() {
    const id = this.$route.params.id
    if (id) {
      this.articleId = id
      await this.loadArticle(id)
    }
    await this.loadCategories()
    await this.loadTags()
  },
  mounted() {
    this.$nextTick(() => this.initEditor())
  },
  methods: {
    initEditor() {
      if (this.editor) { this.editor.destroy(); this.editor = null }
      
      const editor = new E('#rich-toolbar', '#rich-content')
      editor.config.height = 600
      editor.config.uploadImgServer = '/api/notes/upload'
      editor.config.uploadFileName = 'file'
      editor.config.uploadImgHooks = {
        customInsert: (insertImgFn, result) => {
          if (result.code === 200) insertImgFn(result.data.url)
        }
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
      if (this.form.content) editor.txt.html(this.form.content)
      
      // 监听内容变化
      editor.config.onchange = (newHtml) => {
        this.form.content = newHtml
      }
      this.editor = editor
    },
    async loadArticle(id) {
      try {
        const { data } = await request.get(`/api/articles/${id}`)
        if (data.code === 200) {
          this.form = {
            ...data.data,
            tags: Array.isArray(data.data.tags) ? data.data.tags : (data.data.tags ? data.data.tags.split(',') : [])
          }
          if (this.editor && this.form.content) {
            this.editor.txt.html(this.form.content)
          }
        }
      } catch (e) { this.$message.error('加载文章失败') }
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
    insertImage() {
      this.$message.info('请使用编辑器工具栏插入图片')
    },
    insertVideo() {
      this.$message.info('视频功能开发中')
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
    applyTemplate(template) {
      const templates = {
        default: '<h1>标题</h1><p>正文内容...</p>',
        report: '<h2>📊 核心观点</h2><p></p><h2>📈 数据分析</h2><p></p><h2>💡 投资建议</h2><p></p>',
        news: '<h2>📰 事件概述</h2><p></p><h2>🔍 深度分析</h2><p></p><h2>📊 市场影响</h2><p></p>',
        tutorial: '<h2>🎯 目标</h2><p></p><h2>📋 步骤</h2><ol><li></li></ol><h2>💡 注意事项</h2><p></p>'
      }
      if (this.editor && templates[template]) {
        this.editor.txt.html(templates[template])
      }
    }
  }
}
</script>

<style scoped>
.note-editor-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
}

.header-left { display: flex; align-items: center; }
.page-title { font-size: 18px; font-weight: 600; margin-left: 16px; }
.header-actions { display: flex; gap: 8px; }

.editor-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.editor-sidebar {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e6e6e6;
  padding: 16px;
  overflow-y: auto;
}

.editor-main {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.editor-tools {
  width: 240px;
  background: #fff;
  border-left: 1px solid #e6e6e6;
  padding: 16px;
  overflow-y: auto;
}

.tool-card { margin-bottom: 16px; }

.cover-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-image { width: 100%; height: 100%; object-fit: cover; }
.cover-uploader-icon { font-size: 28px; color: #8c939d; }

.editor-stats {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 6px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e6e6e6;
}

.stat-item:last-child { border-bottom: none; }
.stat-label { color: #606266; }
.stat-value { font-weight: 600; }

.editor-mode-switch { margin-bottom: 12px; text-align: center; }

.word-count {
  font-size: 13px;
  color: #606266;
  line-height: 2;
}

.preview-content {
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px;
  line-height: 1.8;
}

.preview-content h1, .preview-content h2, .preview-content h3 { margin: 16px 0 8px; }
.preview-content p { margin: 8px 0; }
.preview-content img { max-width: 100%; }
</style>
