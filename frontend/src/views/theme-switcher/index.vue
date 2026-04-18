<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header"><span>🎨 主题切换</span></div>
      <el-switch v-model="isDark" active-text="暗色模式" inactive-text="亮色模式" @change="toggleTheme" />
    </el-card>
    <el-card>
      <div slot="header"><span>🎯 主题预览</span></div>
      <el-row :gutter="20">
        <el-col :span="8" v-for="theme in themes" :key="theme.name">
          <el-card shadow="hover" :class="theme.class" @click="applyTheme(theme)">
            <div style="text-align:center;padding:20px;">
              <div style="font-size:16px;font-weight:600;margin-bottom:8px;">{{ theme.name }}</div>
              <div style="color:#909399;font-size:12px;">点击应用</div>
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
      isDark: false,
      themes: [
        { name: '默认亮色', class: 'theme-light', value: 'light' },
        { name: '暗色模式', class: 'theme-dark', value: 'dark' },
        { name: '跟随系统', class: 'theme-auto', value: 'auto' }
      ]
    }
  },
  methods: {
    toggleTheme() {
      document.body.classList.toggle('dark-theme', this.isDark)
      localStorage.setItem('theme', this.isDark ? 'dark' : 'light')
      this.$message.success(`已切换至${this.isDark ? '暗色' : '亮色'}模式`)
    },
    applyTheme(theme) {
      document.body.className = theme.class
      localStorage.setItem('theme', theme.value)
      this.$message.success(`已应用${theme.name}`)
    }
  }
}
</script>
