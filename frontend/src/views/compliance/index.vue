<template>
  <div class="app-container">
    <el-card>
      <div slot="header"><span>{{ title }}</span></div>
      <el-empty description="页面开发中..." />
    </el-card>
  </div>
</template>
<script>
export default {
  name: '{{ name }}',
  computed: {
    title() {
      return this.$route.meta.title || '页面'
    }
  }
}
</script>
