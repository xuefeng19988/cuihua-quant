<template>
  <div class="app-wrapper">
    <el-container style="height: 100vh;">
      <!-- Sidebar -->
      <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar-container" :class="{ collapse: isCollapse }">
        <div class="logo" @click="$router.push('/')">
          <img src="/favicon.ico" class="logo-icon" onerror="this.style.display='none'" />
          <span v-if="!isCollapse" class="logo-title">🦜 翠花量化</span>
          <span v-else class="logo-icon-text">🦜</span>
        </div>

        <el-scrollbar wrap-class="scrollbar-wrapper">
          <el-menu
            :default-active="activeMenu"
            :collapse="isCollapse"
            :collapse-transition="false"
            :unique-opened="true"
            background-color="#304156"
            text-color="#bfcbd9"
            active-text-color="#409EFF"
            router
          >
            <sidebar-item v-for="route in sidebarRoutes" :key="route.path" :item="route" :base-path="route.path" />
          </el-menu>
        </el-scrollbar>
      </el-aside>

      <!-- Main Container -->
      <el-container>
        <!-- Header -->
        <el-header class="header-container">
          <div class="header-left">
            <div class="hamburger" @click="$store.dispatch('settings/toggleSideBar')">
              <i :class="isCollapse ? 'el-icon-s-unfold' : 'el-icon-s-fold'"></i>
            </div>
            <el-breadcrumb separator="/" class="breadcrumb">
              <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">{{ item.title }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand" trigger="click">
              <div class="user-info">
                <span class="user-name">{{ userInfo.name || '管理员' }}</span>
                <span class="user-avatar">{{ userInfo.avatar || '🦜' }}</span>
                <i class="el-icon-arrow-down el-icon--right"></i>
              </div>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="profile">👤 个人信息</el-dropdown-item>
                <el-dropdown-item command="settings">⚙️ 系统设置</el-dropdown-item>
                <el-dropdown-item command="theme">🎨 主题切换</el-dropdown-item>
                <el-dropdown-item command="logout" divided>🚪 退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
        </el-header>

        <!-- Content -->
        <el-main class="main-container">
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
import SidebarItem from './components/SidebarItem'

export default {
  name: 'Layout',
  components: { SidebarItem },
  computed: {
    ...mapState({
      isCollapse: state => !state.settings.sidebar.opened,
      userInfo: state => state.user
    }),
    activeMenu() {
      const { meta, path } = this.$route
      if (meta.activeMenu) return meta.activeMenu
      return path
    },
    sidebarRoutes() {
      return this.$router.options.routes.filter(r => !r.hidden)
    },
    breadcrumbs() {
      return this.$route.matched.filter(item => item.meta && item.meta.title).map(item => ({ path: item.path, title: item.meta.title }))
    }
  },
  methods: {
    handleCommand(command) {
      const map = { profile: '/settings', settings: '/settings', theme: '/theme-switcher' }
      if (command === 'logout') {
        this.$confirm('确定退出登录?', '提示', { type: 'warning' })
          .then(() => this.$router.push('/login'))
          .catch(() => {})
      } else if (map[command]) {
        this.$router.push(map[command])
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.app-wrapper { width: 100%; height: 100%; }

.sidebar-container {
  background: #304156;
  transition: width 0.3s;
  overflow: hidden;
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);

  &.collapse { width: 64px !important; }

  .logo {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background: #2b2f3a;
    border-bottom: 1px solid #1f2d3d;

    .logo-icon { width: 32px; height: 32px; margin-right: 8px; }
    .logo-title { color: #fff; font-size: 16px; font-weight: 600; white-space: nowrap; }
    .logo-icon-text { font-size: 24px; }
  }

  .el-scrollbar {
    height: calc(100vh - 50px);
  }

  ::v-deep .el-scrollbar__wrap {
    overflow-x: hidden;
  }

  ::v-deep .el-menu { border-right: none; }
  ::v-deep .el-submenu__title:hover, ::v-deep .el-menu-item:hover { background-color: #263445 !important; }
  ::v-deep .el-menu-item.is-active { background-color: #409EFF !important; color: #fff !important; }
}

.header-container {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);

  .header-left { display: flex; align-items: center; flex: 1; }
  .hamburger { font-size: 20px; cursor: pointer; padding: 0 12px; transition: color 0.3s; &:hover { color: #409EFF; } }
  .breadcrumb { margin-left: 8px; }

  .header-right .user-info { display: flex; align-items: center; cursor: pointer; padding: 0 8px; }
  .user-name { margin-right: 8px; color: #606266; }
  .user-avatar { font-size: 20px; }
}

.main-container { background: #f0f2f5; overflow-y: auto; }
</style>
