<template>
  <div class="app-wrapper">
    <el-container style="height: 100vh;">
      <!-- Sidebar -->
      <el-aside :width="isCollapse ? '64px' : '210px'" style="background: #304156; transition: width 0.3s;">
        <div class="logo">
          <span v-if="!isCollapse">🦜 翠花量化</span>
          <span v-else>🦜</span>
        </div>
        <el-menu
          :default-active="$route.path"
          :collapse="isCollapse"
          :collapse-transition="false"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          router
          unique-opened
        >
          <template v-for="route in $router.options.routes">
            <template v-if="!route.hidden">
              <!-- Single item -->
              <el-menu-item v-if="!route.children || route.children.length <= 1"
                :key="route.path" :index="route.path || route.children[0].path">
                <i :class="route.children ? route.children[0].meta.icon : route.meta.icon"></i>
                <span slot="title">{{ route.children ? route.children[0].meta.title : route.meta.title }}</span>
              </el-menu-item>
              <!-- Group -->
              <el-submenu v-else :key="route.path" :index="route.path">
                <template slot="title">
                  <i :class="route.meta.icon"></i>
                  <span slot="title">{{ route.meta.title }}</span>
                </template>
                <el-menu-item v-for="child in route.children" :key="child.path"
                  :index="route.path + '/' + child.path">
                  <i :class="child.meta.icon" style="margin-right: 4px;"></i>
                  <span slot="title">{{ child.meta.title }}</span>
                </el-menu-item>
              </el-submenu>
            </template>
          </template>
        </el-menu>
      </el-aside>

      <!-- Main -->
      <el-container>
        <!-- Header -->
        <el-header style="background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center;">
            <i :class="isCollapse ? 'el-icon-s-unfold' : 'el-icon-s-fold'"
              @click="$store.dispatch('settings/toggleSideBar')"
              style="font-size: 20px; cursor: pointer; margin-right: 16px;"></i>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">{{ item.title }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div style="display: flex; align-items: center;">
            <el-dropdown @command="handleCommand">
              <span style="cursor: pointer; display: flex; align-items: center;">
                <span style="margin-right: 8px;">{{ userInfo.name || '管理员' }}</span>
                <span style="font-size: 20px;">{{ userInfo.avatar || '🦜' }}</span>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
        </el-header>

        <!-- Content -->
        <el-main style="background: #f0f2f5;">
          <transition name="fade-transform" mode="out-in">
            <router-view />
          </transition>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Layout',
  computed: {
    ...mapState({
      isCollapse: state => !state.settings.sidebar.opened,
      userInfo: state => state.user
    }),
    breadcrumbs() {
      const matched = this.$route.matched.filter(item => item.meta && item.meta.title)
      return matched.map(item => ({ path: item.path, title: item.meta.title }))
    }
  },
  methods: {
    handleCommand(command) {
      if (command === 'logout') {
        this.$confirm('确定退出登录?', '提示', { type: 'warning' })
          .then(() => this.$router.push('/login'))
          .catch(() => {})
      } else if (command === 'profile') {
        this.$router.push('/settings')
      } else if (command === 'settings') {
        this.$router.push('/settings')
      }
    }
  }
}
</script>

<style scoped>
.logo {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #1f2d3d;
}
</style>
