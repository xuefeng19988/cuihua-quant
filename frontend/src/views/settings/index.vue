<template>
  <div class="app-container">
    <!-- 个人信息 -->
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>👤 个人信息</span></div>
      <el-form :model="userForm" label-width="80px" style="max-width: 400px;">
        <el-form-item label="昵称"><el-input v-model="userForm.nickname" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="userForm.email" /></el-form-item>
        <el-form-item label="头像"><el-input v-model="userForm.avatar" placeholder="emoji 如 🦜" /></el-form-item>
        <el-form-item><el-button type="primary" @click="saveProfile">💾 保存</el-button></el-form-item>
      </el-form>
    </el-card>

    <!-- 主题设置 -->
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>🎨 主题设置</span></div>
      <el-radio-group v-model="theme">
        <el-radio label="dark">🌙 深色模式</el-radio>
        <el-radio label="openclaw">🐾 OpenClaw 风格</el-radio>
        <el-radio label="light">☀️ 浅色模式</el-radio>
      </el-radio-group>
    </el-card>

    <!-- 修改密码 -->
    <el-card>
      <div slot="header"><span>🔒 修改密码</span></div>
      <el-form :model="pwdForm" label-width="100px" style="max-width: 400px;">
        <el-form-item label="原密码"><el-input v-model="pwdForm.old" type="password" /></el-form-item>
        <el-form-item label="新密码"><el-input v-model="pwdForm.new" type="password" /></el-form-item>
        <el-form-item label="确认密码"><el-input v-model="pwdForm.confirm" type="password" /></el-form-item>
        <el-form-item><el-button type="primary" @click="changePassword">🔑 修改密码</el-button></el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Settings',
  data() {
    return {
      theme: 'dark',
      userForm: { nickname: '管理员', email: 'admin@cuihua.quant', avatar: '🦜' },
      pwdForm: { old: '', new: '', confirm: '' }
    }
  },
  methods: {
    saveProfile() { this.$message.success('个人信息已保存') },
    changePassword() {
      if (this.pwdForm.new !== this.pwdForm.confirm) return this.$message.error('两次密码不一致')
      if (this.pwdForm.new.length < 6) return this.$message.error('密码长度不能少于6位')
      this.$message.success('密码已修改')
      this.pwdForm = { old: '', new: '', confirm: '' }
    }
  }
}
</script>
