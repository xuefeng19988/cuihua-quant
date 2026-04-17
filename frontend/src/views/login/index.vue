<template>
  <div class="login-container">
    <div class="login-form">
      <div class="title-container">
        <h3 class="title">🦜 翠花量化</h3>
        <p class="subtitle">CUIHUA QUANT SYSTEM</p>
      </div>

      <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名" prefix-icon="el-icon-user" />
        </el-form-item>

        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="el-icon-lock"
            @keyup.enter.native="handleLogin" show-password />
        </el-form-item>

        <el-checkbox v-model="loginForm.remember" style="margin-bottom: 16px;">记住我，30天免登录</el-checkbox>

        <el-button :loading="loading" type="primary" style="width: 100%; margin-bottom: 16px;"
          @click.native.prevent="handleLogin">
          登 录
        </el-button>

        <div style="text-align: center;">
          <el-link type="primary" @click="$router.push('/register')">没有账号？去注册</el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      loginForm: { username: '', password: '', remember: false },
      loginRules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
      },
      loading: false
    }
  },
  created() {
    this.checkInit()
  },
  methods: {
    checkInit() {
      fetch('/api/auth/check-init')
        .then(r => r.json())
        .then(d => {
          if (!d.has_users) {
            this.$router.push('/register')
          }
        })
    },
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (!valid) return
        this.loading = true
        fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.loginForm.username,
            password: this.loginForm.password,
            remember_me: this.loginForm.remember
          })
        })
        .then(res => res.json())
        .then(data => {
          this.loading = false
          if (data.code === 200) {
            localStorage.setItem('token', data.token || 'authenticated')
            this.$router.push('/')
          } else {
            this.$message.error(data.message || '登录失败')
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
.login-container {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-form {
  width: 380px;
  padding: 40px 35px 15px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}
.title-container { text-align: center; margin-bottom: 30px; }
.title { font-size: 24px; font-weight: 600; color: #303133; margin: 0; }
.subtitle { font-size: 12px; color: #909399; margin: 8px 0 0; letter-spacing: 2px; }
</style>
