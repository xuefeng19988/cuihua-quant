<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header"><span>🎨 主题切换</span></div>
      <el-switch v-model="isDark" active-text="暗色模式" inactive-text="亮色模式" @change="toggleTheme" />
      <span style="margin-left:12px;color:#909399;font-size:12px;">当前: {{ isDark ? '暗色' : '亮色' }}</span>
    </el-card>
    <el-card>
      <div slot="header"><span>🎯 主题预览</span></div>
      <el-row :gutter="20">
        <el-col :span="8" v-for="theme in themes" :key="theme.value">
          <el-card shadow="hover" :class="['theme-preview-card', { active: currentTheme === theme.value }]" @click="applyTheme(theme)">
            <div class="preview-content" :class="theme.value === 'dark' ? 'preview-dark' : 'preview-light'">
              <div class="preview-header"></div>
              <div class="preview-sidebar"></div>
              <div class="preview-body">
                <div class="preview-card-item"></div>
                <div class="preview-card-item"></div>
              </div>
            </div>
            <div style="text-align:center;padding:12px 0 0;">
              <div style="font-size:14px;font-weight:600;">{{ theme.name }}</div>
              <el-tag size="mini" :type="currentTheme === theme.value ? 'success' : 'info'" style="margin-top:4px;">
                {{ currentTheme === theme.value ? '✓ 当前主题' : '点击应用' }}
              </el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'ThemeSwitcher',
  data() {
    return {
      currentTheme: localStorage.getItem('theme') || 'light',
      themes: [
        { name: '🌞 亮色模式', value: 'light' },
        { name: '🌙 暗色模式', value: 'dark' }
      ]
    }
  },
  computed: {
    isDark: {
      get() { return this.currentTheme === 'dark' },
      set(val) {
        this.currentTheme = val ? 'dark' : 'light'
        this.applyCurrentTheme()
      }
    }
  },
  created() {
    this.applyCurrentTheme()
  },
  methods: {
    toggleTheme() {
      this.currentTheme = this.isDark ? 'dark' : 'light'
      this.applyCurrentTheme()
      this.$message.success(`已切换至${this.currentTheme === 'dark' ? '暗色' : '亮色'}模式`)
    },
    applyTheme(theme) {
      this.currentTheme = theme.value
      this.isDark = theme.value === 'dark'
      this.applyCurrentTheme()
      this.$message.success(`已应用 ${theme.name}`)
    },
    applyCurrentTheme() {
      localStorage.setItem('theme', this.currentTheme)
      document.body.setAttribute('data-theme', this.currentTheme)
      if (this.currentTheme === 'dark') {
        document.body.classList.add('dark-theme')
      } else {
        document.body.classList.remove('dark-theme')
      }
      // Dispatch event for layout to update
      window.dispatchEvent(new CustomEvent('theme-change', { detail: { theme: this.currentTheme } }))
    }
  }
}
</script>

<style scoped>
.theme-preview-card { cursor: pointer; transition: transform 0.2s; }
.theme-preview-card:hover { transform: translateY(-4px); }
.theme-preview-card.active { border-color: #67C23A !important; }

.preview-content {
  border-radius: 6px;
  overflow: hidden;
  height: 120px;
  position: relative;
}
.preview-light {
  background: #f0f2f5;
}
.preview-light .preview-header {
  height: 20px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
}
.preview-light .preview-sidebar {
  position: absolute;
  left: 0; top: 20px;
  width: 30px; height: 100px;
  background: #304156;
}
.preview-light .preview-body {
  padding: 8px;
}
.preview-light .preview-card-item {
  height: 24px;
  background: #fff;
  border-radius: 4px;
  margin-bottom: 6px;
}

.preview-dark {
  background: #141414;
}
.preview-dark .preview-header {
  height: 20px;
  background: #1f1f1f;
  border-bottom: 1px solid #333;
}
.preview-dark .preview-sidebar {
  position: absolute;
  left: 0; top: 20px;
  width: 30px; height: 100px;
  background: #1d1e2c;
}
.preview-dark .preview-body {
  padding: 8px;
}
.preview-dark .preview-card-item {
  height: 24px;
  background: #1f1f1f;
  border-radius: 4px;
  margin-bottom: 6px;
}
</style>
