<template>
  <div class="register-container">
    <div class="register-card">
      <div class="title-container">
        <h3 class="title">🦜 翠花量化</h3>
        <p class="subtitle">欢迎注册 - CUIHUA QUANT</p>
      </div>

      <el-alert v-if="!hasUsers" type="info" :closable="false" style="margin-bottom: 16px;">
        <template slot="title">首次使用，请注册管理员账号</template>
      </el-alert>

      <el-form ref="registerForm" :model="form" :rules="rules" class="register-form">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="el-icon-user" />
        </el-form-item>

        <el-form-item prop="nickname">
          <el-input v-model="form.nickname" placeholder="昵称（可选）" prefix-icon="el-icon-chat-dot-round" />
        </el-form-item>

        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱（可选）" prefix-icon="el-icon-message" />
        </el-form-item>

        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码（至少6位）" prefix-icon="el-icon-lock" show-password />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" prefix-icon="el-icon-lock" show-password
            @keyup.enter.native="handleRegister" />
        </el-form-item>

        <el-button :loading="loading" type="primary" style="width: 100%; margin-bottom: 16px;"
          @click.native.prevent="handleRegister">
          注 册
        </el-button>

        <div style="text-align: center;">
          <el-link type="primary" @click="$router.push('/login')">已有账号？去登录</el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      hasUsers: false,
      loading: false,
      form: { username: '', nickname: '', email: '', password: '', confirmPassword: '' },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 2, max: 20, message: '长度 2-20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码至少6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: this.validateConfirm, trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    this.checkInit()
  },
  methods: {
    validateConfirm(rule, value, callback) {
      if (value !== this.form.password) {
        callback(new Error('两次密码不一致'))
      } else {
        callback()
      }
    },
    checkInit() {
      fetch('/api/auth/check-init')
        .then(r => r.json())
        .then(d => {
          this.hasUsers = d.has_users
          if (d.has_users) {
            this.$router.push('/login')
          }
        })
    },
    handleRegister() {
      this.$refs.registerForm.validate(valid => {
        if (!valid) return
        this.loading = true
        fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.form.username,
            nickname: this.form.nickname,
            email: this.form.email,
            password: this.form.password
          })
        })
        .then(r => r.json())
        .then(d => {
          this.loading = false
          if (d.code === 200) {
            localStorage.setItem('token', d.token)
            this.$message.success('注册成功！')
            this.$router.push('/')
          } else {
            this.$message.error(d.message || '注册失败')
          }
        })
        .catch(() => {
          this.loading = false
          this.$message.error('网络错误')
        })
      })
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.register-card {
  width: 400px;
  padding: 40px 35px 15px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}
.title-container { text-align: center; margin-bottom: 24px; }
.title { font-size: 24px; font-weight: 600; color: #303133; margin: 0; }
.subtitle { font-size: 12px; color: #909399; margin: 8px 0 0; letter-spacing: 2px; }
.register-form { padding: 0 10px; }
</style>
